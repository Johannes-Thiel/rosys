import abc
from typing import Optional

from rosys import persistence

from ..event import Event
from ..runtime import runtime
from ..world import Camera, Image


class CameraProvider(abc.ABC):

    CAMERA_ADDED = Event()
    '''a new camera has been added (argument: camera)'''
    CAMERA_REMOVED = Event()
    '''a camera has been removed (argument: camera id)'''
    NEW_IMAGE = Event()
    '''an new image is available (argument: image)'''

    def __init__(self) -> None:
        self.needs_backup: bool = False
        persistence.register(self)

    @property
    @abc.abstractmethod
    def cameras(self) -> dict[str, Camera]:
        return {}

    @property
    def images(self) -> list[Image]:
        return sorted((i for c in self.cameras.values() for i in c.images), key=lambda i: i.time)

    def add_camera(self, camera: Camera) -> None:
        self.cameras[camera.id] = camera
        self.CAMERA_ADDED.emit(camera)
        self.needs_backup = True

    def remove_camera(self, camera_id: str) -> None:
        del self.cameras[camera_id]
        self.CAMERA_REMOVED.emit(camera_id)
        self.needs_backup = True

    def remove_all_cameras(self) -> None:
        [self.remove_camera(camera_id) for camera_id in list(self.cameras)]

    def remove_calibration(self, camera_id: str) -> None:
        self.cameras[camera_id].calibration = None
        self.needs_backup = True

    def remove_all_calibrations(self) -> None:
        [self.remove_calibration(camera_id) for camera_id in self.cameras]

    def add_image(self, camera: Camera, image: Image) -> None:
        camera.images.append(image)
        self.NEW_IMAGE.emit(image)

    def prune_images(self, max_age_seconds: Optional[float] = None):
        for camera in self.cameras.values():
            if max_age_seconds is None:
                camera.images.clear()
            else:
                while camera.images and camera.images[0].time < runtime.time - max_age_seconds:
                    del camera.images[0]