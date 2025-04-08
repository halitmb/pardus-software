#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 14:53:00 2020

@author: fatih
"""

import json

import gi

gi.require_version("GLib", "2.0")
gi.require_version('Soup', '2.4')
from gi.repository import GLib, Gio, Soup
from Logger import Logger


class AppDetail(object):
    def __init__(self):

        self.session = Soup.Session(user_agent="application/json")
        self.Logger = Logger(__name__)

    def get_details(self, uri, dic):
        message = Soup.Message.new("POST", uri)
        message.set_request('Content-type:application/json', Soup.MemoryUse.COPY, json.dumps(dic).encode('utf-8'))
        message.request_headers.append('Content-type', 'application/json')
        self.session.send_async(message, None, self.on_finished, message, dic["app"])

    def on_finished(self, session, result, message, app):
        try:
            input_stream = session.send_finish(result)
        except GLib.Error as error:
            if message.status_code == Soup.Status.SSL_FAILED:
                self.session.props.ssl_strict = False
            self.Logger.warning("AppDetail stream Error: {}, {}".format(error.domain, error.message))
            self.Logger.exception("{}".format(error))
            self.app_details_from_server(False)
            return False

        if input_stream:
            data_input_stream = Gio.DataInputStream.new(input_stream)
            line, length = data_input_stream.read_line_utf8()
            self.app_details_from_server(True, json.loads(line), app)
        input_stream.close_async(GLib.PRIORITY_LOW, None, self._close_stream, None)

    def _close_stream(self, session, result, data):
        try:
            session.close_finish(result)
        except GLib.Error as error:
            self.Logger.warning("AppDetail Close Error: {}, {}".format(error.domain, error.message))
            self.Logger.exception("{}".format(error))

    # def control(self, uri):
    #     message = Soup.Message.new("POST", uri)
    #     message.request_headers.append('Content-type', 'application/json')
    #     self.session.send_async(message, None, self.on_control_finished, message)
    #
    # def on_control_finished(self, session, result, message):
    #     if message.status_code == Soup.Status.SSL_FAILED:
    #         self.session.props.ssl_strict = False
    #     try:
    #         input_stream = session.send_finish(result)
    #     except GLib.Error:
    #         return False
    #
    #     input_stream.close_async(GLib.PRIORITY_LOW, None, self._control_close_stream, None)
    #
    # def _control_close_stream(self, session, result, data):
    #     try:
    #         session.close_finish(result)
    #     except GLib.Error:
    #         pass
