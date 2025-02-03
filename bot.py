import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from spotify import get_auth_url, get_user_top_artists
from user_tokens import load_tokens, get_valid_access_token
from top_artists import get_global_top_artists, get_recent_artists


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send('Olá! Estou funcionando!')

@bot.command()
async def charts(ctx):
    user_id = str(ctx.author.id)
    user_tokens = load_tokens()

    if user_id not in user_tokens:
        await ctx.send(
            f"{ctx.author.mention}, você precisa autenticar primeiro! "
            "Use o link enviado anteriormente para conectar sua conta Spotify."
        )
        return

    try:
        access_token = get_valid_access_token(user_id, user_tokens)

        user_artists = get_recent_artists(access_token)
        if not user_artists:
            await ctx.send(f"{ctx.author.mention}, nenhum dado disponível para os últimos 7 dias.")
            return

        top_artists = sorted(user_artists.items(), key=lambda x: x[1], reverse=True)[:5]

        report = "\n".join([f"{i+1}. {artist} - {count} execuções" for i, (artist, count) in enumerate(top_artists)])
        await ctx.send(f"🎶 **Top 5 Artistas Mais Ouvidos Semana do Usuário:**\n{report}")

    except Exception as e:
        await ctx.send(f"{ctx.author.mention}, ocorreu um erro ao buscar seus dados. Tente novamente mais tarde.")
        print(f"[ERROR] Falha ao buscar dados para o usuário {user_id}: {e}")

@bot.command()
async def weekly_report(ctx):
    user_tokens = load_tokens()
    global_top_artists = get_global_top_artists(user_tokens)

    if not global_top_artists:
        await ctx.send("Nenhum dado disponível para criar o relatório desta semana.")
        return

    report = "\n".join([f"{i+1}. {artist} - {count} execuções" for i, (artist, count) in enumerate(global_top_artists)])
    await ctx.send(f"🎶 **Top 5 Artistas Mais Ouvidos no Discord Esta Semana:**\n{report}")


bot.run(TOKEN)
