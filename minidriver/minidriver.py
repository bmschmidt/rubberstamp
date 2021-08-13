from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient import http
import datetime
import yaml
import re
from pathlib import Path
from typing import Union, List
import csv
from openpyxl import load_workbook
import pypandoc
import importlib
import logging

"""

Minnie Driver provides general methods for syncing directories from Google
Drive. Project specific methods (e.g., rubberstamp for Wax)
should be somewhere else.

"""

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.readonly']

#prefs = yaml.safe_load(open("rubberstamp.yaml"))

def create_service():
    """From the basic usage of the Drive v3 API.
    Generates authorizations if they don't exist in a popup.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json'
                , SCOPES)
            creds = flow.run_local_server(port=9797)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service


def get_files(drive_id, service, recursively = True):
    files = service.files().list(q=f"'{drive_id}' in parents",
                                      spaces='drive',
                                      pageSize=50,
                                      fields="nextPageToken, files(kind,mimeType, id, name, modifiedTime)").execute()
    for file in files['files']:
        #### WHY ALEX AND MARII WHY???
        file['path'] = Path(file['name'])
        if file['mimeType'].endswith("apps.folder") and recursively:
            for subfile in get_files(file['id'], service):
                subfile['path'] = file['path'] / subfile['path']
                yield subfile
        else:
            if not "google" in file['mimeType']:
                # Can't handle google docs.                
                yield file

def local_is_outdated(file:dict, local_path:Path):
    assert file['modifiedTime'].endswith("Z") #i.e., make sure Google still returns times as UTC
    if not local_path.exists():
        return True
    remote_modified_time = datetime.datetime.fromisoformat(file['modifiedTime'][:-1])
    if not remote_modified_time.timestamp() < local_path.stat().st_mtime:
        return True
    return False

def flatten_wax_image_dir(drive_id: str, local_dir, service):
    """
    Find all images in the given dir, and download them.
    Some guesswork to allow nested google drive folders.
    """
    files = get_files(drive_id, service, recursively = True)
    num_yielded = 0
    for file in files:
        num_yielded += 1
        if file['mimeType'] == 'image/jpeg':
          path = file['path']
          raw_name = path.with_suffix("").name
          # If it's just two digits, assume it's a subelement in 
          # something else.
          if re.search(r"^[0-9]{1,2}$", raw_name):
            dest = local_dir / path.parent.name / path.name
          else:
            dest = local_dir / path.name
          if local_is_outdated(file, dest):
            download_file(file['id'], dest, service)
    if num_yielded == 0:
        logging.warning(f"No files found for google drive ID {drive_id}: "
        "this can occur if the Google user for your credentials "
        "is not allowed to access it.")

def sync_directory(drive_id, local_dir, service):
    print(f"Syncing directory {drive_id} to {local_dir}")
    for file in get_files(drive_id, service, recursively = True):
        path = local_dir / file['path']
        path.parent.mkdir(exist_ok = True, parents = True)
        # ".DS_Store on mac directories."
        if path.name.startswith("."):
            continue
        if local_is_outdated(file, path):
            print("Fetching", file)
            path.parent.mkdir(exist_ok = True, parents = True)
            download_file(file['id'], path, service)
            download_file(file['id'], path, service)

def download_file(file_id: str, destination: Path, service):
    # From the google drives docs, lightly edited.
    # Only for images--docs and sheets require a different treatment.
    print(f"Downloading {file_id} to {destination}")
    destination.parent.mkdir(exist_ok = True, parents = True)
    request = service.files().get_media(fileId=file_id)
    fh = destination.open(mode = "wb")
    downloader = http.MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

def sync_doc_or_sheet(file: Union[str, dict], destination: Path, service):
    """
    file: either a google drive ID, or a dict as returned from service.files().get.
    """
    if destination.suffix == ".docx":
        mimeType ='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif destination.suffix == ".xlsx":
        mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        raise NotImplementedError("You can only export to docx or xlsx. "
        "Don't worry, no Microsoft products will be used in the parsing"
        " of your file.")
    if type(file) == str:
        file = service.files().get(fileId=file, fields="kind, id, name, modifiedTime, owners").execute()
    file_id = file['id']

    if local_is_outdated(file, destination):
        print(f"Downloading {file['name']} to {destination}.")
        request = service.files().export_media(fileId=file_id,
                         mimeType=mimeType)
        fh = destination.open("wb")
        downloader = http.MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))

def xlsx_to_csv(source: Path, dest: Path, sheet = None):
    assert dest.suffix == ".csv"
    assert source.suffix == ".xlsx"
    if not dest.exists() or source.stat().st_mtime > dest.stat().st_mtime:
        wb = load_workbook(source)
        if sheet is not None:
            sh = wb[sheet]
        else:
            sh = wb.active
        with open(dest, 'w', newline="") as f:
            c = csv.writer(f)
            for r in sh.rows:
                vals = [cell.value for cell in r]
                #XXXXX REALLY BAD BUT NECESSARY BECAUSE WAX IS WEIRD ABOUT LOWERCASE!!!!
                if vals[0] is None:
                    logging.error(f"No PID for {vals}")
                    continue
                vals[0] = vals[0].lower()
                # Empty csv rows screw up things.
                if len([v for v in vals if v is not None and v != ""]):
                    c.writerow(vals)

def docx_to_md(source: Path, dest: Path, metadata:dict):
    # Metadata is a dict. All pairs will be turned into
    # Yaml metadata that lives in the Markdown
    assert dest.suffix == ".md"
    assert source.suffix == ".docx"
    if dest.exists() and not source.stat().st_mtime > dest.stat().st_mtime:
        return
    print(f"Running pandoc for {source} -> {dest}")
    args = ['--standalone']
    for k, v in metadata.items():
        args.append(f'--metadata={k}:{v}')
    print("Dangerous media extraction.")
    args.append(f"--extract-media=./img")
    from pathlib import Path
    with importlib.resources.path("minidriver", "lib") as f:
        string = str(f / "filter.lua")
        args.append(f'--lua-filter')
        args.append(string)
    output = pypandoc.convert_file(str(source), 'md', extra_args=args)
    with dest.open("w") as fout:
        fout.write(output)
