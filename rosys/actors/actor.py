import logging


class Actor:
    interval: float = None

    def __init__(self) -> None:
        name = __name__[:-5] + self.__class__.__name__
        self.log = logging.getLogger(name)

    async def step(self):
        pass

    async def tear_down(self):
        pass

    def __str__(self) -> str:
        return type(self).__name__
