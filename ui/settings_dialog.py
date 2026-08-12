from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QFormLayout,
                               QLineEdit)

from core.config import load_config, save_config, default_config_path
from security.creds import (save_baidu_creds, get_baidu_creds, delete_baidu_creds)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        config = load_config()

        form = QFormLayout(self)
        self.hotkey_edit = QLineEdit(config.get("hotkey", "Ctrl+Alt+A"))
        self.engine_combo = QComboBox()
        self.engine_combo.addItems(["rapid", "baidu"])
        self.engine_combo.setCurrentText(config.get("default_engine", "rapid"))
        self.api_key_edit = QLineEdit()
        self.secret_key_edit = QLineEdit()
        self.secret_key_edit.setEchoMode(QLineEdit.Password)
        creds = get_baidu_creds()
        if creds:
            self.api_key_edit.setText(creds[0])
            self.secret_key_edit.setText(creds[1])

        form.addRow("全局热键", self.hotkey_edit)
        form.addRow("默认引擎", self.engine_combo)
        form.addRow("百度 API Key", self.api_key_edit)
        form.addRow("百度 Secret Key", self.secret_key_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def save(self):
        config = load_config()
        config["hotkey"] = self.hotkey_edit.text().strip() or "Ctrl+Alt+A"
        config["default_engine"] = self.engine_combo.currentText()
        save_config(config, default_config_path())

        if self.api_key_edit.text().strip() and self.secret_key_edit.text().strip():
            save_baidu_creds(self.api_key_edit.text().strip(), self.secret_key_edit.text().strip())
        elif not self.api_key_edit.text().strip():
            delete_baidu_creds()
        self.accept()
