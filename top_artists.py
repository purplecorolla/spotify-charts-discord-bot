import spotipy
from datetime import datetime, timedelta
from user_tokens import get_valid_access_token
import pytz

def get_recent_artists(access_token):
    sp = spotipy.Spotify(auth=access_token)
    timezone = pytz.timezone('America/Sao_Paulo')
    end_time = datetime.now(timezone)
    start_time = end_time - timedelta(days=7)

    artists_count = {}
    before = None
    total_tracks_processed = 0

    print(f"[DEBUG] Início do período: {start_time}, Fim do período: {end_time}")

    while True:
        results = sp.current_user_recently_played(limit=50, before=before)
        if not results['items']:
            print("[DEBUG] Nenhum item retornado, encerrando busca.")
            break

        print(f"[DEBUG] Número de músicas retornadas: {len(results['items'])}")

        for item in results['items']:
            try:
                played_at = datetime.strptime(item['played_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
            except ValueError:
                played_at = datetime.strptime(item['played_at'], '%Y-%m-%dT%H:%M:%SZ')

            played_at = pytz.UTC.localize(played_at)
            played_at = played_at.astimezone(timezone)

            artist_name = item['track']['artists'][0]['name']
            print(f"[DEBUG] Verificando música: {item['track']['name']} - Artista: {artist_name} - Tocada em: {played_at}")

            if start_time <= played_at <= end_time:
                print(f"[DEBUG] Música dentro do período: {item['track']['name']} - Artista: {artist_name}")
                if artist_name in artists_count:
                    artists_count[artist_name] += 1
                else:
                    artists_count[artist_name] = 1

        before = results['cursors']['before']
        total_tracks_processed += len(results['items'])

        print(f"[DEBUG] Cursor 'before' atualizado para: {before}")
        print(f"[DEBUG] Total de músicas processadas até agora: {total_tracks_processed}")

        if total_tracks_processed >= 500:
            print("[DEBUG] Limite de 500 músicas processadas atingido, encerrando.")
            break

    print(f"[DEBUG] Contagem final de artistas: {artists_count}")
    return artists_count


def get_global_top_artists(user_tokens):
    """
    Consolida os dados de todos os usuários para calcular o Top 5 Global.
    """
    global_artists_count = {}

    for user_id, token_data in user_tokens.items():
        try:
            access_token = get_valid_access_token(user_id, user_tokens)
            user_artists = get_recent_artists(access_token)

            for artist, count in user_artists.items():
                if artist in global_artists_count:
                    global_artists_count[artist] += count
                else:
                    global_artists_count[artist] = count

        except Exception as e:
            print(f"[ERROR] Falha ao processar dados para user_id={user_id}: {e}")

    global_top_artists = sorted(global_artists_count.items(), key=lambda x: x[1], reverse=True)
    return global_top_artists[:5]