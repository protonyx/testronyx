"""
Testronyx Flask app factory
"""

__author__ = 'kkennedy'

import flask
from injector import Module, singleton, provides
from . import api, rpc


class FlaskAppModule(Module):
    @singleton
    @provides(flask.Flask)
    def create_app(self):
        """
        Testronyx Flask App Factory

        :return: flask.Flask
        """
        app = flask.Flask(__name__)

        app.register_blueprint(api.api_blueprint)
        app.register_blueprint(rpc.rpc_blueprint)

        return app





