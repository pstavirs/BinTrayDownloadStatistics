import json
import requests
import scraperwiki
from datetime import date as Date, datetime

downloads = {}

#scraperwiki.sqlite.execute("delete from downloads where Date > '2015-03-29'")

last_date = scraperwiki.sqlite.select("max(Date) from downloads where Date < '" + Date.today().isoformat() + "'")[0]['max(Date)']
print "Last date in DB: "+last_date

for package in ['ostinato-bin-win32', 'ostinato-bin-osx-universal', 'ostinato-src']:
    # retrieve the statistics json data
    page = requests.get('https://bintray.com/statistics/packageStatistics?pkgPath=/ostinato/ostinato/'+package)
    #print page.text

    # parse the json
    j = json.loads(page.text)
    #print json.dumps(j)

    # json schema -
    # { ..., data:[{version:<version>, series:[[<timestamp>, <count>], ...]}]
    # series timestamps ordered from older to newer dates; timestamps in msec
    for version_data in j['data']:
        version = version_data['version']
        data = version_data['series']

        # since today is not yet over, remove today's count
        data.pop()

        #print version
        #print data

        name = package+'-'+version
        for tuple in data:
            # tuple = [<timestamp>, <count>]
            # skip tuples that we've already stored in the db
            date = datetime.fromtimestamp(float(tuple[0])/1e3).__str__()[:10]
            count = tuple[1]
            if (date <= last_date):
                continue
            print date, name, count
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

