from flask import Flask, request
from user_tokens import save_tokens, load_tokens
from spotify import get_user_top_artists

app = Flask(__name__)

@app.route("/callback")
def callback():
    code = request.args.get('code')
    user_id = request.args.get('state')
    user_tokens = load_tokens()

    print(f"Callback recebido: User ID: {user_id}, Code: {code}")

    try:
        result = get_user_top_artists(code, user_id)
        token_info = result['token_info']

        user_tokens[user_id] = {
            'access_token': token_info['access_token'],
            'refresh_token': token_info['refresh_token'],
            'expires_at': token_info['expires_at']
        }
        save_tokens(user_tokens)
        print(f"✅ Tokens salvos para o usuário {user_id}")
        return "Autenticação concluída! Volte ao Discord e use !charts novamente."

    except Exception as e:
        print(f"[ERROR] Erro durante o callback: {e}")
        return "Erro durante a autenticação", 500

if __name__ == "__main__":
    app.run(port=8888)