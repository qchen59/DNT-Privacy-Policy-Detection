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
        websites.append({'name': row[0], 'category': row[1], 'location': row[2], 'purl': row[3], 'url': row[4]})


def get_geo(url):
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

    return rec


def detect(website):
    try:
        html = urlopen(website.get('purl')).read()
        soup = BeautifulSoup(html, features="html.parser")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip it out

        # get text
        text = soup.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        content = '\n'.join(chunk for chunk in chunks if chunk)

        # result.save(output_dir='../data')
        matches = ["DNT", "Do Not Track", "do not track"]
        s = ''
        mention = 'No'
        for sentence in content.split('.'):
            if any(x in sentence for x in matches):
                print(sentence)
                s += sentence
                mention = 'Yes'
    except:
        pass


if __name__ == "__main__":
    websites = []
    read_data('../data/websites.csv')

    for site in websites:
        r = detect(site)
