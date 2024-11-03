import discord
from discord.ext import commands
import json

# Replace with your bot token and admin Discord ID
TOKEN = "MTI5MTY0MTE4NDE0NTUwNjMxNA.G5XcCh.hIg_zEPDQeCvnrJWl0yuNfjXagIQDOGvLY2Qcw"
ADMIN_ID = 1041574639845003366  # Replace with the admin's Discord ID

bot = commands.Bot(command_prefix="!")

# Load messages from JSON
def load_messages():
    with open("dm_messages.json", "r") as file:
        return json.load(file)

# Save messages to JSON
def save_messages(data):
    with open("dm_messages.json", "w") as file:
        json.dump(data, file, indent=4)

# Command to add a new DM message
@bot.command()
@commands.is_owner()
async def add_dm_message(ctx, *, content):
    """Admin adds a new message for DMs."""
    data = load_messages()
    new_message = {
        "id": len(data["messages"]) + 1,
        "content": content,
        "status": "working",
        "votes": {"working": 0, "not_working": 0},
        "reported_by": []
    }
    data["messages"].append(new_message)
    save_messages(data)
    await ctx.send("Message added successfully!")

# Command for users to view working DM messages
@bot.command()
async def view_dm_messages(ctx):
    """Users view all working messages in DM."""
    data = load_messages()
    working_messages = [msg["content"] for msg in data["messages"] if msg["status"] == "working"]
    if working_messages:
        await ctx.send("\n".join(working_messages))
    else:
        await ctx.send("No messages available.")

# Command to vote on whether a message is working or expired
@bot.command()
async def vote_message(ctx, message_id: int, vote: str):
    """Vote on a message status ('working' or 'not_working')."""
    data = load_messages()
    message = next((msg for msg in data["messages"] if msg["id"] == message_id), None)
    
    if not message:
        await ctx.send("Message not found.")
        return

    if vote not in ["working", "not_working"]:
        await ctx.send("Vote should be 'working' or 'not_working'")
        return

    message["votes"][vote] += 1

    # If enough votes mark it as "not working," send to pending_verification
    if message["votes"]["not_working"] >= 3 and message["status"] == "working":
        message["status"] = "pending_verification"
        message["reported_by"].append(ctx.author.name)
        
        # Notify admin for verification
        admin_user = await bot.fetch_user(ADMIN_ID)
        await admin_user.send(f"Message ID {message_id} reported as 'not working' by {ctx.author}. Please verify.")
    
    save_messages(data)
    await ctx.send(f"Your vote has been recorded for message ID {message_id}.")

# Command for admin to verify reported messages
@bot.command()
async def verify_message(ctx, message_id: int, action: str):
    """Admin verifies reported messages (approve or delete)."""
    data = load_messages()
    message = next((msg for msg in data["messages"] if msg["id"] == message_id), None)
    
    if not message or message["status"] != "pending_verification":
        await ctx.send("Message not found or not pending verification.")
        return

    if action == "approve":
        message["status"] = "working"
        await ctx.send(f"Message ID {message_id} approved as 'working'.")
    elif action == "delete":
        data["messages"] = [msg for msg in data["messages"] if msg["id"] != message_id]
        await ctx.send(f"Message ID {message_id} has been deleted.")
    else:
        await ctx.send("Action must be 'approve' or 'delete'.")

    save_messages(data)

# Error handler for missing permissions
@add_dm_message.error
async def add_dm_message_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("Only the owner can add messages.")

@verify_message.error
async def verify_message_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to verify messages.")

# Run the bot
bot.run(TOKEN)