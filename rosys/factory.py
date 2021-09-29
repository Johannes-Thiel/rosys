import os
from rosys.world.world import World
from .actors.esp import Esp
from .actors.serial_esp import SerialEsp
from .actors.mocked_esp import MockedEsp
from .actors.web_esp import WebEsp
import logging

log = logging.getLogger(__name__)


def create_esp(world: World) -> Esp:
    try:
        return SerialEsp()
    except:
        pass
    try:
        return WebEsp()
    except:
        log.exception('could not create web esp')
        pass
    return MockedEsp(world)