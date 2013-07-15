# -*- coding: utf-8 -*-s
# Copyright (c) 2013, Michael Stolovitzsky (emestee@catnarok.net)
# Based on work by Wojciech Bederski (wuub.net)
# All rights reserved. 
# See LICENSE.txt for details.

from repls import Repl
import sublime_plugin
import sublimerepl

from time import sleep

import dev_bensock as bensock
import socket

class ReplEnterClojureNreplCommand(sublime_plugin.TextCommand):
    def run(self, edit):
       rv = sublimerepl.manager.repl_view(self.view)
       print self.view, rv
       if rv:
            rv.replace_current_input(edit, rv.user_input + "\n")
            self.view.show(rv.input_region)
            rv.enter()
    
class ClojureNreplRepl(Repl):
    TYPE = "clojure_nrepl"

    @property
    def prompt(self):
        return "%s > " % self._ns

    def __init__(self, encoding="utf-8", external_id=None, host="localhost", port=None, suppress_echo=False):
        """Create new ClojureNreplRepl with the following initial values:
        encoding: one of python accepted encoding used to encode commands and decode responses
        external_id: external, persistent name of this repl used to find it later
        host: nrepl server host to connect to
        port: nrepl server port to connect to
        """

        Repl.__init__(self, encoding, external_id, "", suppress_echo)
        self._alive = True
        self._killed = False
        self._sessions = []
        self._current_session = None
        self._socket = None
        self._bencode_socket = None
        self._ns = "(unknown)"
        self._debug_recv = True
        self._debug_eval = True

        self.connect(host, port)

    def name(self):
        return "Clojure %s:%s" % (self._host, self._port)

    def is_alive(self):
        return self._bencode_socket.socket is not None

    def read_bytes(self):
        o = []

        nrepl_msg = self._bencode_socket.recv()
        if nrepl_msg is None:
            self.kill()
            return None

        if self._debug_recv:
            print nrepl_msg
        init='id' in nrepl_msg and nrepl_msg['id'] == 'init'

        if 'new-session' in nrepl_msg:
            self._current_session = nrepl_msg['new-session']

        if 'ns' in nrepl_msg:
            self._ns = nrepl_msg['ns']

        if 'status' in nrepl_msg and 'done' in nrepl_msg['status']:
            if 'id' in nrepl_msg and nrepl_msg['id'] in self._evals:
                self._evals.remove(nrepl_msg['id'])
            # Prompt injection hack
            if not init:
                o.append("")
                o.append(self.prompt) 
    
        if 'out' in nrepl_msg:
            o.append(nrepl_msg['out'] + "\n")

        if 'status' in nrepl_msg:
            if 'eval-error' in nrepl_msg['status']:
                o.append("Evaluation error")
                o.append("Root exception: " + nrepl_msg['root-ex'])
                o.append("Exception: " + nrepl_msg['ex'])

        if 'err' in nrepl_msg:
            o.append(nrepl_msg['err'])

        if 'value' in nrepl_msg:
            # Suppress initialization output
            if 'id' in nrepl_msg and nrepl_msg['id'] == 'init':
                self._current_session = nrepl_msg['session']
                return self.read_bytes()
            o.append(nrepl_msg['value'] + "\n")

        return "\n".join(o)

    def write_bytes(self, bytes):
        print "write_bytes() at instance", self, "sock", self._bencode_socket
        if bytes == "":
            return

        self._eval_seq += 1
        self._evals.append(self._eval_seq)
        print "%d evals pending" % len(self._evals)
        self.op_eval(self._current_session, bytes, self._eval_seq)

    def kill(self):
        self.disconnect()
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
        self._bencode_socket = bensock.BencodeStreamSocket(s)
        self.session_init()

    def disconnect(self):
        self._bencode_socket.disconnect()
        self._bencode_socket = None

    def session_init(self):
        self._evals = []
        self.op_clone('init')
        self.read_bytes()
        self.op_eval(self._current_session, '1')
        self.read_bytes()
        self._eval_seq = 0

    def op_clone(self, id=None):
        op = {'op': 'clone'}
        if id:
            op['id'] = id

        self._bencode_socket.send(op)

    def op_eval(self, session, s, id=None):
        op = {'op': 'eval', 'code': s}
        if session is not None:
            op['session'] = session

        if id is not None:
            op['id'] = id

        if self._debug_eval:
            print "eval", s, self
        self._bencode_socket.send(op)
