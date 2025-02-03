import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import time

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPE = 'user-top-read user-read-recently-played'

def get_auth_url(state=None):
    sp_oauth = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=None
    )
    auth_url = sp_oauth.get_authorize_url(state=state)
    return auth_url, sp_oauth


def get_user_top_artists(code, user_id, period="short_term"):
    sp_oauth = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=f".cache-{user_id}"
    )

    print(f"[DEBUG] Trocando código por token para user_id={user_id}")
    token_info = sp_oauth.get_access_token(code)
    if not token_info or 'access_token' not in token_info:
        print(f"[ERROR] Falha ao obter token para user_id={user_id}, code={code}")
        raise Exception("Erro ao obter token de acesso")

    access_token = token_info['access_token']
    print(f"[DEBUG] Token de acesso obtido: {access_token[:10]}... para user_id={user_id}")
    print(f"[DEBUG] Escopos do token: {token_info.get('scope')}")  # Log dos escopos

    sp = spotipy.Spotify(auth=access_token)
    try:
        results = sp.current_user_top_artists(limit=10, time_range=period)
    except spotipy.exceptions.SpotifyException as e:
        print(f"[ERROR] Falha ao buscar artistas: {e}")
        raise e

    top_artists = [artist['name'] for artist in results['items']]
    print(f"[DEBUG] Artistas retornados para user_id={user_id}: {top_artists}")

    return {
        'top_artists': top_artists,
        'token_info': token_info
    }

def refresh_access_token(refresh_token):
    """
    Atualiza o access_token usando o refresh_token.
    Retorna o novo access_token e o tempo de expiração.
    """
    url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET
    }

    response = requests.post(url, data=payload)
    if response.status_code == 200:
        token_info = response.json()
        print(f"[DEBUG] Resposta da API do Spotify: {token_info}")
        print("✅ Access token atualizado com sucesso!")

        return {
            "access_token": token_info["access_token"],
            "expires_at": int(time.time()) + token_info.get("expires_in", 3600),
        }
    else:
        print(f"[ERROR] Falha ao atualizar access token: {response.status_code}, {response.text}")
        raise Exception("Erro ao atualizar access token")


def respond_deferred(interaction_id, interaction_token):
    url = f"https://discord.com/api/v10/interactions/{interaction_id}/{interaction_token}/callback"
    payload = {
        "type": 5
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    print(f"[DEBUG] Resposta diferida enviada: {response.status_code}")


def follow_up_message(interaction_token, content):
    if not interaction_token:
        print("[ERROR] Interaction Token está vazio.")
        return None

    url = f"https://discord.com/api/v10/webhooks/{os.getenv('DISCORD_APP_ID')}/{interaction_token}"
    payload = {
        "content": content
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    print(f"[DEBUG] Mensagem de acompanhamento enviada: {response.status_code}, {response.text}")

    return response

def exchange_code_for_tokens(code):
    url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.getenv("REDIRECT_URI"),
        "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
        "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET"),
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, data=data, headers=headers)
    if response.status_code != 200:
        print(f"[ERROR] Erro ao obter tokens: {response.text}")
        raise Exception("Erro ao trocar código por tokens.")

    return response.json()
