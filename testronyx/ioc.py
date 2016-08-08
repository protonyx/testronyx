import logging
from injector import Module, Injector, provides


class LoggingModule(Module):
    def configure(self, binder):
        pass

    @provides(logging.Logger)
    def provide_logger(self):
        logger = logging.getLogger('testronyx')
        return logger

ioc = Injector([LoggingModule])

import app

ioc.binder.install(app.FlaskAppModule)
