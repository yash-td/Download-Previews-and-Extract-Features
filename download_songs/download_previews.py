from tqdm import tqdm
import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from configparser import ConfigParser
import os
from utils import download_songs

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

data = pd.read_csv('big5_mft_tracks.csv')
preview_url = data['preview_url']
track_id = data['track_id']



download_songs(preview_url, track_id)
print('Dataset Downloaded ....')