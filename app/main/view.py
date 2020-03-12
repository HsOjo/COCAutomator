from ojoqt import BaseView

from app.res.ui.main import Ui_MainWindow


class MainWindowView(Ui_MainWindow, BaseView):
    def callback_init(self):
        pass

    def callback_event_register(self):
        self.actionSelectDevice.triggered.connect(self._callback_select_device_triggered)

    def _callback_select_device_triggered(self, b: bool):
        pass
