
import re

import xxhash
import langcodes

import tools.general as utils


class TracksData():
    def __init__(self):
        self._rawMediaTracksData = {}
        self._sources = []

    """
    Public Functions
    """

    ################################################################################################################
    ###### These Function adds every track from bdinfo list of tracks to a dictionary                              #
    #It also adds data about the source of the information, and where to output it                                 #
    ################################################################################################################

    def updateRawTracksDict(self, trackStrs, playlistNum, playlistFile, streams, source, output):
        tracks = []
        for index, currline in enumerate(trackStrs):
            index = index+2
            self._appendTrack(currline, index, tracks, source)
        for track in tracks:
            track["sourceDir"] = source
            track["sourceKey"] = utils.getShowName(source)
        self._expandRawTracksData(
            tracks, playlistNum, playlistFile, streams, source, output)
        self.addSource(source)

    def addSource(self, source):
        self._sources.append(utils.getShowName(source))

    ################################################################################################################
    #   Getter Functions
    ################################################################################################################

    @property
    def rawMediaTracksData(self):
        return self._rawMediaTracksData

    def filterBySource(self, source):
        return self._rawMediaTracksData.get(utils.getShowName(source))

    """
   Private
    """

    ################################################################################################################
    ###### These Functions are used to parse Data from String for the corresponding Track Type i.e Video, Audio,etc#
    ################################################################################################################

    def _videoParser(self, currline):
        tempdict = {}
        bdinfo = re.search(
            "(?:.*?: (.*))", currline).group(1)
        tempdict = self._defaultMediaDict(bdinfo)
        tempdict["type"] = "video"
        return tempdict

    def _audioParser(self, currline):
        tempdict = {}
        lang = self._medialang(currline)
        langcode = self._mediacode(lang)
        bdinfo = list(filter(lambda x: x != None, list(
            re.search("(?:.*?/ )(?:(.*?) \(.*)?(.*)?", currline).groups())))[0]
        tempdict = self._defaultMediaDict(bdinfo, langcode, lang)
        tempdict["type"] = "audio"
        tempdict["auditorydesc"] = False
        tempdict["original"] = False
        tempdict["commentary"] = False

        return tempdict

    def _audioCompatParser(self, currline):
        tempdict = {}
        lang = self._medialang(currline)
        langcode = self._mediacode(lang)
        bdinfo = re.search("(?:.*?)(?:\((.*?)\))", currline)
        if bdinfo == None:
            return
        bdinfo = list(filter(lambda x: x != None, list(bdinfo.groups()
                                                       )))
        if len(bdinfo) == 0:
            return
        bdinfo = bdinfo[0]
        tempdict = self._defaultMediaDict(bdinfo, langcode, lang)
        tempdict["type"] = "audio"
        tempdict["compat"] = True
        tempdict["auditorydesc"] = False
        tempdict["original"] = False
        tempdict["commentary"] = False
        return tempdict

    def _subParser(self, currline):
        tempdict = {}
        lang = self._medialang(currline)
        bdinfo = currline
        langcode = self._mediacode(lang)
        tempdict = self._defaultMediaDict(bdinfo, langcode, lang)
        tempdict["type"] = "subtitle"
        tempdict["sdh"] = False
        tempdict["textdesc"] = False
        tempdict["commentary"] = False
        return tempdict

    # Standard Track Data Helper
    def _defaultMediaDict(self, bdinfo, langcode=None, lang=None):
        tempdict = {}
        tempdict["bdinfo_title"] = bdinfo
        tempdict["langcode"] = langcode
        tempdict["lang"] = lang
        tempdict["compat"] = False
        tempdict["default"] = False
        tempdict["forced"] = False
        tempdict["machine_parse"] = []
        tempdict["length"] = None
        return tempdict

        ################################################################################################################
        ###### These Functions are Used to get the Language/Code of a Track                                            #
        ################################################################################################################

    def _medialang(self, currline):
        return re.search("(?:.*?: )(.*?)(?: /.*)", currline).group(1)

    def _mediacode(self, lang):
        try:
            return langcodes.standardize_tag(langcodes.find(lang))
        except:
            return

        ################################################################################################################
        ###### Adds Track to List                                                                                     #
        ################################################################################################################

    def _appendTrack(self, currline, index, tracks, source):
        tempdict = None
        tempdict2 = None
        match = re.search("([a-z|A-Z]*?):", currline, re.IGNORECASE).group(1)
        if match == "Video":
            tempdict = self._videoParser(currline)
        elif match == "Audio":
            tempdict = self._audioParser(currline)
            tempdict2 = self._audioCompatParser(currline)
        elif match == "Subtitle":
            tempdict = self._subParser(currline)
    # Try to Get Unique Key Values
        tempdict["index"] = index
        value = tempdict["bdinfo_title"] + \
            utils.getShowName(source) + str(tempdict["index"])
        key = xxhash.xxh32_hexdigest(value)
        post = tempdict["langcode"] or "vid"
        tempdict["key"] = f"{key}_{post}"
        tempdict["parent"] = None
        tempdict["child"] = None
        tracks.append(tempdict)
        if tempdict2 != None:
            tempdict2["index"] = index

            # Try to Get Unique Key Values
            value = tempdict2["bdinfo_title"] + \
                utils.getShowName(source) + str(tempdict2["index"])
            key = xxhash.xxh32_hexdigest(value)
            post = tempdict2["langcode"] or "vid"
            tempdict2["key"] = f"{key}_{post}"
            tempdict2["child"] = None
            tempdict2["parent"] = tempdict["bdinfo_title"]
            tempdict["child"] = tempdict2["bdinfo_title"]
            tempdict["parent"] = None
            tracks.append(tempdict2)

    # Primary Key are Basename Source
    # Tracks are Objects
    # Output is a a string
    def _expandRawTracksData(self, tracks, playlistNum, playlistFile, streams, source, output):
        self._rawMediaTracksData[utils.getShowName(source)] = {}
        self._rawMediaTracksData[utils.getShowName(source)]["tracks"] = tracks
        self._rawMediaTracksData[utils.getShowName(
            source)]["outputDir"] = output
        self._rawMediaTracksData[utils.getShowName(
            source)]["sourceDir"] = source
        self._rawMediaTracksData[utils.getShowName(
            source)]["playlistNum"] = playlistNum
        self._rawMediaTracksData[utils.getShowName(
            source)]["playlistFile"] = playlistFile
        self._rawMediaTracksData[utils.getShowName(
            source)]["streamFiles"] = streams
