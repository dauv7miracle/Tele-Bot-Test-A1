from pyrogram import Client, filters

api_id = 15542958  # Your API ID
api_hash = "115e7c25b2747bd94757e7d2191f7417"  # Your API Hash

app = Client("aa1", api_id=api_id, api_hash=api_hash)

@app.on_message(filters.command("ping", prefixes=".") & filters.me)
async def ping(client, message):
    print("Ping command received")
    await message.reply("Pong!")

if __name__ == "__main__":
    app.run()
