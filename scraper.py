import json
import lxml.html
import re
import requests
import scraperwiki

downloads = {}

for package in ['ostinato-bin-win32', 'ostinato-bin-osx-universal', 'ostinato-src']:
    page = requests.get('https://bintray.com/pstavirs/ostinato/'+package+'/#statistics') 
    doc = lxml.html.document_fromstring(page.text)

    # get the javascript snippet containing the downloads data
    script = doc.xpath("//div[@id='renderPkgPage']//div[@id='show-pkg']/script[1]")[0]
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

    # since today is not yet over, get yesterday's count 
    name = package+'-'+j[0]['name']
    date = j[0]['data'][-2][0]
    count = j[0]['data'][-2][1]
    #print date, name, count
    downloads['Date'] = date
    downloads[name] = count

print downloads
scraperwiki.sqlite.save(unique_keys=['Date'], data=downloads, table_name='downloads')

