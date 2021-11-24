from urllib.request import urlopen
import csv
import IP2Location
import os
import socket
from bs4 import BeautifulSoup


def read_data(filename):
    file = open(filename)
    csvreader = csv.reader(file)
    # read the header
    next(csvreader)
    for row in csvreader:
        websites.append({'name': row[0], 'category': row[1], 'location': row[2], 'url': row[3], 'purl': row[4]})


def get_geo(url):
    if 'www' not in url:
        url = url[8:]
    else :
        url = url[12:]
    database = IP2Location.IP2Location(os.path.join("../data", "IP2LOCATION-LITE-DB3.IPV6.BIN"))
    rec = 'N/A'
    try:
        ip = socket.gethostbyname(url)
        try:
            rec = database.get_region(ip)
        except:
            pass
    except:
        pass
    print(url, rec)
    return rec


def detect(website):
    row = []
    # name
    row.append(website.get('name'))
    # category
    row.append(website.get('category'))
    # company region
    row.append(website.get('location'))
    # host region
    row.append(get_geo(website.get('url')))
    # privacy policy region
    row.append(get_geo(website.get('purl')))
    try:
        html = urlopen(website.get('purl'), timeout=10).read()
        soup = BeautifulSoup(html, features="html.parser")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()  # rip it out

        # get text
        text = soup.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        content = '\n'.join(chunk for chunk in chunks if chunk)
        matches = ["DNT", "Do Not Track", "do not track", "禁止追踪"]
        s = ''
        dnt = 'No'
        mention = 'No'
        sts = content.split('.')
        idx = 0
        for sentence in sts:
            if any(x in sentence for x in matches):
                if idx != 0 and idx != len(sts) - 2:
                    if not sts[idx - 1] in s:
                        s += sts[idx - 1]
                    if not sentence in s:
                        s += sentence
                    if not sts[idx + 1] in s:
                        s += sts[idx + 1]
                    if not sts[idx + 2] in s:
                        s += sts[idx + 2]
                mention = 'Yes'
            idx += 1
        # mention DNT?
        row.append(mention)
        # sentence
        row.append(s)
        if mention == 'Yes':
            dnt = 'Yes'
        dn_matches = ["do not support", "do not respond", "does not support", "doest not respond", "don't", "don’t"
            , "do not recognize", "does not"]
        if any(x in s for x in dn_matches):
            dnt = 'No'
        # support DNT?
        row.append(dnt)
    except:
        row.append('No')
        row.append('')
        row.append('No')
    return row


if __name__ == "__main__":
    websites = []
    read_data('../data/websites.csv')

    # result = polipy.get_policy("https://www.nytimes.com/privacy/privacy-policy#what-information-do-we-gather-about-you", screenshot=True)
    # result.save(output_dir='../data')
    with open('../data/websites_data.csv', mode='w') as data:
        data_writer = csv.writer(data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # Write header
        data_writer.writerow(
            ['name', 'category', 'company_region', 'host_region', 'privacy_policy_region', 'mention_DNT', 'sentence',
             'support_DNT'])
        for site in websites:
            r = detect(site)
            print(r)
            data_writer.writerow(r)
