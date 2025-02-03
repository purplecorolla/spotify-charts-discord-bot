import requests
import os

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
APPLICATION_ID = "1234567123456789876"
GUILD_ID = "123456712345678987" #Channel ID do servidor que o bot será disponibilizado


commands = [
    {
        "name": "charts",
        "description": "Mostra os artistas mais ouvidos na última semana."
    },
    {
        "name": "weekly_report",
        "description": "Mostra o top 5 global de artistas mais ouvidos no Discord na última semana."
    },
    {
        "name": "instrucoes",
        "description": "Exibe instruções sobre como usar o bot.",
    },
    {
        "name": "ajuda",
        "description": "Lista todos os comandos disponíveis.",
    }
]

headers = {
    "Authorization": f"Bot {DISCORD_TOKEN}",
    "Content-Type": "application/json"
}

url = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/guilds/{GUILD_ID}/commands"

for command in commands:
    response = requests.post(url, json=command, headers=headers)
    if response.status_code == 201:
        print(f"✅ Comando '{command['name']}' registrado com sucesso!")
    else:
        print(f"❌ Falha ao registrar o comando '{command['name']}': {response.status_code} {response.text}")
