#!/usr/bin/env python3


"""
Example Client for irclib

Copyright (C) 2014, 2015 Tyler Philbrick
All Rights Reserved
For license information, see COPYING
"""

from irclib.baseclient import BaseClient
import winsound
import forums
import string
import json
import urllib.request

class MyIRC(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cmdchar = "~"
        self.mcserverlist = ['OREBuild', 'ORESchool', 'ORESurvival']
        self.mcplayerlist = {}
        self.mcplayerdata = {}

    def handle_JOIN(self, line):
        if self.nick == line.nick:
            self.printing = True
            self.getplayerlist()

    def cmd_HELP(self, line):
        self.privmsg("You can do ~test or ~pm", target=line.nick)

    def cmd_TEST(self, line):
        self.privmsg("This is a test, it worked too, how about that!",
            target=line.nick)

    def mc_cmd_TEST(self, line):
        self.mcprivmsg(line, 'Werkin\'')

    def mc_cmd_REFRESHLIST(self, line):
        self.mcprivmsg(line, "Refreshing player list")
        self.getplayerlist()
    
    def mc_handle_MCPLAYERLIST(self, line):
        if line.mcparams[0] == 0:
            self.mcplayerlist[line.nick] = []
        else:
            self.mcplayerlist[line.nick] = line.mcparams[1]

    def mc_cmd_POKE(self, line):
        self.mcprivmsg(line, 'Apuly has been poked')
        winsound.PlaySound('SystemExclamation', winsound.SND_ASYNC)

    def mc_handle_PLAYERLEFT(self, line):
        if line.mcparams in self.mcplayerlist[line.nick]:
            self.mcplayerlist[line.nick].remove(line.mcparams)
    
    def mc_handle_PLAYERJOINED(self, line):
        #print('adding %s to server %s' % (line.mcparams, line.nick,))
        if not line.mcparams in self.mcplayerlist[line.nick]:
            self.mcplayerlist[line.nick].append(line.mcparams)

    def mc_cmd_LIST(self, line):
        if self.mcplayerlist is None:
            return
        self.mcprivmsg(line, 'Player list:')
        for mcserver in self.mcplayerlist:
            #print(self.mcplayerlist[mcserver])
            send = '{}: {}'.format(mcserver, ', '.join(self.mcplayerlist[mcserver]))
            self.mcprivmsg(line, send)

    def mc_cmd_SEARCH(self, line):
        searchTerm = line.mcparams[-1].split()[1]
        searchParams = self.searchParams(searchTerm)
        results = forum.search(searchParams)
        if results is None:
            self.mcprivmsg(line, 'Cooldown period has not yet expired. Please wait.')
            return
        self.mcplayerdata[line.mcparams[0]] = {'searchResults': results[0:5]}
        i=1
        for result in results[0:5]:
            self.mcprivmsg(line, '{}: {}'.format(i, result[1]))
            i += 1
        self.mcprivmsg(line, 'Use the {}result command to view the links.'.format(self.cmdchar))

    def mc_cmd_RESULT(self, line):
        try:
            data = self.mcplayerdata[line.mcparams[0]]['searchResults']
        except KeyError:
            self.mcprivmsg(line, 'No data found. Before using this command, please use the {}search command.'.format(self.cmdchar))
            return
        s_number = line.mcparams[-1].split()[1][0]
        if s_number in string.digits:
            index = int(s_number)-1
            if 0 <= index <= 4:
                try:
                    self.mcprivmsg(line, 'http://{}/{}'.format(forum.ip, data[index][0]))
                    return
                except IndexError:
                    self.mcprivmsg(line, 'No data found.')
                    return
        self.mcprivmsg(line, 'Please enter a number between 1 and 5')

    #def mc_cmd_UUID(self, line):
    #    param = line.mcparams[-1].split()[1]
    #    self.mcprivmsg(line, self.getUuid(param))

    #def getUuid(self, playerName):
    #    f = urllib.request.urlopen('https://api.mojang.com/users/profiles/minecraft/%s' % playerName)
    #    response = f.read(100).decode()
    #    playerProp = json.loads(response)
    #    return playerProp['id']

        
    def getplayerlist(self):
        try:
            #print(self.mcserverlist)
            for mcserver in self.mcserverlist:
                #print(mcserver)
                self.privmsg(".list", target = mcserver)
                self.mcplayerlist[mcserver] = []
        except NameError:
            pass

    def searchParams(self, searchTerm):
        return {'submit':      'Search',
                  'sortordr':    'desc',
                  'sortby':      'lastpost',
                  'showresults': 'threads',
                  'postthread':  '1',
                  'postdate':    '0',
                  'pddir':       '1',
                  'keywords': searchTerm,
                  'forum[]': '10',
                  'findthreadst': '1',
                  'action': 'do_search' }
        

if __name__ == "__main__":
    print("launching chatbot v2")
    forum = forums.open('forum.openredstone.org', ssl = True)
    #forum.open()
    irc = MyIRC(
        ("irc.freenode.net", 6667),
        ("usern", "hostn", "realn"),
        "Bottery",
        "#openredstone",
        printing = False
    )

    irc.run()
