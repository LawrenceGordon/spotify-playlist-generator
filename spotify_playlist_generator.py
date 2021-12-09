import requests, argparse, copy, json, spotipy
import spotipy.util as util
#from secret import token
from secret import user_id
from secret import client_id
from secret import client_secret

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", "-l", type=int, default=10, help="number of songs requested")
    parser.add_argument("--market", "-m", default="US", help="Country")
    parser.add_argument("--genre", "-g", help="seed genre")
    parser.add_argument("--artist", "-a", help="seed artist")
    parser.add_argument("--track", "-t", help="seed track")
    parser.add_argument("--dance", type=float, help="target danceability")
    parser.add_argument("--inst", "-i", type=float, help="target instrumentalness")
    parser.add_argument("--energy", "-e", type=float, help="target energy")
    parser.add_argument("--name", "-n", help="playlist name")
    parser.add_argument("--description", "-d", help="playlist description")
    parser.add_argument("-p", action="store_true", help="public if specified")

    return parser.parse_args()

def get_playlist(token, limit, market, seed_genres, seed_artists, seed_tracks, target_danceability, target_instrumentalness, target_energy):
    opt_queries = copy.deepcopy(vars())
    uris = []

    query = ''
    for k, v in opt_queries.items():
        if v is not None:
            query += f'{k}={v}&'
    query = query.rstrip('&')

    endpoint_url = "https://api.spotify.com/v1/recommendations?"
    query = endpoint_url + query

    response = requests.get(query, 
            headers={"Content-Type":"application/json", 
            "Authorization":"Bearer " + token})

    json_response = response.json()

    for idx, i in enumerate(json_response['tracks']):
        uris.append(i['uri'])
        print(f"{idx + 1}.) \"{i['name']}\" by {i['artists'][0]['name']}")

    return uris

def get_name(artist, track):
    if artist is None and track is None:
        name = input("Please specify a playlist name: ")
        return name
    elif track is None:
        endpoint_url = f"https://api.spotify.com/v1/artists/{artist}"
        response = requests.get(endpoint_url, 
            headers={"Content-Type":"application/json", 
            "Authorization":"Bearer " + token})
        name = f"Playlist based off of {response.json()['name']}"
        return name
    else:
        endpoint_url = f"https://api.spotify.com/v1/tracks/{track}"
        response = requests.get(endpoint_url, 
            headers={"Content-Type":"application/json", 
            "Authorization":"Bearer " + token})
        name = f"Playlist based off of {response.json()['name']} by {response.json()['album']['artists'][0]['name']}"
        return name

def make_playlist(user_id, token, uris, name, desc, public):
    endpoint_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    request_body = json.dumps({
          "name": name,
          "description": desc,
          "public": public
        })
    response = requests.post(url = endpoint_url, data = request_body, headers={"Content-Type":"application/json", 
        "Authorization":"Bearer " + token})

    url = response.json()['external_urls']['spotify']
    print(response.status_code)

    # Adds songs to playlist
    playlist_id = response.json()['id']

    endpoint_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    #print(endpoint_url, uris)

    request_body = json.dumps({
            "uris" : uris
            })
    response = requests.post(url = endpoint_url, data = request_body, headers={"Content-Type":"application/json", 
                            "Authorization":"Bearer " + token})

    print(response.status_code)
    print(f'Your playlist is ready at {url}')

def get_token(user_id, client_id, client_secret):
    token = util.prompt_for_user_token(user_id, "playlist-modify-private", client_id, client_secret, redirect_uri="http://localhost/")
    return token


args = parse_args()
token = get_token(user_id, client_id, client_secret)

artist = args.artist.split(":")[2] if args.artist is not None else args.artist
track = args.track.split(":")[2] if args.track is not None else None
print(artist, track)

uris = get_playlist(token, args.limit, args.market, args.genre, artist, track, args.dance, args.inst, args.energy)
if track is not None:
    uris[0] = (args.track)
if args.name is None:
    name = get_name(artist, track)
else:
    name = args.name
make_playlist(user_id, token, uris, name, args.description, args.p)
