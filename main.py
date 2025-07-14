from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio

api_id = 15542958
api_hash = "115e7c25b2747bd94757e7d2191f7417"
app = Client("aa1", api_id=api_id, api_hash=api_hash)


# 🧾 Command menu
async def send_command_menu(message: Message):
    text = (
        "📜 *Available Commands:*\n\n"
        "👥 Contacts:\n"
        "`.bc1a` – Broadcast to contacts\n"
        "`.add1a` – Add usernames from `usernames.txt`\n"
        "`.list1a` – List all saved contacts\n\n"
        "👥 Groups:\n"
        "`.bc1b` – Broadcast to groups\n"
        "`.addbl1` – Blacklist current group\n"
        "`.unbl1` – Unblacklist current group\n"
        "`.bl_list1a` – List all blacklisted groups\n"
        "`.clear1a` – Clear all blacklisted groups\n"
    )
    await message.reply(text)

@app.on_message(filters.command("ping", prefixes=".") & filters.me)
async def ping(client, message: Message):
        print("Ping command received")
        await message.reply("Pong!")
    
# 📢 Broadcast to contacts
@app.on_message(filters.command("bc1a", prefixes=".") & filters.reply & filters.me)
async def broadcast_to_contacts(client, message: Message):
    target_message = message.reply_to_message
    if not target_message:
        await message.reply("❗Please reply to the message you want to broadcast.")
        return

    contacts = await client.get_contacts()
    total = len(contacts)
    sent, failed = 0, 0

    await message.reply(f"📢 Broadcasting to {total} contacts...")

    for contact in contacts:
        try:
            await target_message.copy(chat_id=contact.id)
            print(f"✅ Sent to {contact.first_name} ({contact.id})")
            sent += 1
            await asyncio.sleep(1.2)
        except Exception as e:
            print(f"❌ Failed to send to {contact.id}: {e}")
            failed += 1
            await asyncio.sleep(0.5)

    await message.reply(f"📤 Done!\nSent: {sent} ✅\nFailed: {failed} ❌")
    await send_command_menu(message)


# 📢 Broadcast to groups
@app.on_message(filters.command("bc1b", prefixes=".") & filters.reply & filters.me)
async def broadcast_to_groups(client: Client, message: Message):
    target_message = message.reply_to_message
    if not target_message:
        await message.reply("❗Please reply to the message you want to broadcast.")
        return

    sent, failed = 0, 0

    try:
        with open("blacklisted_groups.txt", "r") as file:
            blacklisted_ids = set(map(int, file.read().splitlines()))
    except FileNotFoundError:
        blacklisted_ids = set()

    await message.reply("📢 Broadcasting to groups...")

    async for dialog in client.get_dialogs():
        chat = dialog.chat
        if chat.type in ["group", "supergroup"]:
            if chat.id in blacklisted_ids:
                print(f"🚫 Skipped blacklisted group: {chat.title} ({chat.id})")
                continue
            try:
                await target_message.copy(chat_id=chat.id)
                print(f"✅ Sent to group: {chat.title} ({chat.id})")
                sent += 1
                await asyncio.sleep(1.2)
            except Exception as e:
                print(f"❌ Failed to group {chat.id}: {e}")
                failed += 1
                await asyncio.sleep(0.5)

    await message.reply(f"📤 Done!\nSent: {sent} ✅\nFailed: {failed} ❌")
    await send_command_menu(message)


# ➕ Add contacts from file
@app.on_message(filters.command("add1a", prefixes=".") & filters.me)
async def add_contacts(client, message):
    success, failed = 0, 0
    with open("usernames.txt", "r", encoding="utf-8") as f:
        usernames = [line.strip().lstrip("@") for line in f if line.strip()]

    await message.reply(f"⏳ Adding {len(usernames)} usernames to contacts...")

    for username in usernames:
        try:
            user = await client.get_users(username)
            await client.add_contact(
                user_id=user.id,
                first_name=user.first_name or "NoName",
                last_name=user.last_name or ""
            )
            print(f"✅ Added: @{username}")
            success += 1
            await asyncio.sleep(1.2)
        except Exception as e:
            print(f"❌ Failed: @{username} - {e}")
            failed += 1

    await message.reply(f"✅ Done.\nAdded: {success}\nFailed: {failed}")
    await send_command_menu(message)


# 🚫 Blacklist current group
@app.on_message(filters.command("addbl1", prefixes=".") & filters.me)
async def blacklist_group(client, message: Message):
    chat = message.chat
    if chat.type not in ("group", "supergroup"):
        await message.reply("⚠️ This command must be used in a group.")
        return

    try:
        with open("blacklisted_groups.txt", "a+") as file:
            file.seek(0)
            blacklisted = file.read().splitlines()
            if str(chat.id) not in blacklisted:
                file.write(f"{chat.id}\n")
                await message.reply(f"🚫 Group '{chat.title}' has been blacklisted.")
            else:
                await message.reply("✅ This group is already blacklisted.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")
    await send_command_menu(message)


# ✅ Unblacklist current group
@app.on_message(filters.command("unbl1", prefixes=".") & filters.me)
async def unblacklist_group(client, message: Message):
    chat = message.chat
    if chat.type not in ("group", "supergroup"):
        await message.reply("⚠️ This command must be used in a group.")
        return

    try:
        with open("blacklisted_groups.txt", "r") as file:
            groups = file.read().splitlines()

        if str(chat.id) in groups:
            groups.remove(str(chat.id))
            with open("blacklisted_groups.txt", "w") as file:
                file.write("\n".join(groups) + "\n")
            await message.reply(f"✅ Group '{chat.title}' has been unblacklisted.")
        else:
            await message.reply("ℹ️ This group is not blacklisted.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")
    await send_command_menu(message)


# 🧾 List blacklisted groups
@app.on_message(filters.command("bl_list1a", prefixes=".") & filters.me)
async def list_blacklisted_groups(client, message: Message):
    try:
        with open("blacklisted_groups.txt", "r") as file:
            groups = file.read().splitlines()

        if not groups:
            await message.reply("✅ No groups are currently blacklisted.")
            return

        text = "🚫 *Blacklisted Group IDs:*\n" + "\n".join(groups)
        await message.reply(text, quote=True)
    except FileNotFoundError:
        await message.reply("✅ No blacklist file found. You're all clear.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")
    await send_command_menu(message)


# 🧹 Clear all blacklisted groups
@app.on_message(filters.command("clear1a", prefixes=".") & filters.me)
async def clear_blacklisted_groups(client, message: Message):
    try:
        open("blacklisted_groups.txt", "w").close()
        await message.reply("🧹 All blacklisted groups have been cleared.")
    except Exception as e:
        await message.reply(f"❌ Error clearing blacklist: {e}")
    await send_command_menu(message)


# 📋 List contacts
@app.on_message(filters.command("list1a", prefixes=".") & filters.me)
async def list_contacts(client, message: Message):
    contacts = await client.get_contacts()
    if not contacts:
        await message.reply("❗ You have no saved contacts.")
        return

    contact_lines = []
    for user in contacts:
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        username = f"@{user.username}" if user.username else "(no username)"
        contact_lines.append(f"{name} | {username} | ID: `{user.id}`")

    chunk = ""
    for line in contact_lines:
        if len(chunk) + len(line) + 1 > 4000:
            await message.reply(chunk)
            chunk = ""
        chunk += line + "\n"

    if chunk:
        await message.reply(chunk)
    await send_command_menu(message)


# ℹ️ Help command
@app.on_message(filters.command("help1a", prefixes=".") & filters.me)
async def show_help(client, message: Message):
    help_text = """
📖 *Available Commands*:

👥 **Broadcasting**
• `.bc1a` — Broadcast message to all contacts (must reply to a message)
• `.bc1b` — Broadcast message to all groups (except blacklisted ones)

📌 **Contact Management**
• `.add1a` — Add usernames from `usernames.txt` to contacts
• `.list1a` — List all saved contacts

🚫 **Group Blacklist Management**
• `.addbl1` — Blacklist the current group (used inside group)
• `.unbl1` — Remove the current group from blacklist
• `.bl_list1a` — Show all blacklisted group IDs
• `.clear1a` — Clear the entire group blacklist

❓ **Help**
• `.help1a` — Show this help message
"""
    await message.reply(help_text)
    await send_command_menu(message)

# 🧹 Clean up unsupported Groups
@app.on_message(filters.command("clean1a", prefixes=".") & filters.me)
async def clean_invalid_peers(client, message):
    removed, failed, checked = 0, 0, 0
    await message.reply("🔍 Scanning for invalid/broken chats...")

    async for dialog in client.get_dialogs():
        checked += 1
        try:
            chat = await client.get_chat(dialog.chat.id)
            # If get_chat works, the peer is valid
        except ValueError as e:
            if "Peer id invalid" in str(e):
                try:
                    await client.delete_chat(dialog.chat.id)
                    print(f"🗑️ Deleted invalid peer: {dialog.chat.id}")
                    removed += 1
                except Exception as ex:
                    print(f"❌ Failed to delete {dialog.chat.id}: {ex}")
                    failed += 1
        except Exception as ex:
            print(f"⚠️ Other error on {dialog.chat.id}: {ex}")
            failed += 1

    await message.reply(
        f"✅ Scan Complete\n\n"
        f"Total Dialogs Checked: {checked}\n"
        f"🗑️ Invalid Peers Removed: {removed}\n"
        f"❌ Errors: {failed}"
    )

# ✅ Run the app
print("✅ Userbot is running. Waiting for commands...")
app.run()
