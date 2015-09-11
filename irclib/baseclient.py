"""
Base client class for my IRC clientside library

Copyright (C) 2014, 2015 Tyler Philbrick, Paul Bersee
All Rights Reserved
For license information, see COPYING
"""

from irclib.baseirc import BaseIRC
import re
from time import sleep


class BaseClient(BaseIRC):
    def __init__(self, *args, **kwargs):
        """Initiates connection"""
        super().__init__(*args, **kwargs)
        self.connect()
        self.ident()
        self.set_nick()

    def handle_001(self, line):
        self.join()

    def handle_PING(self, line):
        """Implements PONG"""
        send = "PONG :{}".format(line.params[-1])
        self._send(send)

    def handle_PRIVMSG(self, line):
        """Calls cmd_<word> when command is received"""
        if line.nick in self.mcserverlist:
            self.handleMcMessage(line)
        #else:
        #    self.handleIrcMessage(line)

    def handleIrcMessage(self, line):  
        try:
            if not line.params[-1].startswith(self.cmdchar):
                return
        except AttributeError:
            return
        try:
            getattr(self, "cmd_" + line.params[-1].split()[0][1:].upper())(line, line.nick, line.params[-1].split())
        except AttributeError:
            pass


    def handleMcMessage(self, line):
        words = line.params[-1].split()
        if words[0][-1] == ':':
            if len(words) == 1:
                return
            if not words[1].startswith(self.cmdchar):
                return
            try:
                getattr(self, "cmd_" + words[1][1:].upper())(line, words[0][:-1], words[1:])
            except AttributeError:
                pass
        else:
            regex = re.match(r'^(\w+) (left|joined) the game', line.params[-1])
            if regex:
                try:
                    getattr(self, "mc_handle_PLAYER{}".format(regex.group(2).upper()))(line, regex.group(1))
                except AttributeError:
                    pass
                finally:
                    return
                #self._mcparams = regex.group(1)
                #self._mcevent = 'player' + regex.group(2)
            regex = re.match(r'(\d{1,2}) player\/s online:( [(, )+](, )?)*', line.params[-1])
            if regex:
                #self._mcevent = 'mcplayerlist'
                #self._mcparams = [int(regex.group(1))]
                if line.params[-1][-1] != ':':
                    params = line.params[-1].split(': ')[1].strip('\n').split(', ')
                    for i in range(len(params)):
                        params[i] = params[i].split(']',1)[-1]
                else:
                    params = []
                try:
                    getattr(self, "mc_handle_MCPLAYERLIST")(line, int(regex.group(1)), params)
                except AttributeError:
                    pass
                finally:
                    return
                #print(params)
                #self._mcparams.append(params)