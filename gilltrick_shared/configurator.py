import os, json
from backend_shared.logger import colors

class Configurator:
    def __init__(self):
        self.config_path = f"{os.getcwd()}/config/config.json"
        print(self.config_path)
        self.config = None
        self.colors = colors.Colors()

    def load_config(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as fp:
                self.config = json.load(fp)
            return self.config
        except Exception as e:
            print(f"{self.colors.FAIL}Cannot load config file @config/config.json\nError: {e}\n{self.colors.ENDC}")
            exit()