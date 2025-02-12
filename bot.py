import sqlite3
import discord
import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DB_PATH = "data/elon_musk_bot.db"

# Configuración de la base de datos
if not os.path.exists("data"):
    os.makedirs("data")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS messages (user TEXT, message TEXT)''')
conn.commit()

# Cliente de Discord
intents = discord.Intents.default()
intents.messages = True

class ElonMuskBot(discord.Client):
    async def on_ready(self):
        print(f'Conectado como {self.user}')
        for guild in self.guilds:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    await channel.send("Hola, soy Elon Musk Bot. Puedo hablar con ustedes en cualquier momento. Comandos disponibles: !ayuda")
                    break
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        # Guardar mensaje en la base de datos
        cursor.execute("INSERT INTO messages (user, message) VALUES (?, ?)", (message.author.name, message.content))
        conn.commit()
        
        # Generar respuesta con Ollama
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "mistral", "prompt": message.content, "stream": False}
            )
            reply = response.json().get("response", "Lo siento, hubo un error procesando la respuesta.")
        except Exception as e:
            reply = "Error al conectar con Ollama."
            print(f"Error con Ollama: {e}")
        
        await message.channel.send(reply)

# Iniciar el bot
client = ElonMuskBot(intents=intents)
client.run(TOKEN)
