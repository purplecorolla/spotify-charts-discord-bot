import json
import os
from spotify import refresh_access_token
import time
import boto3

S3_BUCKET = os.getenv("S3_BUCKET_NAME")
S3_KEY = "tokens.json"


s3_client = boto3.client("s3")

user_tokens = {}

def save_tokens(tokens):
    """
    Salva o dicionário de tokens no S3 como JSON.
    :param tokens: Dicionário contendo os tokens dos usuários.
    """
    if not S3_BUCKET:
        raise ValueError("S3_BUCKET_NAME não configurado. Certifique-se de definir a variável de ambiente.")

    try:
        tokens_json = json.dumps(tokens, indent=4)
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=S3_KEY,
            Body=tokens_json,
            ContentType="application/json"
        )
        print("✅ Tokens salvos no S3 com sucesso!")
    except Exception as e:
        print(f"[ERROR] Falha ao salvar tokens no S3: {e}")
        raise

def load_tokens():
    """
    Carrega os tokens do S3.
    :return: Dicionário contendo os tokens dos usuários.
    """
    global user_tokens

    if not S3_BUCKET:
        raise ValueError("S3_BUCKET_NAME não configurado. Certifique-se de definir a variável de ambiente.")

    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        tokens_json = response["Body"].read().decode("utf-8")
        user_tokens = json.loads(tokens_json)
        print("✅ Tokens carregados do S3 com sucesso!")
    except s3_client.exceptions.NoSuchKey:
        print("[INFO] Nenhum arquivo de tokens encontrado no S3. Criando vazio.")
        user_tokens = {}
    except Exception as e:
        print(f"[ERROR] Falha ao carregar tokens do S3: {e}")
        user_tokens = {}

    return user_tokens

load_tokens()

def get_valid_access_token(user_id, user_tokens):
    """
    Retorna um access_token válido para o usuário, atualizando-o se necessário.
    """
    token_data = user_tokens.get(user_id)
    if not token_data:
        raise Exception(f"Usuário {user_id} não encontrado nos tokens.")

    expires_at = token_data.get("expires_at", 0)
    current_time = int(time.time())
    print(f"[DEBUG] Verificação do token: expira em {expires_at}, hora atual {current_time}")

    if current_time >= expires_at:
        print(f"[INFO] Access token para o usuário {user_id} expirou. Atualizando...")
        refresh_token = token_data.get("refresh_token")
        if not refresh_token:
            raise Exception(f"Refresh token não encontrado para o usuário {user_id}.")

        try:
            new_token_info = refresh_access_token(refresh_token)
            token_data["access_token"] = new_token_info["access_token"]
            token_data["expires_at"] = current_time + new_token_info.get("expires_in", 3600)

            user_tokens[user_id] = token_data
            save_tokens(user_tokens)
            print(f"[INFO] Novo token atualizado para o usuário {user_id}")
        except Exception as e:
            print(f"[ERROR] Falha ao atualizar o token para o usuário {user_id}: {e}")
            raise

    return token_data["access_token"]
