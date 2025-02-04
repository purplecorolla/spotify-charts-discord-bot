## 🤖 Spotify Charts Discord Bot

Este é um bot do **Discord** que permite visualizar os artistas mais ouvidos do usuário no **Spotify**, utilizando a API oficial do serviço. Ele requer autenticação OAuth para acessar os dados do usuário.

This is a **Discord bot** that allows users to view their most listened artists on **Spotify**, using the official Spotify API. It requires OAuth authentication to access user data.

---

## 🛠️ Fluxo de funcionamento | Bot Flow

![Fluxo do Bot](docs/discord-spotify-bot-gif.gif)

### (BR) **Fluxo de funcionamento do bot**
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

### (EN) **Bot Flow**
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

## 🔑 Fluxo de Autenticação | Authentication Flow

### (BR) **Fluxo de Autenticação no Spotify**
1️⃣ O usuário envia um comando `/charts` pela primeira vez.  
2️⃣ O bot detecta que o usuário **ainda não autenticou no Spotify**.  
3️⃣ A Lambda retorna um link de **autorização do Spotify** para o usuário clicar.  
4️⃣ O usuário autoriza o aplicativo, e o Spotify redireciona para a **API Gateway** com um código de autorização.  
5️⃣ A API Gateway chama a **Lambda**, que troca o código pelo token de acesso e refresh token.  
6️⃣ O token é salvo no **S3 Bucket** para reutilização futura.  
7️⃣ A Lambda responde ao usuário no Discord, agora com os dados do Spotify.

---

### (EN) **Spotify Authentication Flow**
1️⃣ The user sends the `/charts` command for the first time.  
2️⃣ The bot detects that the user **has not authenticated with Spotify yet**.  
3️⃣ Lambda returns a **Spotify authorization link** for the user to click.  
4️⃣ The user authorizes the app, and Spotify redirects to the **API Gateway** with an authorization code.  
5️⃣ API Gateway triggers **Lambda**, which exchanges the code for an access token and a refresh token.  
6️⃣ The token is stored in the **S3 Bucket** for future use.  
7️⃣ Lambda responds to the user on Discord, now with Spotify data.  

---

