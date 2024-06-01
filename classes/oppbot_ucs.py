import logging
import os

from classes.oppbot_settings import Settings


class UCS:
    "Processes language UCS file strings and the in game symbolic aliases."

    def __init__(self, ucsPath=None, settings=None) -> None:

        self.settings = settings
        if not settings:
            self.settings = Settings()

        self.ucsPath = ucsPath
        if not ucsPath:
            self.ucsPath = self.settings.data.get('cohUCSPath')

    def compare_UCS(self, compareString) -> str:
        try:
            if compareString:
                if (os.path.isfile(self.ucsPath)):
                    with open(self.ucsPath, 'r',  encoding='utf16') as f:
                        for line in f:
                            if len(line.split('\t')) > 1:
                                firstString = str(line.split('\t')[0])
                                cs = str(compareString[1:].strip())
                                if cs == str(firstString):
                                    return " ".join(line.split()[1:])
        except Exception as e:
            logging.error(str(e))
            logging.exception("Exception : ")
