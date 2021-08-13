from minidriver import *
import yaml
from pathlib import Path
import datetime
import sys
import time

def rubberstamp():
    args = sys.argv
    if (len(args) == 1):
        print("You must specificy a directory; e.g., 'rubberstamp .'")
    elif (len(args) == 2):
        print("Copying once. To copy continuously, give a time interval"
              " after the directory; e.g., rubberstamp . 30")
        stamp(args[1])
    else:
        while True:
            stamp(args[1])
            time.sleep(int(args[2]))
    # Parses a Jekyll YAML file for needed Wax blocks.

def stamp(root):
    root = Path(root)
    if not (root / "credentials.json").exists():
        raise FileNotFoundError("You must have a file in the directory "
        "called 'credentials.json' exported from the Google Drive API.")
    data = yaml.safe_load((root / "_config.yml").open())
    service = create_service()

    for menu_item in data['menu']:
        # This feels rickety. Other than calling something an exhibit, how do you indicate
        # the existence of a page?
        if menu_item['label'] == 'Exhibits':
            for sub in menu_item['sub']:
                assert sub['link'].endswith("/") # gotta be a folder going to something.
                dest = Path(root, sub['link'].replace("/exhibits", "_exhibits").rstrip("/"))
                dest_md = dest.with_suffix(".md")
                dest_docx = dest.with_suffix(".docx")
                if "google_drive_id" in sub:
                    id = sub['google_drive_id']
                    desc = service.files().get(fileId=id, fields="kind, id, name, modifiedTime, owners").execute()
                    minidriver.sync_doc_or_sheet(desc, dest_docx, service)
                    meta = {"author": desc['owners'][0]['displayName'],
                           "layout": "exhibit",
                            "permalink": sub['link']
                           }
                    minidriver.docx_to_md(source = dest_docx, dest = dest_md, metadata = meta)

    for name, description in data['collections'].items():
        if name == 'exhibits':
            continue
        if 'metadata' in description:
            m = description['metadata']
            if 'google_drive_id' in m:
                if "/" in m['google_drive_id']:
                    id, sheet = m['google_drive_id'].split("/")
                else:
                    id = m['google_drive_id']
                    sheet = None # Uses the first sheet.
                desc = service.files().get(fileId=id, fields="kind, id, name, modifiedTime, owners").execute()
                dest = Path(root, "_data", desc['name']).with_suffix(".xlsx")
                csv = Path(root, "_data", m['source'])
                minidriver.sync_doc_or_sheet(desc, dest, service)
                minidriver.xlsx_to_csv(source = dest, dest = csv, sheet = sheet)
        if 'images' in description:
            imgs = description['images']
            if 'google_drive_id' in imgs:
                if not 'source' in imgs:
                    raise KeyError("You must include a wax source as well as a google_drive_id for collection", name)
                dest = Path(root, "_data", imgs['source'])
                minidriver.flatten_wax_image_dir(imgs['google_drive_id'], service)
            if 'google_drive_ids' in imgs:
                for id in imgs['google_drive_ids']:
                    if not 'source' in imgs:
                        raise KeyError("You must include a wax source as well as a google_drive_id for collection", name)
                    dest = Path(root, "_data", imgs['source'])
                    minidriver.flatten_wax_image_dir(id, dest, service)

