# -*- coding: utf-8 -*-s
# Copyright (c) 2011, Michael Stolovitzsky (emestee@catnarok.net)
# Based on work by Wojciech Bederski (wuub.net)
# All rights reserved. 
# See LICENSE.txt for details.

#import sublime_plugin
#import sublimerepl

# from nrepl_client.repl import Repl as NReplClient
# from nrepl_client.terminal import SublimeTerminal as NReplSublimeTerminal

from repls import Repl
# 
from time import sleep

#class ReplEnterClojureNreplCommand(sublime_plugin.TextCommand):
#    def run(self, edit):
#        rv = sublimerepl.manager.repl_view(self.view)
#        print self.view, rv
#        if rv:
#            rv.enter()
#            rv.repl._terminal.internal.write(">>> ")
    
class ClojureNreplRepl(Repl):
    TYPE = "clojure_nrepl"

    @property
    def prompt(self):
        return "%s > " % self._nrepl.session.ns

    def __init__(self, encoding, external_id=None, host="localhost", port=4001, suppress_echo=False):
        """Create new ClojureNreplRepl with the following initial values:
        encoding: one of python accepted encoding used to encode commands and decode responses
        external_id: external, persistent name of this repl used to find it later
        host: nrepl server host to connect to
        port: nrepl server port to connect to
        cmd_postfix: some REPLS require you to end a command with a postfix to begin execution,
          think ';' or '.', you can force repl to add it automatically"""

        super(ClojureNreplRepl, self).__init__(encoding, external_id, "", suppress_echo)
        # self._terminal = NReplSublimeTerminal()
        # self._nrepl = NReplClient((host, int(port)), terminal=self._terminal)
        self._host = host
        self._port = port
        self._alive = True
        self._killed = False

    def name(self):
        return "Clojure nrepl %s:%s" % (self._host, self._port)

    def is_alive(self):
        return false
        return self._alive

    def read_bytes(self):
        return None
        """Read waiting input from vt"""
        # msg = self._terminal.read()
        msg = ""
        return "\n" + msg
        
    def write_bytes(self, bytes):
        pass
        # self._nrepl.user_input(bytes)

    def kill(self):
        self._killed = True
        self._alive = False

