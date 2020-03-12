import os

from pyadb import Device, PyADB
from pyojo.tools.shell import get_app_shell

from app import BaseApplication
from app.base import BaseMainWindow
from app.base.dialog import SelectDialog
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
        if self._config.load():
            self._device = self._adb.devices.get(self._config.device)

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
            self._config.device = item['sn']
            self._config.save()
