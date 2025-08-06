from pyrogram import Client, filters

api_id =   # Your API ID
api_hash = ""  # Your API Hash

app = Client("client name", api_id=api_id, api_hash=api_hash)

@app.on_message(filters.command("ping", prefixes=".") & filters.me)
async def ping(client, message):
    print("Ping command received")
    await message.reply("Pong!")

if __name__ == "__main__":
    app.run()


