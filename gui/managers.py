from PyQt5.QtCore import QObject, pyqtSignal


class SignalManager(QObject):
    toggle_process_signal = pyqtSignal(bool)
