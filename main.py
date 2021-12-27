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
    average_popularity_tracks = statistics.mean(track_popularities)
    x_pos_tracks = [i for i, _ in enumerate(track_names)]
    plt.barh(x_pos_tracks, track_popularities, color='green')
    plt.yticks(x_pos_tracks, track_names)
    plt.xlim([0, 100])
    plt.savefig(r'D:\Programming Files\SpotifyWrapped\templates\tracks_plot.png', bbox_inches = 'tight')

    #Get user's top artists
    artists_response=requests.get(SPOTIFY_API_URL + "/me/top/artists?time_range=short_term&limit=10", headers=authorization_header)
    artists_json=artists_response.json()
    artists_items=artists_json['items']
    artist_names=[]
    artist_ids=[]
    artist_popularities=[]
    artist_list=[]
    i=0
    while i<len(artists_items):
        artist_names.append(artists_items[i]['name'])
        artist_ids.append(artists_items[i]['id'])
        artist_popularities.append(artists_items[i]['popularity'])
        if i==len(artists_items)-1:
            artist_list.append(str(i+1) + ". " + str(artist_names[i]))
        else:
            artist_list.append(str(i+1) + ". " + str(artist_names[i]) + "\n" )
        i=i+1
    average_popularity_artists = statistics.mean(artist_popularities)
    x_pos_artists = [i for i, _ in enumerate(track_names)]
    plt.barh(x_pos_artists, artist_popularities, color='green')
    plt.yticks(x_pos_artists, artist_names)
    plt.xlim([0, 100])
    plt.savefig(r'D:\Programming Files\SpotifyWrapped\templates\artists_plot.png', bbox_inches = 'tight')

    #Find average metrics of top 10 tracks
    ids = ""
    i=0
    while i<len(track_ids):
        ids+=track_ids[i] + ","
        i=i+1
    metrics_response = requests.get(SPOTIFY_API_URL + "/audio-features?ids="+ids, headers=authorization_header)
    metrics_json = metrics_response.json()
    metrics_audiofeatures = metrics_json['audio_features']

    danceability = []
    energy = []
    loudness = []
    acousticness= []
    instrumentalness = []
    liveness = []
    valence = []
    tempo = []

    i=0
    while i<len(metrics_audiofeatures):
        danceability.append(metrics_audiofeatures[i]['danceability'])
        energy.append(metrics_audiofeatures[i]['energy'])
        loudness.append(metrics_audiofeatures[i]['loudness'])
        acousticness.append(metrics_audiofeatures[i]['acousticness'])
        instrumentalness.append(metrics_audiofeatures[i]['instrumentalness'])
        liveness.append(metrics_audiofeatures[i]['liveness'])
        valence.append(metrics_audiofeatures[i]['valence'])
        tempo.append(metrics_audiofeatures[i]['tempo'])
        i=i+1
    
    average_danceability = round(statistics.mean(danceability),2)
    average_energy = round(statistics.mean(energy),2)
    average_loudness = round(statistics.mean(loudness),2)
    average_acousticness = round(statistics.mean(acousticness),2)
    average_instrumentalness = round(statistics.mean(instrumentalness),2)
    average_liveness = round(statistics.mean(liveness),2)
    average_valence = round(statistics.mean(valence),2)
    average_tempo = round(statistics.mean(tempo),2)

    tracks_popularity_string = "The average popularity of your top 10 tracks is " + str(average_popularity_tracks) + " out of 100."
    artists_popularity_string = "The average popularity of your top 10 artists is " + str(average_popularity_artists) + " out of 100."

    metrics_array = ["","","","","","","","",""]
    metrics_array[0] = "The average danceability of your top 10 tracks is " + str(average_danceability) + " on a scale from 0 to 1."
    metrics_array[1] = "The average energy of your top 10 tracks is " + str(average_energy) + " on a scale from 0 to 1."
    metrics_array[2] = "The average loudness of your top 10 tracks is " + str(average_loudness) + " decibels (on a scale from -60 and 0 db)."
    metrics_array[3] = "The average acousticness of your top 10 tracks is " + str(average_acousticness) + " on a scale from 0 to 1"
    metrics_array[4] = "The average instrumentalness of your top 10 tracks is " + str(average_instrumentalness) + " on a scale from 0 to 1, where the closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content."
    metrics_array[5] = "The average liveness of your top 10 tracks is " + str(average_liveness) + " on a scale from 0 to 1, where higher liveness values represent an increased probability that the track was performed live."
    metrics_array[6] = "The average valence of your top 10 tracks is " + str(average_valence) + " on a scale from 0 to 1."
    metrics_array[7] = "The average tempo of your top 10 tracks is " + str(average_tempo) + " beats per minute."

    


    # Combine profile and playlist data to display
    template = render_template("index.html", tracklist=tracklist, tracks_popularity=tracks_popularity_string, artistlist=artist_list, artists_popularity=artists_popularity_string, metricslist=metrics_array)
    return template


if __name__ == "__main__":
    app.run(debug=True, port=PORT)