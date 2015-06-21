import http.client
import urllib.parse
from html import parser
import bs4
import re

class open(object):
    def __init__(self, ip, port = None, ssl = False):
        self.ip = ip
        self._port = port
        self._ssl = ssl
        self.prepareSearch()

    def open(self):
        if not self._ssl:
            self._conn = http.client.HTTPConnection(self.ip, self._port)
        else:
            self._conn = http.client.HTTPSConnection(self.ip, self._port)

    def request(self, method, url, body = None, header = {}):
        self._conn.request(method, url, body, header)
        self.resp = self._conn.getresponse()
        
    def prepareSearch(self, searchUrl = None, header = None):
        self.searchUrl = searchUrl or '/search.php'
        self.header = header or {"Content-type": "application/x-www-form-urlencoded", 
                                 "submit": "text/plain"}

    def search(self, searchParams):
        

        self.searchParams = searchParams
        encodeParams = urllib.parse.urlencode(searchParams)
        
        #self._conn = http.client.HTTPSConnection(self._ip, self._port)

        self.open()


        try:        
            self.request('POST', self.searchUrl, encodeParams, self.header)
        except http.client.BadStatusLine:
            return self.results

        if self.resp.status != 200:
            return None
        soup = bs4.BeautifulSoup(self.resp.readall())
        url = soup.find('a').get('href')
        if url is None:
            return None
            #raise NoUrlError("Resultpage URL not found.")


        self.request("GET", '/{}'.format(url))

        if self.resp.status != 200:
            return None
        pageContent = self.resp.readall().decode()
        regex = r'<a href="showthread\.php\?tid=\d+&amp;highlight=%s" class=" subject_old" id="tid_\d+">.{1,85}</a>' % self.searchParams['keywords']
        regexResult = re.findall(regex, pageContent, re.I)
        self.results = self.parseLinks(regexResult)
        return self.results


    def parseLinks(self, links):
        out = []
        for link in links:
            soup = bs4.BeautifulSoup(link)
            url = soup.find('a').get('href')
            title = soup.getText()
            out.append((url, title))
        return out

        
    #class NoUrlError(Exception):
    #    def __init__(self, value):
    #        self.value = value
    #    def __str__(self):
    #        return repr(self.value)