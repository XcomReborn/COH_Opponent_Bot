import logging
import re
import datetime

from classes.oppbot_settings import Settings
from functools import partial
from classes.oppbot_ucs import UCS


class ReplayParser:
    "Parses a Company of Heroes 1 replay header."

    def __init__(self, filePath=None, settings=None) -> None:

        self.settings = settings
        if not settings:
            self.settings = Settings()

        self.filePath = filePath

        self.fileVersion = None
        self.chunkyVersion = None
        self.randomStart = None
        self.highResources = None
        self.VPCount = None
        self.matchType = None
        self.localDateString = None
        self.localDate = None
        self.unknownDate = None
        self.replayName = None
        self.gameVersion = None
        self.modName = None
        self.mapName = None
        self.mapNameFull = None
        self.mapDescription = None
        self.mapDescriptionFull = None
        self.mapFileName = None
        self.mapWidth = None
        self.mapHeight = None
        self.playerList = []

        self.success = None

        self.data = None
        self.dataIndex = 0

        if filePath:
            self.load(self.filePath)

    def read_unsigned_long_4_bytes(self) -> int:
        "Reads 4 bytes as an unsigned long int."

        try:
            if self.data:
                fourBytes = bytearray(
                    self.data[self.dataIndex:self.dataIndex+4])
                self.dataIndex += 4
                theInt = int.from_bytes(
                    fourBytes,
                    byteorder='little',
                    signed=False)
                return theInt
        except Exception as e:
            logging.error(str(e))
            logging.error("Failed to read 4 bytes")
            logging.exception("Stack Trace: ")
            self.success = False

    def read_bytes(self, numberOfBytes):
        "reads a number of bytes from the data array"

        try:
            if self.data:
                output = bytearray(
                    self.data[self.dataIndex:self.dataIndex+numberOfBytes])
                self.dataIndex += numberOfBytes
                return output
        except Exception as e:
            logging.error(str(e))
            logging.error("Failed to Read bytes")
            logging.exception("Stack Trace: ")
            self.success = False

    def read_length_string(self):
        "Reads an indexed String."

        try:
            if self.data:
                stringLength = self.read_unsigned_long_4_bytes()
                theString = self.read_2_byte_string(stringLength=stringLength)
                return theString
        except Exception as e:
            logging.error(str(e))
            logging.error("Failed to read a string of specified length")
            logging.exception("Stack Trace: ")
            self.success = False

    def read_2_byte_string(self, stringLength=0) -> str:
        "Reads a 2byte encoded little-endian string of specified length."

        try:
            if self.data:
                theBytes = bytearray(
                    self.data[self.dataIndex:self.dataIndex+(stringLength*2)])
                self.dataIndex += stringLength*2
                theString = theBytes.decode('utf-16le')
                return theString
        except Exception as e:
            logging.error(str(e))
            logging.error("Failed to read a string of specified length")
            logging.exception("Stack Trace: ")
            self.success = False

    def read_length_ASCII_string(self) -> str:
        "Reads ASCII string, the length defined by the first four bytes."

        try:
            if self.data:
                stringLength = self.read_unsigned_long_4_bytes()
                theString = self.read_ASCII_string(stringLength=stringLength)
                return theString
        except Exception as e:
            logging.error(str(e))
            logging.error("Failed to read a string of specified length")
            logging.exception("Stack Trace: ")
            self.success = False

    def read_ASCII_string(self, stringLength=0) -> str:
        "Reads an ASCII string of specfied length."
        try:
            if self.data:
                theBytes = bytearray(
                    self.data[self.dataIndex:self.dataIndex+stringLength])
                theString = theBytes.decode('ascii')
                self.dataIndex += stringLength
                return theString
        except UnicodeDecodeError:
            # if unable to get an ASCII string try for a ucs2 string.
            theString = self.read_2_byte_string(stringLength=stringLength)
            return theString


    def read_null_terminated_2_byte_string(self) -> str:
        "Reads a Utf-16 little endian character string."

        try:
            if self.data:
                characters = ""
                for character in iter(
                        partial(self.read_bytes, 2),
                        bytearray(b"\x00\x00")
                ):
                    characters += bytearray(character).decode('utf-16le')
                return characters
        except Exception as e:
            logging.error(str(e))
            logging.error("Failed to read a string of specified length")
            logging.exception("Stack Trace: ")
            self.success = False

    def read_null_terminated_ASCII_string(self) -> str:
        "Reads a byte array until the first NULL and converts to a string."

        try:
            if self.data:
                characters = ""
                for character in iter(
                    partial(self.read_bytes, 1),
                    bytearray(b"\x00")
                ):
                    characters += bytearray(character).decode('ascii')
                return characters
        except Exception as e:
            logging.error(str(e))
            logging.error("Failed to read a string of specified length")
            logging.exception("Stack Trace: ")
            self.success = False

    def seek(self, numberOfBytes, relative=0):
        "Moves the file index a number of bytes forward or backward"

        try:
            numberOfBytes = int(numberOfBytes)
            relative = int(relative)
            if relative == 0:
                assert (0 <= numberOfBytes <= len(self.data))
                self.dataIndex = numberOfBytes
            if relative == 1:
                assert (
                    0 <= (numberOfBytes+self.dataIndex) <= len(self.data))
                self.dataIndex += numberOfBytes
            if relative == 2:
                assert (
                    0 <= (len(self.data) - numberOfBytes) <= len(self.data))
                self.dataIndex = len(self.data) - numberOfBytes
        except Exception as e:
            logging.error(str(e))
            logging.error("Failed move file Index")
            logging.exception("Stack Trace: ")

    def load(self, filePath=""):
        with open(filePath, "rb") as fileHandle:
            self.data = fileHandle.read()
        self.process_data()

    def process_data(self) -> bool:
        "Processes replay byte data."

        # Set return flag
        self.success = True

        # Process the file Header
        self.fileVersion = self.read_unsigned_long_4_bytes()  # int (8)

        self.read_ASCII_string(stringLength=8)  # COH__REC

        self.localDateString = self.read_null_terminated_2_byte_string()

        # Parse localDateString as a datetime object
        self.localDate = self.decode_date(self.localDateString)

        self.seek(76, 0)

        firstRelicChunkyAddress = self.dataIndex
        
        self.read_ASCII_string(stringLength=12)  # relicChunky

        self.read_unsigned_long_4_bytes()  # unknown

        self.chunkyVersion = self.read_unsigned_long_4_bytes()  # 3

        self.read_unsigned_long_4_bytes()  # unknown

        self.chunkyHeaderLength = self.read_unsigned_long_4_bytes()

        self.seek(-28, 1)  # sets file pointer back to start of relic chunky
        self.seek(self.chunkyHeaderLength, 1)  # seeks to begining of FOLDPOST

        self.seek(firstRelicChunkyAddress, 0)
        self.seek(96, 1)
        # move pointer to the position of the second relic chunky

        secondRelicChunkyAddress = self.dataIndex

        self.read_ASCII_string(stringLength=12)  # relicChunky

        self.read_unsigned_long_4_bytes()  # unknown
        self.read_unsigned_long_4_bytes()  # chunkyVersion 3
        self.read_unsigned_long_4_bytes()  # unknown
        chunkLength = self.read_unsigned_long_4_bytes()

        self.seek(secondRelicChunkyAddress, 0)
        self.seek(chunkLength, 1)  # seek to position of first viable chunk

        self.parse_chunk(0)
        self.parse_chunk(0)

        return self.success

    def resolve_mapNameFull_And_mapDescription_From_UCS(self):
        # mapNameFull and mapDescriptionFull will be None
        # until resolved this takes time because file reading
        # so moved to separate function call
        # get mapNameFull and mapDescriptionFull from ucs file
        ucs = UCS(settings=self.settings)
        self.mapNameFull = ucs.compare_UCS(self.mapName)
        self.mapDescriptionFull = ucs.compare_UCS(self.mapDescription)

    def parse_chunk(self, level):

        chunkType = self.read_ASCII_string(stringLength=8)
        # Reads FOLDFOLD, FOLDDATA, DATASDSC, DATAINFO etc

        chunkVersion = self.read_unsigned_long_4_bytes()

        chunkLength = self.read_unsigned_long_4_bytes()

        chunkNameLength = self.read_unsigned_long_4_bytes()

        self.seek(8, 1)

        if chunkNameLength > 0:
            self.read_ASCII_string(stringLength=chunkNameLength)  # chunkName

        chunkStart = self.dataIndex

        # Here we start a recusive loop
        if chunkType:
            if (chunkType.startswith("FOLD")):

                while (self.dataIndex < (chunkStart + chunkLength)):
                    self.parse_chunk(level=level+1)

        if (chunkType == "DATASDSC") and (int(chunkVersion) == 2004):

            self.read_unsigned_long_4_bytes()  # unknown
            self.unknownDate = self.read_length_string()
            self.read_unsigned_long_4_bytes()  # unknown
            self.read_unsigned_long_4_bytes()  # unknown
            self.read_unsigned_long_4_bytes()  # unknown
            self.modName = self.read_length_ASCII_string()
            self.mapFileName = self.read_length_ASCII_string()
            self.read_unsigned_long_4_bytes()  # unknown
            self.read_unsigned_long_4_bytes()  # unknown
            self.read_unsigned_long_4_bytes()  # unknown
            self.read_unsigned_long_4_bytes()  # unknown
            self.read_unsigned_long_4_bytes()  # unknown
            self.mapName = self.read_length_string()

            value = self.read_unsigned_long_4_bytes()
            if value != 0:  # test to see if data is replicated or not
                self.read_2_byte_string(value)  # unknown
            self.mapDescription = self.read_length_string()
            self.read_unsigned_long_4_bytes()  # unknown
            self.mapWidth = self.read_unsigned_long_4_bytes()
            self.mapHeight = self.read_unsigned_long_4_bytes()
            self.read_unsigned_long_4_bytes()  # unknown
            self.read_unsigned_long_4_bytes()  # unknown
            self.read_unsigned_long_4_bytes()  # unknown

        if (chunkType == "DATABASE") and (int(chunkVersion == 11)):

            self.seek(16, 1)

            self.randomStart = True
            self.randomStart = not (self.read_unsigned_long_4_bytes() == 0)
            #  0 is fixed 1 is random

            self.read_unsigned_long_4_bytes()  # COLS

            self.highResources = (self.read_unsigned_long_4_bytes() == 1)

            self.read_unsigned_long_4_bytes()  # TSSR

            self.VPCount = 250 * (1 << (int)(
                self.read_unsigned_long_4_bytes()))

            self.seek(5, 1)

            self.replayName = self.read_length_string()

            self.seek(8, 1)

            self.VPGame = (self.read_unsigned_long_4_bytes() == 0x603872a3)

            self.seek(23, 1)

            self.read_length_ASCII_string() # gameminorversion

            self.seek(4, 1)

            self.read_length_ASCII_string() # gamemajorversion

            self.seek(8, 1)
            # matchname
            if (self.read_unsigned_long_4_bytes() == 2):
                self.read_length_ASCII_string() # gameversion
                self.gameVersion = self.read_length_ASCII_string()
            self.read_length_ASCII_string()
            # cant find in korean replay
            self.matchType = self.read_length_ASCII_string()
            # korean 2v2 contains a long 'nonsense' string.
            if "\uc0de\u0bad\u0101\u4204\u4cc5\u0103\u1000" in self.matchType:
                self.matchType = "automatch"

        if (chunkType == "DATAINFO") and (chunkVersion == 6):

            userName = self.read_length_string()
            self.read_unsigned_long_4_bytes()
            self.read_unsigned_long_4_bytes()
            faction = self.read_length_ASCII_string()
            self.read_unsigned_long_4_bytes()
            self.read_unsigned_long_4_bytes()

            self.playerList.append({'name': userName, 'faction': faction})

        self.seek(chunkStart + chunkLength, 0)

    def decode_date(self, timeString) -> datetime:
        "Processes the date string."

        # 24hr: DD-MM-YYYY HH:mm
        reEuro = re.compile(r"(\d\d).(\d\d).(\d\d\d\d)\s(\d\d).(\d\d)")
        match = re.match(reEuro, timeString)
        if match:
            logging.info("Euro String")
            logging.info(match.groups())
            try:
                day = int(match.group(1))
                month = int(match.group(2))
                year = int(match.group(3))
                hour = int(match.group(4))
                minute = int(match.group(5))
                return datetime.datetime(
                    year=year,
                    month=month,
                    day=day,
                    hour=hour,
                    minute=minute
                )
            except Exception as e:
                logging.error(str(e))
                logging.exception("Exception : ")

        # 12hr: MM/DD/YYYY hh:mm XM *numbers are not 0-padded
        reUS = re.compile(
            r"(\d{1,2}).(\d{1,2}).(\d\d\d\d)\s(\d{1,2}).(\d{1,2}).*?(\w)M"
            )
        match = re.match(reUS, timeString)
        if match:
            logging.info("US Date String")
            logging.info(match.groups())
            try:
                day = int(match.group(2))
                month = int(match.group(1))
                year = int(match.group(3))
                hour = int(match.group(4))
                minute = int(match.group(5))
                meridiem = str(match.group(6))
                if "p" in meridiem.lower():
                    hour = hour + 12
                return datetime.datetime(
                    year=year,
                    month=month,
                    day=day,
                    hour=hour,
                    minute=minute
                )
            except Exception as e:
                logging.error(str(e))
                logging.exception("Exception : ")

        # YYYY/MM/DD HH:MM
        reAsian = re.compile(r"(\d\d\d\d).(\d\d).(\d\d)\s([^\u0000-\u007F]+)\s(\d?\d).(\d\d)")
        # korean AM/PM 오후 means PM
        match = re.match(
            reAsian,
            timeString
        )
        if match:
            logging.info("Asian Date String")
            logging.info(match.groups())
            try:
                day = int(match.group(3))
                month = int(match.group(2))
                year = int(match.group(1))
                hour = int(match.group(5))
                minute = int(match.group(6))
                meridiem = match.group(4)
                # korean pm
                if meridiem == "오후":
                     hour = hour + 12
                date_time = datetime.datetime(
                    year=year,
                    month=month,
                    day=day,
                    hour=hour,
                    minute=minute
                )
                return date_time
            except Exception as e:
                logging.error(str(e))
                logging.exception("Exception : ")

    def __str__(self) -> str:
        output = "Data:\n"
        output += "fileVersion : {}\n".format(self.fileVersion)
        output += "chunkyVersion : {}\n".format(self.chunkyVersion)
        output += "randomStart : {}\n".format(self.randomStart)
        output += "highResources : {}\n".format(self.highResources)
        output += "VPCount : {}\n".format(self.VPCount)
        output += "matchType : {}\n".format(self.matchType)
        output += "localDateString : {}\n".format(self.localDateString)
        output += "localDate : {}\n".format(self.localDate)
        output += "unknownDate : {}\n".format(self.unknownDate)
        output += "replayName : {}\n".format(self.replayName)
        output += "gameVersion : {}\n".format(self.gameVersion)
        output += "modName : {}\n".format(self.modName)
        output += "mapName : {}\n".format(self.mapName)
        output += "mapNameFull : {}\n".format(self.mapNameFull)
        output += "mapDescription : {}\n".format(self.mapDescription)
        output += "mapDescriptionFull : {}\n".format(self.mapDescriptionFull)
        output += "mapFileName : {}\n".format(self.mapFileName)
        output += "mapWidth : {}\n".format(self.mapWidth)
        output += "mapHeight : {}\n".format(self.mapHeight)
        output += "playerList Size : {}\n".format(len(self.playerList))
        output += "playerList : {}\n".format(self.playerList)
        return output
