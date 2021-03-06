import re
import os


import tools.general as utils
from sites.base.siteMuxData import MuxOBj
import mediatools.mkvtoolnix as mkvTool
import mediadata.movieData as movieData


class AnimeBytes(MuxOBj):
    def __init__(self):
        super().__init__()

    def getFileName(self, kind, remuxConfig, movie, group):
        videoCodec = mkvTool.getVideo(
            remuxConfig["Enabled_Tracks"]["Video"], remuxConfig["Tracks_Details"]["Video"])
        mediaType = mkvTool.getMediaType(
            remuxConfig["Enabled_Tracks"]["Video"], remuxConfig["Tracks_Details"]["Video"])
        videoRes = mkvTool.getVideoResolution(
            remuxConfig["Enabled_Tracks"]["Video"], remuxConfig["Tracks_Details"]["Video"])

        audioCodec = mkvTool.getAudio(
            remuxConfig["Enabled_Tracks"]["Audio"], remuxConfig["Tracks_Details"]["Audio"])
        audioChannel = mkvTool.getAudioChannel(
            remuxConfig["Enabled_Tracks"]["Audio"], remuxConfig["Tracks_Details"]["Audio"])

        movieName = movieData.getMovieName(movie)
        movieYear = movieData.getMovieYear(movie)

        season = remuxConfig.get("Season")
        episode = remuxConfig.get("Episode")

        if kind == "Movie":
            fileName = f"{movieName}.{movieYear}.{videoRes}.{mediaType}.REMUX.{videoCodec}.{audioCodec}.{audioChannel}-{group}.mkv"
        else:
            # add episode name
            episodes = movieData.getEpisodes(
                movieData.getByID(movie["imdbID"]), season)
            episodeData = movieData.getEpisodeData(episodes, episode)
            episodeTitle = episodeData["title"]
            fileName = f"{movieName}.{movieYear}.S{season//10}{season%10}E{episode//10}{episode%10}.{episodeTitle}.{videoRes}.{mediaType}.REMUX.{videoCodec}.{audioCodec}.{audioChannel}-{group}.mkv"
        # Normalize FileName
        fileName = re.sub(" +", " ", fileName)
        fileName = re.sub(" ", ".", fileName)
        fileName = re.sub("\.+", ".", fileName)
        fileName = re.sub("[@_!#$%^&*()<>?/\|}{~:]", "", fileName)

        inputs = ["YES", "NO"]
        choice = utils.singleSelectMenu(
            inputs, f"Is this FileName Correct: {fileName}\n")
        while choice != "YES":
            message = "Enter New FileName: "
            utils.textEnter(message, fileName)
            choice = utils.singleSelectMenu(
                inputs, "Is the File Correct Now\n")
        return os.path.abspath(os.path.join(".", fileName))
