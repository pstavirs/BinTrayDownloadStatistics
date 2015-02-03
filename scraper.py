import json
import lxml.html
import re
import requests
import scraperwiki
from datetime import date as Date

downloads = {}

#scraperwiki.sqlite.execute("delete from downloads where Date > '2015-01-18'")

last_date = scraperwiki.sqlite.select("max(Date) from downloads where Date < '" + Date.today().isoformat() + "'")[0]['max(Date)']
print "Last date in DB: "+last_date

for package in ['ostinato-bin-win32', 'ostinato-bin-osx-universal', 'ostinato-src']:
    page = requests.get('https://bintray.com/package/statistics/pstavirs/ostinato/'+package) 
    doc = lxml.html.document_fromstring(page.text)

    # get the javascript snippet containing the downloads data
    script = doc.xpath("//div[@id='show-pkg']/script[2]")[0]
    #print script.text

    # extract just the downloads data from the javascript
    m = re.search('series:(.*),\s+legend', script.text, re.DOTALL)

    # massage the javascript object to make it valid json
    n = re.sub('Date.UTC\((\d+), (\d+)-1, (\d+)\)', '"\g<1>-\g<2>-\g<3>"', m.group(1))
    n = re.sub('name|data', '"\g<0>"', n);
    #print n

    # parse the json
    j = json.loads(n)
    #print json.dumps(j[0])

    # json schema -
    # [{name : <version>, data : [[<date>, <count>], ...]}]
    # data ordered from older to newer dates
    version = j[0]['name']
    data = j[0]['data']

    # since today is not yet over, remove today's count
    data.pop()

    #print version
    #print data

    name = package+'-'+version
    for tuple in data:
        # tuple = [<date>, <count>]
        # skip tuples that we've already stored in the db
        if (tuple[0] <= last_date):
            continue
        date = tuple[0]
        count = tuple[1]
        #print date, name, count
        if (not downloads.has_key(date)):
            downloads[date] = {}
        downloads[date][name] = count

# downloads is a dict with schema -
#       { date: {name: count, name: count, ...}, ...}
# we need to convert it into a list of dicts with schema -
#       [ {Date: date, name: count, name: count, ...}, ...]
#print downloads
keys = downloads.keys()
# sort in increasing order of dates
keys.sort()
records = []
for d in keys:
    x = downloads[d]
    x['Date'] = d
    records.append(x)
print records
if len(records):
    scraperwiki.sqlite.save(unique_keys=['Date'], data=records, table_name='downloads')

