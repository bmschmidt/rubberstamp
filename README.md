# Rubberstamp

This is a recipe for continuously updating a wax site from Google drive.
The point is to allow multiple people to collaborate on a project simultaneously,
and for the webpage to be continuously updated.

It's called 'rubberstamp' because

1. It just robotically approves any changes that any user makes to the repo, and
2. You *could* use a rubber stamp to make a wax seal, but it wouldn't work
   especially well.

The python components are called `minidriver.py` because they're a more
general set of interfaces to Google Drive that should be useful if
you want to build minimal computing projects with people who use Google Docs,
not markdown. Sometimes you gotta meet people where they are.

## Steps

1. Create files in Google Drive, including potentially
   1. CSVs of collections.
   2. Folders of images.
   3. Exhibits as doc files.

2. Create an OAuth client ID. This requires configuring a project for your Google Drive.
   You can't read from Google docs without this. I find this to be the hardest part,
   because it takes you into the part of the Google settings where I always
   worry I might accidentally set up a server.

   ![Photo of Google Docs page](docs/credentials.png)



3. Edit the base _config.yml to include information about where to find the
   associated documents on Google Drives.

   This looks the same as a basic Wax/Jekyll configuration, except that you
   can place a key called `google_drive_id` inside any field. If so, rather
   using local markdown/images/csvs to generate the wax site, instead the
   relevant files will be retrieved from Google Drive. To avoid filename confusion,
   you have to use the Google Drive ID, which creates inscrutable file names.
   But it's not so hard to find (it's just the bit at the end of any URL in
   Google.) The precise strategy will differ by file type; for images, an
   entire folder with subfolders on Drive will be fetched. For exhibits,
   you should specify a drive folder with *documents* in it, which will be
   converted from Google Docs to Markdown through Pandoc. For metadata,
   give the path to a Google Sheet; you may optionally put a slash at the end,
   (e.g.: '1gbPtPQtHpOClQXJ8CjMGGj4B6kTN_UkpX6XrCCCD278/Elijah') in which case
   the tab with that name will be fetched.

  ```
     collections:
       exhibits:
         output: true
         # Every google doc in this drive will be converted to Markdown and become
         # an exhibit.
         google_drive_id: 1En1kFsl6dlW4hRhf1OpBgTIpjgLC5SZI
       Rhee: # name of collection
         output: true # makes sure pages are output as html files
         layout: 'generic_collection_item' # the layout for the pages to use
         metadata:
           source: 'A13053834.csv' # path to the metadata file within `_data`
           google_drive_id: '1gbPtPQtHpOClQXJ8CjMGGj4B6kTN_UkpX6XrCCCD278/Elijah'
         images:
           source: 'raw_images/Rhee' # path to the directory of images within `_data`--w
           # A google drive *folder*; all files in this, including subdirectories,
           # will be synced to the drive above based on modification times.
           google_drive_id: '1RofzC0sDYoUeiSu4DOveDEAQTakaG12D'
       A002475884: # name of collection
         output: true # makes sure pages are output as html files
         layout: 'generic_collection_item' # the layout for the pages to use
         metadata:
           source: 'A002475884.csv' # path to the metadata file within `_data`
           google_drive_id: '1gbPtPQtHpOClQXJ8CjMGGj4B6kTN_UkpX6XrCCCD278/Eunbin'
         images:
           source: 'raw_images/A002475884' # path to the directory of images within `_data`
           google_drive_id: '1VnhmXM15cyNX3TSBjj6oFpYan0aGYlBV'
  ```

### Inline images

There's gonna be some way to include inline images.

### Dependencies

This runs in Python, probably 3.8 or later. You also need the packages
`pypandoc` and `openpyxl` (for parsing documents and spreadsheets,
respectively), as well as some Google API tools.

```
pip install pypandoc openpyxl
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

# SeMinnieTiC versioning

Semantic versioning is a well-regarded strategy for controlling releases. The
basic idea of semantic versioning is that you always keep the version number
below 1 because anything higher involves a strong contract with your users that,
let's be honest, you're not going to follow through on.

This project (like all minidriver projects) uses
a related but improved strategy known as SeMinnieTiC versioning. In SeminnieTec
versioning, every commit message must end with the phrase "How do you like them
apples?" (or at least the last three words). More significant changes should
be indicated by increasing the stress on "them"; e.g., a new feature addition should be
"`How do you like *them* apples?`," major additions to the API
should be "`How do you like **them** apples?`", and anything that breaks
backwards compatibility must be indicated with the commit
"`How do you like ***them*** apples?`" so that users are aware of the change.

In order to get the semantic versioning number, you just cat out the git log and
work out the number of changes in each class to get a number like "4.3.2".
If users want
guarantees about API stability, they have to do this themselves.
You can also refer to major versions by lining them up against
[Minnie Driver's Wikipedia filmography](https://en.wikipedia.org/wiki/Minnie_Driver#Film).
Version 0 is "The Zebra Man", Version 1 is "That Sunday," etc.

The C at the end of SeMinnieTiC is pronounced the opposite of the X in LaTeX.


# Code of Conduct

See the above section. Follow the Wax project code of conduct.
