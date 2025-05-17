import os, datetime
from backend_shared.logger import colors
from backend_shared.utils import inputTranslator

class Logger():
    def __init__(self):
        self.levels = {"error":0, "info":1, "debug":2}
        self.colors = colors.Colors()
        self.colorTranslator = inputTranslator.InputTranslator().ColorTranslator()

    def log(self, level, message):
        """Logs to disk.

        Takes two arguments first the Log-level like ERROR, DEBUG or INFO.
        2nd the message itself.
        Formates a string with a date and writes it to the disc with the level as PREFIX.log
        Creates the file if not not exists otherwise it appends the message to the log file
        """
        message = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} || {message}\n"
        with open(f"{os.getcwd()}/logs/{datetime.datetime.now().strftime('%y-%m-%d')}_{level}.log", "a") as fd:
            fd.writelines(message)
        print(f"[API-{level}] {message}")

    def print(self, color, text):
        print(f"{self.colorTranslator.translate(color)}{text}{self.colorTranslator.translate('ENDC')}")