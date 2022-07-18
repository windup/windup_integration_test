import sentaku


class Implementation(object):

    navigator = None

    def __init__(self, owner):
        self.owner = owner

    @property
    def application(self):
        return self.owner


class MTAImplementationContext(sentaku.ImplementationContext):
    """Our context for Sentaku"""

    pass
