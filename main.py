import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os

# Ensure intents are enabled
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Enable the privileged message content intent
intents.guilds = True

# Define the bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Path to the JSON file to store messages
messages_file_path = 'messages.json'
user_id = 1041574639845003366  # Your User ID

# Load messages from the JSON file
def load_messages():
    if not os.path.exists(messages_file_path):
        return []
    with open(messages_file_path, 'r') as f:
        return json.load(f)

# Save messages to the JSON file
def save_messages(messages):
    with open(messages_file_path, 'w') as f:
        json.dump(messages, f)

# Add a message to the JSON file
@bot.command(name="addcrunchyroll")
async def add_crunchyroll(ctx, *, message: str):
    if ctx.author.id != user_id:  # Check if the author is the admin
        await ctx.send("You do not have permission to use this command.")
        return
    messages = load_messages()
    new_messages = message.split(',')  # Split multiple messages by comma
    messages.extend([msg.strip() for msg in new_messages])  # Add to list
    save_messages(messages)
    await ctx.send(f"Added messages: {', '.join(new_messages)}")

# View a random message
@bot.command(name="crunchyroll")
async def crunchyroll(ctx):
    messages = load_messages()
    if not messages:
        await ctx.send("No messages stored.")
        return

    # Choose a random message
    message = messages.pop(0)  # Show the first message for this example
    save_messages(messages)  # Save updated list
    view = View(timeout=None)

    # Create buttons for "Working" and "Expired"
    button_working = Button(label="Working", style=discord.ButtonStyle.success)
    button_expired = Button(label="Expired", style=discord.ButtonStyle.danger)

    async def button_working_callback(interaction: discord.Interaction):
        await interaction.response.send_message("You confirmed this message as working.")
    
    async def button_expired_callback(interaction: discord.Interaction):
        await interaction.response.send_message("You reported this message as expired.")
        # Notify admin or handle expiration logic here

    button_working.callback = button_working_callback
    button_expired.callback = button_expired_callback

    view.add_item(button_working)
    view.add_item(button_expired)

    await ctx.send(message, view=view)

# Start the bot
bot.run('MTI5MTY0MTE4NDE0NTUwNjMxNA.GrtsyG.DpbwJQLPh5CSib-7EeD6KFrb9knHX_owTkBOa4')  # Replace with your bot token