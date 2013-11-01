drive_bug
=========

Unit test case for reproducing drive bug described here:

http://stackoverflow.com/questions/18177759/serious-bug-the-last-revision-of-drive-revisions-list-doesnt-return-actual-dat


Setup:

1. Install dependency libraries

```
  mkdir <test_directory>
  virtualenv .
  source ./bin/activate
  pip install -r requirements.txt
```

2. Enable Drive in project in the Google API console and download client_secrets.json.

3. Add http://localhost:8080/ to the allowed API redirect URLs in the API console

Running the script:

Run the script as

```
  python drive_bug.py
```

The script will product the following output:

Timestamp errors, where timestamps of revisions differ greatly from that of files.list ( this is a secondary error ) :
```
Timestamp error for <fileid> files.list=2013-10-31T19:22:59.835Z, revisions.list=2013-10-31T19:17:32.141Z delta=327
```

Content errors, where sometimes revisions.list returns links to content with bad data. This is the primary error.

The script will output md5 sums of content obtained through the two different methods, and
here sometimes the content obtained through revisions differs.

```
Content error for <fileid> get=9fcad645e2cbf9906d493bf0eba754dc revisions=0948a876dafffcc17ed9b4395d3843a0
Saving files as files_list_<fileid>.xls and revisions_list_<fileid>.xls
```
