from tqdm import tqdm
import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from configparser import ConfigParser
import os

from utils import pre_process_text, is_same_artist_and_title, track_preview_available

configur = ConfigParser()
configur.read("config.ini")
client_id = configur["main"]["client_id"]
client_secret = configur["main"]["client_secret"]
client_credentials_manager = SpotifyClientCredentials(
    client_id=client_id, client_secret=client_secret
)
sp = spotipy.Spotify(
    client_credentials_manager=client_credentials_manager
)  # sp is the instance of the spotipy api
sleep_min = 1
sleep_max = 3

# Load lyrics dataset
lyrics_df = pd.read_csv(
    "LY_Artist_lyrics_genre_data_from_big5_mft_users_likes_final.csv"
)
lyrics_df = lyrics_df[lyrics_df["lang_detect_spacy"] == "en"]
artists = list(lyrics_df["Artist"])
titles = list(lyrics_df["title"])

# Load already scraped dataset
if os.path.exists("tracks.csv"):
    tracks_df = pd.read_csv("tracks.csv")
else:
    tracks_df = pd.DataFrame()

start_from_here = tracks_df.shape[0]

artists_clean = []
titles_clean = []
for artist, title in zip(artists, titles):
    artists_clean.append(pre_process_text(artist))
    titles_clean.append(pre_process_text(title))

data = []
request_count = 0
for artist_name, song_title in tqdm(
    list(zip(artists_clean, titles_clean))[start_from_here:]
):
    search = f"artist:{artist_name} track:{song_title}"
    query = sp.search(search, type="track")

    # in the below line of code I am checking that the query returned by spotify's api is not empty and if it's
    # not, I check if the preview url is available, and even further I check a third condition whether the artist
    # that we found in our query is the same from our dataset.

    if track_preview_available(query) and is_same_artist_and_title(
        query, artist_name, song_title
    ):

        data.append(
            {
                "artist_name": query["tracks"]["items"][0]["artists"][0][
                    "name"
                ],  # saving the spotify version
                "song_title": query["tracks"]["items"][0][
                    "name"
                ],  # instead of that from the lyrics_df
                "preview_url": query["tracks"]["items"][0]["preview_url"],
                "track_id": query["tracks"]["items"][0]["id"],
                "artist_id": query["tracks"]["items"][0]["artists"][0]["id"],
                "track_popularity": query["tracks"]["items"][0]["popularity"],
            }
        )
    else:
        data.append(
            {
                "artist_name": None,
                "song_title": None,
                "preview_url": None,
                "track_id": None,
                "artist_id": None,
                "track_popularity": None,
            }
        )

    request_count += 1
    if request_count % 1000 == 0:
        tracks_df = pd.concat([tracks_df, pd.DataFrame(data)], axis=0)
        tracks_df.to_csv("tracks.csv")
        data = []

tracks_df = pd.concat([tracks_df, pd.DataFrame(data)], axis=0)
tracks_df.to_csv("tracks.csv")
