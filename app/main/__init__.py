import os

from dt_automator import DTAutomator
from dt_automator.sdk.model import SceneModel
from ojoqt import BaseApplication, BaseMainWindow
from ojoqt.dialog import SelectDialog
from ojoqt.helper import TableHelper
from pyadb import Device, PyADB
from pyojo.tools.shell import get_app_shell

from app.config import Config
from app.main.view import MainWindowView


class MainWindow(BaseMainWindow, MainWindowView):
    def __init__(self, app: BaseApplication):
        self._config = Config()
        self._config._config_path = os.path.expanduser('~/.coc_automator.json')
        self._device = None  # type: Device

        super().__init__(app)

        app_shell = get_app_shell()
        self._adb = PyADB('%s/app/res/libs/adb' % app_shell.get_runtime_dir())
        self._dta = DTAutomator()
        self._dta.load('app/res/data.dat')
        if self._config.load():
            self._device = self._adb.devices.get(self._config.device)
            self._dta.set_device(self._device)

    def sync_scenes(self):
        if self._device is not None:
            scenes = self._project.scenes
            data = []
            for k, v in scenes.items():
                v: SceneModel
                data.append([k, len(v.accuracy)])
            TableHelper.sync_data(self.tableWidgetScenes, data)
            TableHelper.auto_inject_columns_width(self.tableWidgetScenes)

    def _callback_select_device_triggered(self, b: bool):
        devices = self._adb.devices
        if len(devices) == 0:
            self._adb.kill_server()
            self._adb.start_server()
        devices = self._adb.devices

        item = SelectDialog.select(
            self, title=self.tr('Select Device'),
            cols_title=[self.tr('Device'), self.tr('State')],
            rows=[(sn, device.state) for sn, device in devices.items()],
            item_keys=['sn', 'state']
        )

        if item is not None:
            self._device = devices[item['sn']]
            self._dta.set_device(self._device)
            self._config.device = item['sn']
            self._config.save()
