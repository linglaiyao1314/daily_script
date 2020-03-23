import os
import yaml


def reload_settings():
    current_file_path = os.path.abspath(__file__)
    settings_path = os.path.dirname(os.path.dirname(current_file_path))
    with open(os.path.join(settings_path, 'command_settings.yml'), 'r', encoding="utf8") as f:
        settings = yaml.load(f)
    return settings

