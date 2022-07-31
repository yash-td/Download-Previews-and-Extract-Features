import requests
import os
import re
from tqdm import tqdm
from text_unidecode import unidecode
import time
import numpy as np

sleep_min = 1
sleep_max = 3
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)



"""
This functions are used to pre-process artist names and titles
"""


is_not_a_letter_or_number = re.compile('[^a-zA-Z0-9]')

def pre_process_text(text):
    # removes non-ASCII characters
    # see https://pypi.org/project/Unidecode/
    text = unidecode(text)
    text = ' '.join([re.sub(is_not_a_letter_or_number, '', token.lower()) for token in text.split(" ")])
    return text.strip()


"""
In is_same_artist_and_title function I check whether the artist and the title that we found in our query 
are the same ones from our dataset.
"""


def is_same_artist_and_title(query, artist, title):
    is_same_artist = pre_process_text(artist) == pre_process_text(
        query["tracks"]["items"][0]["artists"][0]["name"]
    )
    is_same_title = pre_process_text(title) == pre_process_text(
        query["tracks"]["items"][0]["name"]
    )
    return is_same_artist and is_same_title


"""
In track_preview_available function I am checking that the query returned by spotify's api is not empty 
and if its not I check if the preview url is available.
"""


def track_preview_available(query):
    if query["tracks"]["items"]:
        return bool(query["tracks"]["items"][0]["preview_url"])
    else:
        return False


def download_songs(preview_url, track_id):
    audio_path = "/Users/yash/Desktop/downloaded_songs"  
    if os.path.exists("/yash/ytkd/Desktop/downloaded_songs") is False:
        os.mkdir("/Users/yash/Desktop/downloaded_songs")  
    request_count = 0
    start_time = time.time()
    for i, url in tqdm(enumerate(preview_url)):
        
        file_name = f"{os.path.join(audio_path, track_id[i][:1], track_id[i][:2], track_id[i] + '.mp3')}"

        if not os.path.exists(f"{audio_path}/{track_id[i][:1]}"):
            os.mkdir(f"{audio_path}/{track_id[i][:1]}")

        if not os.path.exists(f"{audio_path}/{track_id[i][:1]}/{track_id[i][:2]}"):
            os.mkdir(f"{audio_path}/{track_id[i][:1]}/{track_id[i][:2]}")

        if not os.path.exists(file_name):
            response = session.get(url, verify=False)
            open(file_name,"wb").write(response.content)

        # request_count+=1

        # if request_count % 300 == 0: # after every 200 requests adding a random sleep time
        #     print(str(request_count) + " records fetched")
        #     time.sleep(np.random.uniform(sleep_min, sleep_max))