from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run
import httplib2
from apiclient.discovery import build

def md5sum(s, string=True):
    import md5
    m = md5.new()
    m.update(s)
    ret = m.digest()

    if string:
        #import hashlib
        ret = m.hexdigest()

    return ret

def D():
    import pdb
    pdb.set_trace()

def J(obj):
    import json
    return json.dumps(obj, sort_keys=True, indent=4)

def s2ts(s):
    from calendar import timegm
    from feedparser import _parse_date as parse_date
    return int(timegm(parse_date(s)))

def file_put_contents(filename, data, mode='w'):
    f = open(filename, mode)
    f.write(data)
    f.close()

#Threshold for eventual consistency
EVENTUAL_CONSISTENCY_TIMEOUT = 300

def basetime(seconds=EVENTUAL_CONSISTENCY_TIMEOUT):
    from datetime import timedelta
    return int(now() - timedelta(seconds=seconds).total_seconds())

def now():
    import time
    return time.time()

FLOW = flow_from_clientsecrets('client_secrets.json',
                               scope='https://www.googleapis.com/auth/drive')

storage = Storage('credentials.dat')
credentials = storage.get()

if credentials is None or credentials.invalid:
    credentials = run(FLOW, storage)

http = httplib2.Http()
http = credentials.authorize(http)

service = build('drive', 'v2', http=http)

files = service.files().list().execute()

#Iterate over files, compare the export links from files.list() 
#and revisions.get()
for i in files["items"]:
    rev = { "modifiedDate" :  None }
    try:
        rev = service.revisions().get(fileId=i['id'],
                                        revisionId="head").execute()
    except Exception:
        #print "id=%.60s [SKIPPED]" % i['id']
        continue


    #Let's ignore files which might not be consistent yet
    if (s2ts(i["modifiedDate"]) > basetime()):
        continue

    #Some files don't have exportlinks. Skip them.
    if i.get('exportLinks') is None:
        continue

    export_map = {
        "application/vnd.google-apps.document" : "text/plain",
        "application/vnd.google-apps.presentation" : "text/plain",
        "application/vnd.google-apps.spreadsheet" :
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }

    ext_map = {
        "application/vnd.google-apps.document" : "txt",
        "application/vnd.google-apps.presentation" : "txt",
        "application/vnd.google-apps.spreadsheet" : "xls"
    }

    export_type = export_map.get(i["mimeType"])
    left = i['exportLinks'].get(export_type)
    right = rev['exportLinks'].get(export_type)


    #The checks below demonstrate two issues:
    #A) That the timestamps of revisions.list are not correct
    #status = (i["modifiedDate"] == rev['modifiedDate'])
    delta = (s2ts(i["modifiedDate"]) - s2ts(rev['modifiedDate']))
    status = (abs(delta) > EVENTUAL_CONSISTENCY_TIMEOUT)

    if status:
        print ("Timestamp error for %s. files.list=%s, revisions.list=%s delta=%s" %
                (i['id'], i["modifiedDate"], rev['modifiedDate'], delta)) 

    #B) In some cases, the content of the head revision don't match
    #   What you get from files.list
    if (left):
        assert(right)
        resp, content1 = http.request(left)
        resp, content2 = http.request(right)

        if (content1 != content2):
            print "Content error for %s get=%s revisions=%s" % (i['id'], 
                                                        md5sum(content1),
                                                        md5sum(content2))


            lname = "files_list_%s.%s" %  (i['id'], ext_map[i['mimeType']])
            rname = "revisions_list_%s.%s" % (i['id'], ext_map[i['mimeType']])

            print "Saving files as %s and %s" % (lname, rname)
            file_put_contents(lname, content1)
            file_put_contents(rname, content2)

        #If you comment out this assert, some files will hit it.
        #assert(content1 == content2)
