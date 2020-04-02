from ojoqt import BaseView

from app.res.ui.main import Ui_MainWindow


class MainWindowView(Ui_MainWindow, BaseView):
    def callback_init(self):
        pass

    def callback_event_register(self):
        self.actionSelectDevice.triggered.connect(self._callback_select_device_triggered)
        self.actionRun.triggered.connect(self._callback_run_triggered)
        self.actionKill.triggered.connect(self._callback_kill_triggered)
        self.actionRestart.triggered.connect(self._callback_restart_triggered)
        self.actionPlay.triggered.connect(self._callback_play_triggered)
        self.actionPause.triggered.connect(self._callback_pause_triggered)
        self.actionStop.triggered.connect(self._callback_stop_triggered)
        self.actionSettings.triggered.connect(self._callback_settings_triggered)
        self.verticalSliderScale.valueChanged.connect(self._callback_scale_changed)

    def _callback_select_device_triggered(self, b: bool):
        pass

    def _callback_run_triggered(self, b: bool):
        pass

    def _callback_kill_triggered(self, b: bool):
        pass

    def _callback_restart_triggered(self, b: bool):
        self._callback_kill_triggered(b)
        self._callback_run_triggered(b)

    def _callback_play_triggered(self, b: bool):
        pass

    def _callback_pause_triggered(self, b: bool):
        pass

    def _callback_stop_triggered(self, b: bool):
        pass

    def _callback_settings_triggered(self, b: bool):
        pass

    def _callback_scale_changed(self, v: int):
        pass
