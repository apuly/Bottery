import re

"""
IRC clientside library

Copyright (C) 2014, Tyler Philbrick
All Rights Reserved
For license information, see COPYING
"""

"""Parses IRC message

Input is line from the IRC server,
Output is named tuple with keys:
    raw: the raw line input
    prefix: the IRC prefix including nick, user/hostname, etc
    nick: the sender's nickname (if any)
    command: the IRC command <- this is the only required part
    params: the command's parameters as a list
    trail: the IRC line's trailing section.  If the line is a
        user chat, the message is here
Any part of the line not included is None
"""

class Line(object):
    def __init__(self, line):
        self._regex = re.compile("\x0f|\x1f|\x02|\x03(?:\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)
        line = line.rstrip('\r\n')        
        
        line = self._regex.sub("", line)
        self._raw = line

        if line[0] == ":":
            self._prefix, line = spl1n(line, " ")
            self._nick = self._prefix.split("!")[0][1:]
        else:
            self._prefix = None
            self._nick = None
        self._command, line = spl1n(line, " ")
        self._params, trail = spl1n(line, ":")
        self._params = self._params.strip().split(" ")
        if trail:
            self._params.append(trail)
        

            
        
        ##code added for ORE server chat compatibility
        #if self._nick and self._serverList:
        #    if self._nick in self._serverList: #move serverList to external variable
        #        self._frommc = True
        #        words = self._params[-1].split()
        #        if words[0][-1] == ':':
        #            self._mcevent = 'message'
        #            mcsender = words[0][:-1]
        #            mcmessage = ' '.join(words[1:])
        #            self._mcparams = (mcsender, mcmessage,)
                        
        #        else:
        #            regex = re.match(r'^(\w+) (left|joined) the game', self._params[-1])
        #            if regex:
        #                self._mcparams = regex.group(1)
        #                self._mcevent = 'player' + regex.group(2)
        #                return
        #            regex = re.match(r'(\d{1,2}) player\/s online: ([(, )+](, )?)*', self._params[-1])
        #            if regex:
        #                self._mcevent = 'mcplayerlist'
        #                self._mcparams = [int(regex.group(1))]
        #                params = self._params[-1].split(': ')[1].strip('\n').split(', ')
        #                for i in range(len(params)):
        #                    params[i] = params[i].split(']',1)[-1]
        #                #print(params)
        #                self._mcparams.append(params)



                    





    @property
    def raw(self):
        return self._raw

    @property
    def prefix(self):
        return self._prefix

    @property
    def nick(self):
        return self._nick

    @property
    def command(self):
        return self._command

    @property
    def params(self):
        return self._params

    #@property
    #def trail(self):
    #    return self._trail

    #code added for ORE server chat compatibility

    #@property
    #def mcparams(self):
    #    return self._mcparams

    #@property
    #def mcevent(self):
    #    return self._mcevent

    #@property
    #def frommc(self):
    #    return self._frommc

def spl1n(string, sep):
    """Splits string once on the first occurance of sep
    returns [head, tail] if succesful, and 
    returns (string, None) if not.

    Intended for scenarios when using unpacking with an unknown string.
    """
    r = string.split(sep, 1)
    if len(r) > 1:
        return r
    else:
       return string, None
