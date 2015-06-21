"""
IRC clientside library

Copyright (C) 2014, Tyler Philbrick
All Rights Reserved
For license information, see COPYING
"""

import socket
from collections import namedtuple, defaultdict

import irclib.parser as parser


class BaseIRC(object):
    """Client object makes connection to IRC server and handles data

    example usage:
    """
    #TODO : update usage example

    def __init__(self, server, names, nick, channel, sock=None, printing=True):
        """Initialiser creates an unbound socket"""
        self.sock = sock or socket.socket()
        self.server = server
        self.names = names
        self.nick = nick
        self.channel = channel
        self.printing = printing

    def _send(self, message):
        """Private method invoked by others to send on socket

        Adds \r\n at the end of messages
        """
        if self.printing:
            print("<< " + message)
        self.sock.sendall((message + "\r\n").encode())

    def connect(self, server=None):
        """Implements socket connection to IRC server

        server_info is tuple of (hostname, port)
        """
        server = server or self.server
        self.sock.connect(server)

    def ident(self, names=None):
        """Sends irclib identity to server,

        Can take either an arbitrary iterable eqivalent to
        [user, host, real]
        or a dict of schema:
        {'user':user, 'host':host, 'real':real}
        """
        names = names or self.names
        if isinstance(names, dict):
            send = "USER {user} 0 * :{real}".format(**names)
        else:
            send = "USER {} 0 * :{}".format(*names)
        self._send(send)

    def set_nick(self, nick=None):
        """Binds or changes irclib nickname

        Note that some servers require you to privmsg a nickname bot
        to verify registerd nicknames
        """
        nick = nick or self.nick
        send = "NICK {}".format(nick)
        self._send(send)

    def join(self, channel=None):
        """Implements irclib joining a channel"""
        channel = channel or self.channel
        send = "JOIN {}".format(channel)
        self._send(send)

    def privmsg(self, message, target=None):
        """Sends a message to <target>

        Can be channel or individual
        """
        target = target or self.channel

        send = "PRIVMSG {} :{}".format(target, message)
        self._send(send)

    def _handle_register(self, line):
        """Handling of registered operations"""
        
        try:
            #print("handle_" + line.command.upper())
            getattr(self, "handle_" + line.command.upper())(line)
        #except Exception as E:
        #    print(E)
        except AttributeError:
            pass

    def _handle_mc_registered(self, line):
        try:
            #print("mc_handle_" + line.mcevent.upper())
            getattr(self, "mc_handle_" + line.mcevent.upper())(line)
        #except Exception as E:
        #    print(E)
        except AttributeError:
            pass

    def run(self):
        """Run IRC program"""
        sockf = self.sock.makefile()

        for line in sockf:
            if self.printing:
                try:
                    print((">> " + line).rstrip('\r\n'))
                except UnicodeEncodeError:
                    pass
            p_line = parser.Line(line, self.mcserverlist)
            #additional code created for porting to openredstone server chat
            if not p_line.frommc:
                self._handle_register(p_line)
            else:
                self._handle_mc_registered(p_line)

    #additional functions added for porting to openredstone server chat
    def mcprivmsg(self, line, message, mctarget = None, irctarget = None):
        irctarget = irctarget or line._nick
        mctarget = mctarget or line._mcparams[0]

        send = 'PRIVMSG {} :.msg {} {}'.format(irctarget, mctarget, message)
        self._send(send)



            

