import re
import os

from dotenv import load_dotenv
from guessit import guessit
from imdb import Cinemagoer as imdb
from tmdbv3api import TMDb, Find
from InquirerPy import inquirer

import tools.general as utils


load_dotenv()
tmdb = TMDb()
tmdb.api_key = os.environ.get("TMDB") or "e7f961054134e132e994eb5e611e454c"
find = Find()
ia = imdb()


def getMovieName(movie):
    return guessit(movie["title"])["title"]


def getByID(id):
    return ia.get_movie(id)


def getMovieYear(movie):
    return movie["year"]


def matchMovie(sources):
    details = guessit(sources[0])
    title = details.get("title")
    results = ia.search_movie(title)
    if len(results) == 0:
        message =\
            """
        Unable to find movie
        Enter imdb id:
        """
        id = utils.textEnter(message)
        result = ia.get_movie(re.sub("tt", "", id))
    else:
        titles = list(map(lambda x: x["long imdb title"], results))
        titles.insert(0, "None of these Titles Match")
        match = utils.singleSelectMenu(titles, 'What Movie/TV Show')
        if match == "None of these Titles Match":
            message = \
                """
            Unable to find movie ID
            Enter imdb id
            """
            id = None
            try:
                id = utils.textEnter(message)
            except:
                print("id is invalid\n")

            result = ia.get_movie(re.sub("tt", "", id))
        else:
            result = results[titles.index(match)-1]

    ia.update(result, info=['main'])
    return result


def getKind(movie):
    kind = movie["kind"]
    if kind == "Movie" or kind == "tv movie" or kind == "video movie":
        return "Movie"
    else:
        return "tv"


def convertIMDBtoTMDB(id):
    if re.search("tt", id) == None:
        id = f"tt{id}"
    results = find.find_by_imdb_id(id)["movie_results"]
    if len(results) > 0:
        return results[0]["id"]


def getSeason(sources):
    details = guessit(sources[0])
    season = details.get("Season")
    return season


def getTotalEpisodes(episodes):
    return len(episodes.keys())


# def getEpisodes(movie, season, episode):
#     ia.update(movie, 'episodes')
#     episode = movie["episodes"][season][episode]
#     ia.update(episode, info=['main'])
#     return episode

def getEpisodes(movie, season):
    ia.update(movie, 'episodes')
    return movie["episodes"][season]


def getEpisodeData(episodes, num):
    episode = episodes[num]
    ia.update(episode, info=['main'])
    return episode


def getEpisodeTitle(movie, season, episode):
    ia.update(movie, 'episodes')
    episode = movie["episodes"][season][episode]
    ia.update(episode, info=['main'])
    return episode


def getMovieTitle(movie):
    movieName = getMovieName(movie)
    movieYear = getMovieYear(movie)
    return f"{movieName} ({movieYear})"
