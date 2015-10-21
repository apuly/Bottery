#!/usr/bin/env python3


"""
Example Client for irclib

Copyright (C) 2014, 2015 Tyler Philbrick
All Rights Reserved
For license information, see COPYING
"""

from irclib.baseclient import BaseClient
import forums
import plotdata.plotmap as plotmap
import mcuuid
from collections import defaultdict
import re
import threading
from time import sleep
import configparser
#import json
#import urllib.request

class MyIRC(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cmdchar = config['BOT']['cmdChar']
        self.mcserverlist = config['MC']['serverList'].split()
        self.mcplayerlist = {}
        self.userdata = {'irc': defaultdict(dict), 'mc': defaultdict(dict)}
        self.config = loadSettings()
       
    def loop(self):
        self.getplayerlist()
        
    def handle_JOIN(self, line):
        if self.nick == line.nick:
            self.printing = True
            self.start_background_loop()
    
    def handle_QUIT(self, line):
        if self.frommc(line):
            self.mcplayerlist[line.nick] = []

    def mc_handle_MCPLAYERLIST(self, line, *args):
        if args[0] == 0:
            self.mcplayerlist[line.nick] = []
        else:
            self.mcplayerlist[line.nick] = args[1]

    def mc_handle_PLAYERLEFT(self, line, *args):
        if args[0] in self.mcplayerlist[line.nick]:
            self.mcplayerlist[line.nick].remove(args[0])
    
    def mc_handle_PLAYERJOINED(self, line, *args):
        #print('adding %s to server %s' % (line.mcparams, line.nick,))
        if not args[0] in self.mcplayerlist[line.nick]:
            self.mcplayerlist[line.nick].append(args[0])

    def cmd_RELOAD(self, line, *args):
        self.respond(line, 'Reloading the configuration.')
        self.config = loadSettings()

    def cmd_HELP(self, line, *args):
        self.respond(line, '{}list: Gives list of players on all servers'.format(self.cmdchar))
        self.respond(line, '{}search: Searches forums'.format(self.cmdchar))
        self.respond(line, 'Syntax: {}search <search term>'.format(self.cmdchar))
        self.respond(line, '{}plot: gets you the plotdata of old build'.format(self.cmdchar))
        self.respond(line, 'Syntax: {c}plot <player name> OR {c}plot <x coords> <y coords>'.format(c = self.cmdchar))

    def cmd_TEST(self, line, *args):
        self.respond(line, 'Werkin\'')

    def cmd_REFRESHLIST(self, line, *args):
        self.respond(line, "Refreshing player list")
        self.getplayerlist()
            
    def cmd_LIST(self, line, *args):
        if self.mcplayerlist is None:
            self.respond(line, 'Player list:')
        for mcserver in self.mcplayerlist:
            #print(self.mcplayerlist[mcserver])
            send = '{}: {}'.format(mcserver, ', '.join(self.mcplayerlist[mcserver]))
            self.respond(line, send)

    def cmd_APP(self, line, *args):
        if not self.config['FORUM'].getboolean('enabled'):
            self.respond(line, 'This command has been disabled.')
            return
        if len(args[1]) < 2:
            self.respond(line, 'Please put in a nickname to search.')
            return
        searchTerm = args[1][1]
        searchParams = self.searchParams(searchTerm, 37)
        try:
            forum.search('/search.php', searchParams)
        except forum.NoRedirect:
            self.respond("No redirect link was found. Either no results were found, or you need to retry.")
        except forum.NoPageFound:
            self.respond("Page could not be loaded. The forums might be down")
        result = forum.searchResults[0]
        self.respond(line, 'http://{}/{}'.format(forum.ip, result.title[1]))



    def cmd_SEARCH(self, line, *args):
        if not self.config['FORUM'].getboolean('enabled'):
            self.respond(line, 'This command has been disabled.')
            return
        if len(args[1]) < 2:
            self.respond(line, 'Please put in something to search.')
            return 
        searchTerm = args[1][1]
        searchParams = self.searchParams(searchTerm)
        try:
            forum.search('/search.php', searchParams)
        except forums.NoRedirect:
            self.respond("No redirect link was found. Either no results were found, or you need to retry.")
        except forums.NoPageFound:
            self.respond("Page could not be loaded. The forums might be down")
        self.addUserData(line, forum.searchResults[:5], args[0], 'searchResults')
        i=1
        for result in forum.searchResults[:5]:
            self.respond(line, '{}: {}'.format(i, result.title[0]))
            i += 1
        self.respond(line, 'Use the {}result command to view the links.'.format(self.cmdchar))

    def cmd_RESULT(self, line, *args):
        if not self.config['FORUM'].getboolean('enabled'):
            self.respond(line, 'This command has been disabled.')
            return
        if len(args[1]) < 2:
            self.respond(line, 'Please select what data you want.')
            return
        s_number = args[1][1]
        if not s_number.isdigit():
            self.respond(line, 'Please enter a number between 1 and 5')
            return
        index = int(s_number) - 1
        searchData = self.getUserData(line, args[0], 'searchResults')
        if searchData is None:
            self.respond(line, 'No data found. Before using this command, please use the {}search command.'.format(self.cmdchar))
            return
        if 0 <= index <= len(searchData):
            link = 'http://{}/{}'.format(forum.ip, searchData[index].title[1])
            self.respond(line, link)
        else:
            self.respond(line, 'No data found.')
            return
        

    def cmd_TIME(self, line, *args):
        self.respond(line, "It's time to go fuck yourself.")

    def cmd_PLOT(self, line, *args):
        if not self.config['PLOT'].getboolean('enabled'):
            self.respond(line, 'This command has been disabled.')
            return
        i = len(args[1])
        if i == 1:
            self.respond(line, 'Please input a nickname or plot coordinates')
        elif i == 2:
            playerName = args[1][1]
            plotList = plotdb.getPlotsByName(playerName)
            if not plotList:
                uuid = mcuuid.getUuidByCurrentName(playerName)
                if not uuid:
                    self.respond(line, 'No player found')
                    return
                else:
                    plotList = plotdb.getPlotsByUuid(uuid)
            self.respond(line, 'Plots owned by {}'.format(playerName))
            for plot in plotList:
                xcoord = plot[0] * 256 + 128
                ycoord = plot[1] * 256 + 128
                self.respond(line, 'X:{}, Y:{}, coordinates: {}, {}'.format(plot[0], plot[1], xcoord, ycoord))
        elif i == 3:
            if args[1][1].isint() and args[1][2].isint():
                xcoord = int(args[1][1])
                ycoord = int(args[1][2])
            else:
                self.respond(line, 'Please input valid coordinates.')
                return
            owner = plotdb.getOwnerByPlayerCoords(xcoord, ycoord)
            if owner is None:
                self.respond(line, 'Plot has no owner.')
            else:
                self.respond(line, 'Plot owned by {}'.format(owner[0]))


            

            

    #def mc_cmd_UUID(self, line):
    #    param = line.mcparams[-1].split()[1]
    #    self.mcprivmsg(line, self.getUuid(param))


        
    def getplayerlist(self):
        try:
            #print(self.mcserverlist)
            for mcserver in self.mcserverlist:
                #print(mcserver)
                self.privmsg(".list", target = mcserver)
                self.mcplayerlist[mcserver] = []
        except NameError:
            pass

    def addUserData(self, line, data, userName, dataName):
        if self.frommc(line):
            self.userdata['mc'][userName][dataName] = data
        else:
            self.userdata['irc'][userName][dataName] = data

    def getUserData(self, line, userName, dataName):
        if self.frommc(line):
            target = 'mc'
        else:
            target = 'irc'

        if userName in self.userdata[target]:
            if dataName in self.userdata[target][userName]:
                return self.userdata[target][userName][dataName]
        return None

    def respond(self, line, message, irctarget = None, mctarget = None):
       
        irctarget = irctarget or line.nick
        if line.nick in self.mcserverlist:
            mctarget = mctarget or line.params[-1].split()[0][:-1]
            self.privmsg(".msg {} {}".format(mctarget, message), irctarget)
        else:
            self.privmsg(message, irctarget)  
   
    def findPlayer(self, playerName):
        for item in self.mcplayerlist:
            if playerName in self.mcplayerlist[item]:
                return item


    def frommc(self, line):
        return line.nick in self.mcserverlist

    def searchParams(self, searchTerm, forums = ''):
        return {'submit':      'Search',
                    'sortordr':    'desc',
                    'sortby':      'lastpost',
                    'showresults': 'threads',
                    'postthread':  '1',
                    'postdate':    '0',
                    'pddir':       '1',
                    'keywords': searchTerm,
                    'forums[]': forums,
                    'findthreadst': '1',
                    'action': 'do_search' }
        
    def start_background_loop(self):
        thread = threading.Thread(target = self._loop)
        thread.start()

    def _loop(self):
        while True:
            self.loop()
            sleep(60)

    def isint(s):
        if s[0] in ('-', '+'):
            return s[1:].isdigit()
        return s.isdigit()


def loadSettings():
    config = configparser.ConfigParser()
    config.read('settings.txt')
    return config

plotdb = None
forum = None


if __name__ == "__main__":
    print("launching chatbot v2")
    config = loadSettings()
    forum = forums.forum(config['FORUM']['ip'], ssl = config['FORUM'].getboolean('ssl'))
    plotdb = plotmap.plotmap(config['PLOT']['dbFile'])
    plotdb.connect()
    #forum.open()

    sub_config = config['IRC']
    irc = MyIRC(
        (sub_config['ip'], sub_config.getint('port')),
        (sub_config['username'], sub_config['hostname'], sub_config['realname']),
        sub_config['nick'],
        sub_config['channel'],
        printing = True
    )

    irc.run()
