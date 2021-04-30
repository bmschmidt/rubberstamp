from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient import http
import datetime
import yaml
from pathlib import Path




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
                                      pageSize=100, fields="nextPageToken, files(kind,mimeType, id, name, modifiedTime)").execute()
    returnval = []
    for file in files['files']:
        file['path'] = Path(file['name'])
        if file['mimeType'].endswith("apps.folder") and recursively:
            for subfile in get_files(file['id'], service):
                subfile['path'] = file['path'] / subfile['path']
                returnval.append(subfile)
        else:
            returnval.append(file)
    return returnval

def sync(drive_id, local_dir, service):
    for file in get_files_recursively(drive_id, service):
        path = local_dir / file['path']
        path.parent.mkdir(exist_ok = True, parents = True)
        # ".DS_Store on mac directories."
        if path.name.startswith("."):
            continue
        print(file)
        assert file['modifiedTime'].endswith("Z") #i.e., make sure Google still returns times as UTC
        if not path.exists() or not datetime.datetime.fromisoformat(file['modifiedTime'][:-1]).timestamp() < path.stat().st_mtime:
            download_file(file['id'], path, service)

def download_file(file_id: str, destination: Path, service):
    # From the google drives docs, lightly edited.

    # Only for images--docs and sheets require a different treatment.
    request = service.files().get_media(fileId=file_id)
    fh = destination.open("wb")
    downloader = http.MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))


def call_api(service):
    # Call the Drive v3 API
    results = service.files().list(
        pageSize=20, fields="nextPageToken, files(id, name, modifiedTime, parents)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        now = datetime.datetime.now()
        for item in items:
            print(item)
            continue
            modTime = datetime.datetime.strptime(item["modifiedTime"][:16],  "%Y-%m-%dT%H:%M")

            if "Week" in item['name']:
                if item['id'] in modtimes and modtimes[item['id']] >= modTime:
                    print("ignoring {} from {}".format(item['name'], item['modifiedTime']))
                    # ignore old files.
                    continue
                if True:
                    file_id = item['id']
                    request = service.files().export_media(fileId=file_id,
                                             mimeType='application/msword')
                    downloader = http.MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print("Download %d%%." % int(status.progress() * 100))
                    modtimes[item['id']] = modTime
                print(u'Downloaded {0} ({1})'.format(item['name'], item['id']))

if __name__ == '__main__':
    main()
    modtimes.close()
