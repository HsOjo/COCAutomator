from dt_automator import DTAutomator

from app.config import Config


class COCAutomator(DTAutomator):
    def __init__(self, event):
        super().__init__()
        self._event = event

    @property
    def config(self) -> Config:
        return self._event['config']()

    def callback_init(self):
        device = self.device
        package = self.config.app_package

        device.app.force_stop(package)
        device.app.start_by_package(package)

    def callback_update(self):
        scene = self.compare_scenes()
        print(scene)

    def callback_destroy(self):
        device = self.device
        package = self.config.app_package
        device.app.force_stop(package)

    def callback_screen_update(self, img_data: bytes):
        self._event['set_preview'](img_data)

    def callback_scenes_update(self, most_acc_scene):
        data = []
        for scene in self.scenes():
            data.append([scene.name, scene.accuracy])
        self._event['refresh_scenes'](data)
