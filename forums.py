import http.client as client
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from collections import namedtuple

#Forum object, created for mybb forum software.
class forum(object):
    def __init__(self, ip, ssl = False, port = None):
        self._ip = ip
        self._ssl = ssl
        self._port = port
    
    #setup the http connection to the forum; returns connection
    def _conn(self):
        if self._ssl:
            conn = client.HTTPSConnection(self._ip, self._port)
        else:
            conn = client.HTTPConnection(self._ip, self._port)
        return conn

    #executes an http GET; returns http response
    def _get(self, url):
        conn = self._conn()
        conn.request('GET', url)
        return conn.getresponse()
    
    #executes an http POST; returns http response
    def _post(self, url, body = None, header = {}):
        conn = self._conn()
        conn.request('POST', url, body, header)
        return conn.getresponse()

    def openPage(self, url):
        return self._get(url)


    #searches the given string on the forums. Requeres body & header, resturn a named tuple of the results
    def search(self, searchUrl, params, header = None):
        #Search from search page
        params = urlencode(params)
        header = header or self._defaultHeader
        self.resp = self._post(searchUrl, params, header)
        if self.resp.status != 200:
            raise self.NoPageFound('Bad response status')
        #get URL from redirect
        soup = BeautifulSoup(self.resp.readall(), 'html.parser')
        url = soup.find('a').get('href')
        if url is None:
            raise self.NoRedirect('Redirect link not found.')
        #load search results
        self.resp = self._get('/{}'.format(url))
        if self.resp.status != 200:
            raise self.NoPageFound('Bad responsen status')
        self.searchResults = self._parseResults(self.resp.readall())

    #Parses the html from the result page; returns named tuple of the results
    def _parseResults(self, html):
        results = []
        #tuple = namedtuple('searchResults', ['thread', 'forum', 'author', 'lastreplier', 'lastreplytime'])
        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.findAll('tr', class_ = 'inline_row')
        for row in rows:
            lines = row.findAll('td')

            line = lines[2].find(class_ = ' subject_old')
            title = self._parseHref(line)

            line = lines[2].find(class_ = 'author smalltext').find('a')
            author = self._parseHref(line)

            line = lines[3].find('a')
            forum_ = self._parseHref(line)

            line = lines[6].findAll('a')[-1]
            lastreplier = self._parseHref(line)

            lastreplytime = lines[6].find('span').getText().split()[:2]

            view_count = lines[5].getText()

            reply_count = lines[4].getText()

            results.append(ThreadList(forum_, title, author, reply_count, view_count, lastreplier, lastreplytime))
        return results
    
    #Parse html, returns tuple containing readable text and the URL
    def _parseHref(self, line):
        return (line.getText(), line.get('href'))

    #Generates the default search parameters.
    def genSearchParams(self, keywords):
        params = self._defaultParams
        params['keywords'] = keywords
        return params

    #Default search paramters, without the searchterm
    _defaultParams = {'submit':      'Search',
                     'sortordr':    'desc',
                     'sortby':      'lastpost',
                     'showresults': 'threads',
                     'postthread':  '1',
                     'postdate':    '0',
                     'pddir':       '1',
                     'keywords': None,
                     'forum[]': '1',
                     'findthreadst': '1',
                     'action': 'do_search' }

    #Default header
    _defaultHeader = {"Content-type": "application/x-www-form-urlencoded", 
                                 "submit": "text/plain"}

    #Exception raised when http response does not have status 200
    class NoPageFound(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr(self.value)
    

    #Exception raised when there is no URL found on the redirect page.
    #This occurs when searching 
    class NoRedirect(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr(self.value)

class ThreadList(object):
    def __init__(self, forum, title, author, reply_count, view_count, last_poster, last_post_time):
        self._title = title
        self._author = author
        self._forum = forum
        self._replc = reply_count
        self._viewc = reply_count
        self._lastpr = last_poster
        self._lastpt = last_post_time
    @property
    def forum(self):
        return self._forum
    @property
    def title(self):
        return self._title
    @property
    def author(self):
        return self._author
    @property
    def reply_count(self):
        return self._replc
    @property
    def view_count(self):
        return self._viewc
    @property
    def last_replier(self):
        return self._lastpr
    @property
    def last_reply_time(self):
        return self._lastpt

    class subforum(object):
        def __init__(self, threads = [], subforums = []):
            self._threads = threads
            self._subforums = subforums
