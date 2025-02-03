import json
import os
import time
from discord.ext import commands
from user_tokens import load_tokens, save_tokens
from top_artists import get_global_top_artists, get_recent_artists
from spotify import refresh_access_token, get_auth_url, respond_deferred, follow_up_message, exchange_code_for_tokens
import discord
import nacl.signing
import nacl.encoding
import nacl.exceptions

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")
if DISCORD_PUBLIC_KEY:
    DISCORD_PUBLIC_KEY = DISCORD_PUBLIC_KEY.strip()


def lambda_handler(event, context):
    print(f"[DEBUG] Evento recebido: {json.dumps(event)}")

    path = event.get("rawPath", "")

    if path == "/prod/callback" or path == "/callback":
        return handle_spotify_callback(event)

    if "headers" in event and "x-signature-ed25519" in event["headers"]:
        if not validate_discord_signature(event):
            print("[ERROR] Assinatura do Discord inválida.")
            return {
                "statusCode": 401,
                "body": "Unauthorized"
            }

    if "body" in event:
        body = json.loads(event["body"])
        if body.get("type") == 1:
            print("[INFO] Respondendo à verificação do Discord.")
            return {
                "statusCode": 200,
                "body": json.dumps({"type": 1}),
            }

    if "source" in event and event["source"] == "aws.events":
        print("[INFO] Lambda acionado pelo EventBridge.")
        return process_weekly_report()

    elif "body" in event:
        print("[INFO] Lambda acionado pelo Discord (Slash Command).")
        return process_discord_command(event)

    print("[ERROR] Evento desconhecido.")
    return {
        "statusCode": 400,
        "body": json.dumps({"message": "Evento desconhecido."}),
    }


def handle_spotify_callback(event):
    try:
        query_params = event.get("queryStringParameters", {})
        code = query_params.get("code")
        state = query_params.get("state")

        if not code or not state:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Código ou estado ausente no callback."}),
            }

        print(f"[INFO] Código recebido: {code}, Estado (User ID): {state}")

        tokens = exchange_code_for_tokens(code)
        print(f"[INFO] Tokens obtidos: {tokens}")

        user_id = state
        user_tokens = load_tokens()
        user_tokens[user_id] = {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "expires_at": int(time.time()) + tokens["expires_in"],
        }
        save_tokens(user_tokens)

        return {
            "statusCode": 200,
            "body": json.dumps({"Autenticacao concluida com sucesso! Retorne ao Discord e digite /charts novamente para seu resumo!"}),
        }
    except Exception as e:
        print(f"[ERROR] Erro ao processar callback: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Erro interno ao processar o callback."}),
        }


def validate_discord_signature(event):
    signature = event["headers"].get("x-signature-ed25519")
    timestamp = event["headers"].get("x-signature-timestamp")
    body = event.get("body", "")
    print(f"[DEBUG] Chave pública usada: {DISCORD_PUBLIC_KEY}")

    if not DISCORD_PUBLIC_KEY:
        raise ValueError("A chave pública do Discord não foi configurada.")

    try:
        verify_key = nacl.signing.VerifyKey(
            DISCORD_PUBLIC_KEY,
            encoder=nacl.encoding.HexEncoder
        )
        verify_key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))
        print("[INFO] Assinatura validada com sucesso.")
        return True
    except nacl.exceptions.BadSignatureError:
        print("[ERROR] Assinatura do Discord inválida.")
        return False


def process_weekly_report():
    user_tokens = load_tokens()

    print("[INFO] Atualizando tokens expirados...")
    for user_id, tokens in user_tokens.items():
        if tokens.get("expires_at", 0) < time.time():
            try:
                new_tokens = refresh_access_token(tokens["refresh_token"])
                user_tokens[user_id].update(new_tokens)
            except Exception as e:
                print(f"[ERROR] Falha ao atualizar token para o usuário {user_id}: {e}")
    save_tokens(user_tokens)

    print("[INFO] Gerando relatório semanal...")
    global_top_artists = get_global_top_artists(user_tokens)

    if not global_top_artists:
        print("[INFO] Nenhum dado disponível para o relatório.")
        return {"statusCode": 200, "body": "Nenhum dado disponível para o relatório."}

    report = "\n".join(
        [f"{i + 1}. {artist} - {count} execuções" for i, (artist, count) in enumerate(global_top_artists)]
    )
    message = f"🎶 **Top 5 Artistas Mais Ouvidos no Discord Esta Semana:**\n{report}"

    send_discord_message(DISCORD_CHANNEL_ID, message)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Relatório enviado com sucesso!"}),
    }


def process_discord_command(event):
    body = json.loads(event["body"])
    command = body.get("data", {}).get("name")
    user_id = body.get("member", {}).get("user", {}).get("id")
    interaction_id = body.get("id")
    interaction_token = body.get("token")

    print(f"[DEBUG] Comando recebido: {command}")

    if command == "charts":
        respond_deferred(interaction_id, interaction_token)

        user_tokens = load_tokens()

        if user_id not in user_tokens:
            auth_url, _ = get_auth_url(state=user_id)
            print(f"[DEBUG] Interaction Token: {interaction_token}")
            follow_up_message(interaction_token, f"🔗 **Autenticação necessária!** Clique no link: {auth_url}")
            return

        try:
            user_data = user_tokens[user_id]
            if user_data.get("expires_at", 0) < time.time():
                print(f"[INFO] Atualizando token expirado para o usuário {user_id}")
                new_tokens = refresh_access_token(user_data["refresh_token"])
                user_tokens[user_id].update(new_tokens)
                save_tokens(user_tokens)

            access_token = user_tokens[user_id]["access_token"]
            user_artists = get_recent_artists(access_token)
            top_artists = sorted(user_artists.items(), key=lambda x: x[1], reverse=True)[:5]
            report = "\n".join(
                [f"{i + 1}. {artist} - {count} execuções" for i, (artist, count) in enumerate(top_artists)])

            follow_up_message(interaction_token, f"🎶 **Seus artistas mais ouvidos:**\n{report}")
        except Exception as e:
            print(f"[ERROR] Erro ao buscar dados para o usuário {user_id}: {e}")
            follow_up_message(interaction_token, "❌ Ocorreu um erro ao buscar seus dados. Tente novamente.")

    elif command == "instrucoes":
        respond_deferred(interaction_id, interaction_token)

        instructions = (
            "ℹ️ **Instruções de Uso:**\n\n"
            "1. Certifique-se de que está autenticado com o Spotify através do comando `/charts`.\n"
            "2. A API do Spotify retorna apenas as últimas **50 faixas** ouvidas.\n"
            "3. Se você não ouviu música recentemente, os dados podem estar incompletos.\n"
            "4. Caso precise de ajuda, entre em contato com o suporte do bot (@purplecorolla) ou utilize `/ajuda`."
        )
        follow_up_message(interaction_token, instructions)

    elif command == "ajuda":
        respond_deferred(interaction_id, interaction_token)

        help_message = (
            "❓ **Comandos Disponíveis:**\n\n"
            "• `/charts` - Mostra os artistas mais ouvidos e/ou autentica o usuário.\n"
            "• `/instrucoes` - Exibe instruções sobre o funcionamento do bot.\n"
            "• `/ajuda` - Mostra esta lista de comandos."
        )
        follow_up_message(interaction_token, help_message)

    else:
        print(f"[ERROR] Comando desconhecido: {command}")
        respond_deferred(interaction_id, interaction_token)
        follow_up_message(interaction_token, "❌ Comando não reconhecido. Use `/ajuda` para ver os comandos disponíveis.")

    return {"statusCode": 200, "body": "OK"}


def send_discord_message(channel_id, message):
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        try:
            channel = client.get_channel(channel_id)
            if channel:
                await channel.send(message)
                print("[INFO] Mensagem enviada com sucesso ao Discord.")
            else:
                print("[ERROR] Canal não encontrado.")
        finally:
            await client.close()

    client.run(DISCORD_TOKEN)


def respond(message):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "type": 4,
            "data": {"content": message},
        }),
    }
