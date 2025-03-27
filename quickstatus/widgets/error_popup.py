from quickstatus.utils.imports import *

error_list = {
    'one zillion': {'type': 'super_critical',
                    'text': 'THE CAPS LOCK KEY WAS PRESSED'},
    100: {'type': 'critical',
          'text': 'Failed to load config file'},
    101: {'type': 'error',
          'text': 'No widgets are specified in the config file. Add some or obtain a new config file.'}
}

class ErrorPopup(QMessageBox):
    def __init__(self, error, details=None):
        super(ErrorPopup, self).__init__()

        self.error = error
        error = error_list[self.error]

        self.buttonBox = QDialogButtonBox()

        self.setWindowTitle('QuickStatus (Gone Haywire)')

        error_type = error['type']
        if error_type == 'critical':
            self.setIcon(self.Icon.Critical)
        if error_type == 'error':
            self.setIcon(self.Icon.Warning)
        self.setText(f'Error code {self.error}')
        if details is not None: self.setDetailedText(f"{type(details).__name__}: {details}")
        self.setInformativeText(error['text'])

        self.exec()

        if error_type in ['critical', 'error']:
            sys.exit()