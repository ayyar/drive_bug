from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run
import httplib2
from apiclient.discovery import build

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

for i in files["items"]:
    rev = { "modifiedDate" :  None }
    try:
        rev = service.revisions().get(fileId=i['id'],
                                        revisionId="head").execute()
    except Exception:
        #print "id=%.60s [SKIPPED]" % i['id']
        continue

    #status = (i["modifiedDate"] == rev['modifiedDate'])
    delta = (s2ts(i["modifiedDate"]) - s2ts(rev['modifiedDate']))
    status = (abs(delta) > 300)
    if status is False:
        continue

    print "id=%.60s mime=%s mtime=%s rev=%r ERROR=[%r] delta=%s" % (i['id'],
                                                         i["mimeType"],
                                                         i["modifiedDate"],
                                                         rev['modifiedDate'],
                                                         status, delta)

