import threading
import socket
import logging
from injector import Module, Injector, inject, singleton
import flask

import app
import version


@singleton
class TestronyxAgent(object):
    """
    Agent class for Testronyx
    """
    SERVER_PORT = 6780
    ZMQ_PORT = 6781

    @inject(logger=logging.Logger, flask_app=flask.Flask)
    def __init__(self, logger, flask_app):
        self.logger = logger

        self.flask_app = flask_app
        self.flask_app.config['TSX_AGENT'] = self

        self.server_port = self.SERVER_PORT

    def start(self, new_thread=True):
        """
        Start the API/RPC Server and Event publisher. If `new_thread` is True, the server will be started in a new
        thread in a non-blocking fashion.

        If a server is already running, it will be stopped and then restarted.

        :returns: True if successful, False otherwise
        :rtype: bool
        """
        SERVER_THREAD_NAME = 'Testronyx-Agent'

        # Clean out old server, if any exists
        threads = [th.name for th in threading.enumerate()]
        if SERVER_THREAD_NAME in threads:
            self.stop()

        try:
            # Server start command
            from werkzeug.serving import run_simple

            def start_flask_app():
                return run_simple(
                    hostname=self.get_hostname(),
                    port=self.server_port,
                    application=self._flask_app,
                    threaded=True,
                    use_debugger=True
                )

            if new_thread:
                server_thread = threading.Thread(name=SERVER_THREAD_NAME, target=start_flask_app)
                server_thread.setDaemon(True)
                server_thread.start()

                return True

            else:
                start_flask_app()

        except:
            self.logger.exception("Exception during server start")
            self.stop()

    def stop(self):
        """
        Stop the Server
        """
        # Shutdown server
        try:
            # Must use the REST API to shutdown
            import urllib2
            url = 'http://{0}:{1}/api/shutdown'.format(self.get_hostname(), self.server_port)
            resp = urllib2.Request(url)
            handler = urllib2.urlopen(resp, timeout=0.5)

            if handler.code == 200:
                self.logger.debug('Server stopped')
            else:
                self.logger.error('Server stop returned code: %d', handler.code)

        except:
            pass

    @staticmethod
    def get_version():
        return version.ver_full

    @staticmethod
    def get_hostname():
        """
        Get the local hostname

        :rtype:                 str
        """
        return socket.gethostname()

    def rpc_register(self, name, instance):
        pass

    def rpc_get(self, name):
        pass