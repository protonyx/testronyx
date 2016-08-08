

class EventMediator(object):
    @inject(logger=logging.Logger)
    def __init__(self, logger):
        self.logger = logger

    def publish(self, event):
        pass

    def subscribe(self):
        pass