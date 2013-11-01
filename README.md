drive_bug
=========

Test case for reproducing drive bug

Setup:

1. Install dependency libraries

mkdir <test_directory>
virtualenv .
source ./bin/activate
pip install -r requirements.txt

2. Enable Drive in project in the Google API console and download client_secrets.json.

3. Add  http://localhost:8080/ to the allowed API redirect URLs



Running the script:

Run the script as "python drive_bug.py"

The script compares timestamps of files.list() with drive.revisions.get(revisionId="head")

After running the script, you will get output listing where the timestamp in the
revisions api lags by by > 300 seconds.


...
id=<fileid> mime=application/vnd.google-apps.document mtime=2013-10-29T12:20:03.138Z
rev=u'2013-10-27T18:15:25.228Z' ERROR=[True] delta=151478
...



4. Seeing what is wrong with the file.

From the output files, it is easiest to see problems with documents. Copy the fileid of the file.


Go to the API explorer and download the file from drive.files.get and drive.revisions.get - use the text/plain export link.

https://developers.google.com/apis-explorer/#p/drive/v2/drive.files.get

https://developers.google.com/apis-explorer/#p/drive/v2/drive.revisions.get

This will show you differences.
