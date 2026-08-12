from ui.settings_dialog import SettingsDialog


def test_dialog_prefills_existing_creds(app, monkeypatch):
    monkeypatch.setattr("ui.settings_dialog.get_baidu_creds", lambda: ("ak-1", "sk-2"))
    dialog = SettingsDialog()
    assert dialog.api_key_edit.text() == "ak-1"
    assert dialog.secret_key_edit.text() == "sk-2"


def test_save_writes_config_and_creds(app, monkeypatch, tmp_path):
    saved = {}
    monkeypatch.setattr("ui.settings_dialog.get_baidu_creds", lambda: None)
    monkeypatch.setattr("ui.settings_dialog.default_config_path", lambda: str(tmp_path / "config.json"))
    monkeypatch.setattr("ui.settings_dialog.save_config",
                        lambda cfg, path=None: saved.update(cfg))
    monkeypatch.setattr("ui.settings_dialog.save_baidu_creds", lambda a, s: None)
    dialog = SettingsDialog()
    dialog.api_key_edit.setText("ak-new")
    dialog.secret_key_edit.setText("sk-new")
    dialog.hotkey_edit.setText("Ctrl+Shift+X")
    dialog.engine_combo.setCurrentText("baidu")
    dialog.save()
    assert saved["hotkey"] == "Ctrl+Shift+X"
    assert saved["default_engine"] == "baidu"
