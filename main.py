import json
from flask import Flask, request, redirect, g, render_template
import requests
from urllib.parse import quote
from decouple import config
import matplotlib.pyplot as plt
import statistics

app = Flask(__name__, static_folder = 'D:/Programming Files/SpotifyWrapped/templates')

#  Client Keys
CLIENT_ID = config('CLIENT_ID')
CLIENT_SECRET = config('CLIENT_SECRET')

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "user-top-read"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}


@app.route("/")
def index():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)


@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    # Get user's URI
    profile_response=requests.get(SPOTIFY_API_URL + "/me", headers=authorization_header)
    profile_json=profile_response.json()
    user_uri=(profile_json['uri'])
    print(profile_json["href"])

    #Get user's top tracks
    tracks_response=requests.get(SPOTIFY_API_URL + "/me/top/tracks?time_range=short_term&limit=10", headers=authorization_header)
    tracks_json=tracks_response.json()
    tracks_items=tracks_json['items']
    track_names = []
    track_ids = []
    track_popularities = []
    track_artists = []
    tracklist=[]
    i=0
    while i<len(tracks_items):
        track_names.append(tracks_items[i]['name'])
        track_ids.append(tracks_items[i]['id'])
        track_artists.append(tracks_items[i]['artists'][0]['name'])
        track_popularities.append(tracks_items[i]['popularity'])
        if i==len(tracks_items)-1:
            tracklist.append(str(i+1) + ". " + track_names[i] + " by " + str(track_artists[i]))
        else:
            tracklist.append(str(i+1) + ". " + track_names[i] + " by " + str(track_artists[i]) + "\n" )
        i=i+1
    # print("Your top tracks are: ")
    # print(tracklist)
    average_popularity = statistics.mean(track_popularities)
    # print("The average popularity of your top 10 tracks is " + str(average_popularity) + " out of 100")

    x_pos = [i for i, _ in enumerate(track_names)]
    plt.barh(x_pos, track_popularities, color='green')
    plt.yticks(x_pos, track_names)
    plt.xlim([0, 100])
    plt.savefig(r'D:\Programming Files\SpotifyWrapped\templates\my_plot.png', bbox_inches = 'tight')


    # Combine profile and playlist data to display
    template = render_template("index.html", toptracks="Your top tracks are:", tracklist=tracklist, popularity="The average popularity of your top 10 tracks is " + str(average_popularity) + " out of 100.")
    return template


if __name__ == "__main__":
    app.run(debug=True, port=PORT)