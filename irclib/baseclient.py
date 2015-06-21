"""
Base client class for my IRC clientside library

Copyright (C) 2014, 2015 Tyler Philbrick
All Rights Reserved
For license information, see COPYING
"""

from irclib.baseirc import BaseIRC


class BaseClient(BaseIRC):
    def __init__(self, *args, **kwargs):
        """Initiates connection"""
        super().__init__(*args, **kwargs)
        self.connect()
        self.ident()
        self.set_nick()
        self.join()

    def handle_PING(self, line):
        """Implements PONG"""
        send = "PONG :{}".format(line.params[-1])
        self._send(send)

    def handle_PRIVMSG(self, line):
        """Calls gocmd_<word> when command is received"""
        
        try:
            if not line.params[-1].startswith(self.cmdchar):
                return
        except AttributeError:
            return
        try:
            getattr(self, "cmd_" + line.params[-1].split()[0][1:].upper())(line)
        except AttributeError:
            pass

    #code created for porting to openredstone server chat
    def mc_handle_MESSAGE(self, line):
        try:
            if not line.mcparams[1].startswith(self.cmdchar):
                return
        except AttributeError:
            return
        try:
            getattr(self, "mc_cmd_" + line.mcparams[1].split()[0][1:].upper())(line)
        except AttributeError as E:
            print(E)
            pass
        