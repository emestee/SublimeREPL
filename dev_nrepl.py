# -*- coding: utf-8 -*-s
# Copyright (c) 2011, Michael Stolovitzsky (emestee@catnarok.net)
# Based on work by Wojciech Bederski (wuub.net)
# All rights reserved. 
# See LICENSE.txt for details.

from repls import Repl
from time import sleep

import dev_bensock as bensock

import socket

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
        return "%s > " % self._ns

    def __init__(self, encoding="utf-8", external_id=None, host="localhost", port=4001, suppress_echo=False):
        """Create new ClojureNreplRepl with the following initial values:
        encoding: one of python accepted encoding used to encode commands and decode responses
        external_id: external, persistent name of this repl used to find it later
        host: nrepl server host to connect to
        port: nrepl server port to connect to
        cmd_postfix: some REPLS require you to end a command with a postfix to begin execution,
          think ';' or '.', you can force repl to add it automatically"""

        Repl.__init__(self, encoding, external_id, "", suppress_echo)
        self._alive = True
        self._killed = False
        self._sessions = []
        self._current_session = None
        self._socket = None
        self._bencode_socket = None
        if host and port:
            self.connect(host, port)

    def name(self):
        return "Clojure %s:%s" % (self._host, self._port)

    def is_alive(self):
        return self._alive

    def read_bytes(self):
        nrepl_msg = self._bencode_socket.recv()
        print "nrepl in:", nrepl_msg

        o = [""]
        if 'status' in nrepl_msg:
            if 'eval-error' in nrepl_msg['status']:
                o.append("Evaluation error")
                o.append("Root exception: " + nrepl_msg['root-ex'])
                o.append("Exception: " + nrepl_msg['ex'])

            if 'done' in nrepl_msg['status']:
                o.append("")        

        if 'err' in nrepl_msg:
            o.append(nrepl_msg['err'])

        if 'value' in nrepl_msg:
            o.append(nrepl_msg['value'])
            self._ns = nrepl_msg['ns']

        o = "\n".join(o)

        return o

    def write_bytes(self, bytes):
        self.eval(self._current_session, bytes)

    def kill(self):
        self._killed = True
        self._alive = False

    def connect(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # try:
        s.connect((host, port))
        # except socket.error, e:
            # XXX handle errors
        self._socket = s
        self._host = host
        self._port = port
        
        # self.protocol = Protocol(s)
        # self.protocol.start()
        # self.initialize_session()
        print "connected to %s:%s" % (host, port)
        self._bencode_socket = bensock.BencodeStreamSocket(s)

    def eval(self, session, s):
        op = {'op': 'eval', 'code': s}
        if session is not None:
            op['session'] = session
        
        print "eval", op
        self._bencode_socket.send(op)