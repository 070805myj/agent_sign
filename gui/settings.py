import json
import os
import sys

DEFAULT_SETTINGS = {
    "language": "en",
    "font_size": 16,
    "chart_output_dir": "",
    "folder_permissions": {},
}

SETTINGS_FILE = os.path.join(
    os.path.expanduser("~"), ".jsp_gui_settings.json"
)


class Settings:
    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self._load()

    def _load(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.settings.update(saved)
            except (json.JSONDecodeError, IOError):
                pass

    def _save(self):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except IOError:
            pass

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self._save()

    def get_language(self):
        return self.settings.get("language", "en")

    def set_language(self, lang):
        self.set("language", lang)

    def get_font_size(self):
        return self.settings.get("font_size", 16)

    def set_font_size(self, size):
        self.set("font_size", size)

    def get_chart_output_dir(self):
        return self.settings.get("chart_output_dir", "")

    def set_chart_output_dir(self, path):
        self.set("chart_output_dir", path)

    def check_folder_permission(self, folder_path):
        normalized_path = os.path.normpath(folder_path)
        permissions = self.settings.get("folder_permissions", {})
        return permissions.get(normalized_path, "never")

    def grant_folder_permission(self, folder_path, always=False):
        normalized_path = os.path.normpath(folder_path)
        permissions = self.settings.get("folder_permissions", {})
        permissions[normalized_path] = "always" if always else "once"
        self.set("folder_permissions", permissions)

    def reset_folder_permission(self, folder_path):
        normalized_path = os.path.normpath(folder_path)
        permissions = self.settings.get("folder_permissions", {})
        if normalized_path in permissions:
            del permissions[normalized_path]
            self.set("folder_permissions", permissions)

    def can_access_folder(self, folder_path):
        normalized_path = os.path.normpath(folder_path)
        permissions = self.settings.get("folder_permissions", {})
        status = permissions.get(normalized_path, "never")
        if status == "always":
            return True
        elif status == "once":
            del permissions[normalized_path]
            self.set("folder_permissions", permissions)
            return True
        return False
