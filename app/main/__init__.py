import os

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from dt_automator.sdk.model import SceneModel
from ojoqt import BaseApplication, BaseMainWindow, try_exec
from ojoqt.dialog import SelectDialog, FormDialog
from ojoqt.dialog.form.field import StringField, SelectField
from ojoqt.helper import TableHelper
from pyadb import Device, PyADB
from pyojo.tools.shell import get_app_shell
from pyojo.utils import object_convert

from app.config import Config
from app.main.coc_automator import COCAutomator
from app.main.view import MainWindowView
from app.res import Const


class MainWindow(BaseMainWindow, MainWindowView):
    signal_set_preview = pyqtSignal(bytes)
    signal_refresh_scene = pyqtSignal(list)

    def __init__(self, app: BaseApplication):
        self._config = Config()
        self._config._config_path = os.path.expanduser('~/.coc_automator.json')
        self._device = None  # type: Device

        self._event = dict(
            config=lambda: self._config,
            set_preview=lambda: self.signal_set_preview,
            refresh_scenes=lambda: self.signal_refresh_scene,
        )

        super().__init__(app)

        app_shell = get_app_shell()
        self._adb = PyADB('%s/app/res/libs/adb' % app_shell.get_runtime_dir())
        self._automator = COCAutomator(self._event)
        self._automator.load('app/res/data.dat')

        self.signal_set_preview.connect(self.set_preview)
        self.signal_refresh_scene.connect(self.refresh_scenes)

        if self._config.load():
            devices = self._adb.devices
            if len(devices) == 0:
                self._adb.kill_server()
                self._adb.start_server()
                devices = self._adb.devices
            self._device = devices.get(self._config.device)
            self._automator.set_device(self._device)

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
            self._automator.set_device(self._device)
            self._config.device = item['sn']
            self._config.save()

    def _callback_settings_triggered(self, b: bool):
        data = FormDialog.input([
            StringField('device', self._config.device, self.tr('Device')),
            SelectField('app_package', Const.dta_app_packages, self._config.app_package, self.tr('App Package')),
        ])
        if data is not None:
            object_convert.dict_to_object(data, self._config, False)
            self._config.save()

    @try_exec(show=True, info_only=True)
    def _callback_run_triggered(self, b: bool):
        package = self._config.app_package
        if package != '':
            self._device.app.start_by_package(package)
        else:
            raise Exception(self.tr('App Package is empty!'))

    def _callback_kill_triggered(self, b: bool):
        package = self._config.app_package
        if package != '':
            self._device.app.force_stop(package)

    def _callback_restart_triggered(self, b: bool):
        self._callback_kill_triggered(b)
        self._callback_run_triggered(b)

    def _callback_play_triggered(self, b: bool):
        self._automator.play()

    def _callback_pause_triggered(self, b: bool):
        self._automator.pause()

    def _callback_stop_triggered(self, b: bool):
        self._automator.stop()

    def _callback_scale_changed(self, v: int):
        self.refresh_preview_size()

    def refresh_preview_size(self):
        pixmap = self.labelPreview.pixmap()
        if pixmap is not None:
            size = pixmap.size()
            scale = self.verticalSliderScale.value() / self.verticalSliderScale.maximum()
            size.setWidth(int(size.width() * scale))
            size.setHeight(int(size.height() * scale))
            self.labelPreview.setMinimumSize(size)
            self.labelPreview.setMaximumSize(size)

    def set_preview(self, img_data: bytes):
        pixmap = QPixmap()
        pixmap.loadFromData(img_data)
        self.labelPreview.setPixmap(pixmap)
        self.refresh_preview_size()

    def refresh_scenes(self, data):
        mi = -1
        mv = 0
        for i, (k, v) in enumerate(data):
            if v > mv:
                mi, mv = i, v
            data[i] = [k, '%.6f' % v]

        TableHelper.sync_data(self.tableWidgetScenes, data)
        TableHelper.auto_inject_columns_width(self.tableWidgetScenes)
        self.tableWidgetScenes.selectRow(mi)
        self.app.processEvents()

    def closeEvent(self, *args):
        self._automator.stop()
        self._automator.destroy()
        return super().closeEvent(*args)
