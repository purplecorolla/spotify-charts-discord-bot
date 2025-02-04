# 🤖 Spotify Charts Discord Bot

Este é um bot do Discord que integra com a API do Spotify para gerar relatórios de artistas mais ouvidos pelos usuários. O bot permite que os usuários autentiquem suas contas do Spotify e visualizem suas estatísticas musicais diretamente no Discord.

## Recursos

- 🎵 Exibe os artistas mais ouvidos dos usuários.
- ⚡ Atualização automática dos tokens de autenticação.
- ⏰ Envio automático de relatórios semanais.
- ✅ Comandos fáceis de usar no Discord.
---
## Configuração

1. Clone este repositório:
   ```sh
   git clone https://github.com/purplecorolla/spotify-charts-discord-bot.git
   cd spotify-charts-discord-bot
   ```

2. Instale as dependências:
   ```sh
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente no arquivo `.env`:
   ```ini
   DISCORD_TOKEN=seu_token_discord
   DISCORD_APP_ID=sua_app_id_discord
   DISCORD_PUBLIC_KEY=sua_public_key_discord
   SPOTIFY_CLIENT_ID=seu_client_id_spotify
   SPOTIFY_CLIENT_SECRET=seu_client_secret_spotify
   REDIRECT_URI=https://seu-api-gateway.amazonaws.com/prod/callback
   S3_BUCKET_NAME=seu_bucket_s3
   DISCORD_CHANNEL_ID=seu_channel_id_discord
   ```
---
## Uso

O bot suporta os seguintes comandos no Discord:

- `/charts` — Exibe os artistas mais ouvidos do usuário.
- `/instrucoes` — Explica as regras da API do Spotify e como o bot funciona.
- `/ajuda` — Lista os comandos disponíveis.
---
## Arquitetura

A infraestrutura do bot é composta pelos seguintes serviços:
- **AWS Lambda** — Executa a lógica do bot.
- **Amazon S3** — Armazena tokens dos usuários.
- **API Gateway** — Expondo endpoints para integração.
- **EventBridge** — Agendamento de relatórios semanais.
---
## 🛠️ Fluxo de funcionamento
  
![Fluxo do Bot](docs/discord-spotify-bot-gif.gif)  
  
### **Fluxo de funcionamento do bot**  
1️⃣ **Usuário interage com o bot no Discord**    
- O usuário envia um comando (`/charts`, `/instrucoes`, `/ajuda`) no canal do Discord.    
  
2️⃣ **Bot do Discord recebe o comando**    
- O bot verifica o comando recebido e envia a requisição para o **API Gateway** da AWS.    
  
3️⃣ **API Gateway direciona a requisição para a AWS Lambda**    
- A AWS Lambda processa o comando e verifica se o usuário está autenticado no Spotify.    
  
4️⃣ **Lambda faz requisição à API do Spotify**    
- Se o usuário já está autenticado, a função Lambda obtém os dados do Spotify, como o histórico de músicas.    
 - Se o usuário **não está autenticado**, a Lambda retorna um link de autenticação.    
  
5️⃣ **Tokens de autenticação são armazenados no S3**    
- Após autenticar no Spotify, o token de acesso do usuário é salvo no **S3 Bucket**.    
 - Se o token já estiver salvo, ele é carregado da AWS para evitar múltiplas autenticações.    
  
6️⃣ **Bot responde ao usuário no Discord**    
- Se o usuário já estava autenticado, o bot responde com os dados do Spotify.    
 - Se o usuário **precisava autenticar**, o bot envia um link para login no Spotify.  
---
### **Fluxo de Autenticação no Spotify**  
1️⃣ O usuário envia um comando `/charts` pela primeira vez.    
2️⃣ O bot detecta que o usuário **ainda não autenticou no Spotify**.    
3️⃣ A Lambda retorna um link de **autorização do Spotify** para o usuário clicar.    
4️⃣ O usuário autoriza o aplicativo, e o Spotify redireciona para a **API Gateway** com um código de autorização.    
5️⃣ A API Gateway chama a **Lambda**, que troca o código pelo token de acesso e refresh token.    
6️⃣ O token é salvo no **S3 Bucket** para reutilização futura.    
7️⃣ A Lambda responde ao usuário no Discord, agora com os dados do Spotify.   
---
## Observações Importantes ⚠️
- O arquivo **token.json** é criado automaticamente no bucket S3 quando um usuário autentica pela primeira vez. Se ele não existir, será gerado.
- A **API do Spotify** retorna apenas as últimas 50 músicas que o usuário ouviu. Não é possível acessar históricos mais antigos.
- Se o usuário não tiver ouvido música recentemente, os dados podem estar incompletos ou não retornar resultados.
- Certifique-se de que seu **Spotify Developer App** está configurado corretamente, incluindo a URI de redirecionamento. 
- O bot precisa ser registrado no **Discord**, e os comandos devem ser adicionados manualmente via API.

---
## Contribuição

Pull requests são bem-vindos! Para mudanças maiores, abra uma issue para discutir o que gostaria de modificar.



---

# 🤖 Spotify Charts Discord Bot (English)

This is a Discord bot that integrates with the Spotify API to generate reports on users most-listened artists. The bot allows users to authenticate their Spotify accounts and view their music stats directly on Discord.

## Features

- 🎵 Displays users top-listened artists.
- ⚡ Automatically refreshes authentication tokens.
- ⏰ Sends weekly reports automatically.
- ✅ Easy-to-use Discord commands.
---
## Setup

1. Clone this repository:
   ```sh
   git clone https://github.com/purplecorolla/spotify-charts-discord-bot.git
   cd spotify-charts-discord-bot
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Set up environment variables in the `.env` file:
   ```ini
   DISCORD_TOKEN=your_discord_token
   DISCORD_APP_ID=your_discord_app_id
   DISCORD_PUBLIC_KEY=your_discord_public_key
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   REDIRECT_URI=https://your-api-gateway.amazonaws.com/prod/callback
   S3_BUCKET_NAME=your_s3_bucket
   DISCORD_CHANNEL_ID=your_discord_channel_id
   ```
---
## Usage

The bot supports the following commands in Discord:

- `/charts` — Displays the user's most listened-to artists.
- `/instrucoes` — Explains Spotify API limitations and how the bot works.
- `/ajuda` — Lists available commands.
---
## Architecture

The bot's infrastructure is composed of the following services:
- **AWS Lambda** — Runs the bot logic.
- **Amazon S3** — Stores user tokens.
- **API Gateway** — Exposes endpoints for integration.
- **EventBridge** — Schedules weekly reports.
---
### 🛠️ **Bot Flow**  
![Fluxo do Bot](docs/discord-spotify-bot-gif.gif)  
1️⃣ **User interacts with the bot on Discord**    
- The user sends a command (`/charts`, `/instructions`, `/help`) in a Discord channel.    
  
2️⃣ **Discord Bot receives the command**    
- The bot verifies the received command and sends a request to the **AWS API Gateway**.    
  
3️⃣ **API Gateway directs the request to AWS Lambda**    
- The AWS Lambda function processes the command and checks if the user is authenticated with Spotify.    
  
4️⃣ **Lambda requests data from the Spotify API**    
- If the user is already authenticated, the Lambda function fetches data from Spotify, such as the listening history.    
 - If the user **is not authenticated**, Lambda returns an authentication link.    
  
5️⃣ **Authentication tokens are stored in S3**    
- After authenticating with Spotify, the user's access token is saved in the **S3 Bucket**.    
 - If the token already exists, it is loaded from AWS to avoid multiple authentication requests.    
  
6️⃣ **Bot replies to the user on Discord**    
- If the user was already authenticated, the bot responds with Spotify data.    
 - If the user **needed to authenticate**, the bot sends a login link for Spotify.    
  
---
### **Spotify Authentication Flow**  
1️⃣ The user sends the `/charts` command for the first time.    
2️⃣ The bot detects that the user **has not authenticated with Spotify yet**.    
3️⃣ Lambda returns a **Spotify authorization link** for the user to click.    
4️⃣ The user authorizes the app, and Spotify redirects to the **API Gateway** with an authorization code.    
5️⃣ API Gateway triggers **Lambda**, which exchanges the code for an access token and a refresh token.    
6️⃣ The token is stored in the **S3 Bucket** for future use.    
7️⃣ Lambda responds to the user on Discord, now with Spotify data.    

---
## Important Notes ⚠️
- The token.json file is automatically created in the S3 bucket when a user authenticates for the first time. If it doesn't exist, it will be generated.
- The Spotify API only returns the last 50 tracks played by the user. Older listening history is not accessible.
- If the user has not played any music recently, the data may be incomplete or may not return any results.
- Ensure that your Spotify Developer App is correctly configured, including the redirect URI.
- The bot must be registered on Discord, and commands must be manually added via the API.
---
## Contributing

Pull requests are welcome! For major changes, open an issue to discuss what you would like to change.




