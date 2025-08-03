
import discord
from discord.ext import commands, tasks
from discord.utils import get
import os
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = YOUR_GUILD_ID  # Replace with your actual Guild ID (integer)
FORM_CHANNEL_ID = YOUR_FORM_CHANNEL_ID  # Channel where private threads are created
VR_CHANNEL_ID = YOUR_VR_CHANNEL_ID  # Channel where staff reviews verification forms
NSFW_ROLE_ID = YOUR_NSFWR_ROLE_ID  # ID of NSFW Verified Role

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    change_status.start()

# Rotating status
statuses = ["🔞 Awaiting brave souls...", "🍒 Click to verify", "👀 Watching for NSFW explorers"]
@tasks.loop(minutes=5)
async def change_status():
    await bot.change_presence(activity=discord.Game(name=statuses[change_status.current_loop % len(statuses)]))

# Command to post the Verify Button Embed
@bot.command()
async def post_verify(ctx):
    embed = discord.Embed(title="NSFW Verification Required", description="To access NSFW sections, click the button below to verify.", color=discord.Color.red())
    view = discord.ui.View()
    button = discord.ui.Button(label="🔞 Verify Me", style=discord.ButtonStyle.primary, custom_id="nsfw_verify_button")
    view.add_item(button)
    await ctx.send(embed=embed, view=view)

# Handle button interaction
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data["custom_id"] == "nsfw_verify_button":
            guild = bot.get_guild(GUILD_ID)
            form_channel = guild.get_channel(FORM_CHANNEL_ID)
            thread = await form_channel.create_thread(name=f"NSFW Verify - {interaction.user.display_name}", type=discord.ChannelType.private_thread, invitable=False)
            await thread.add_user(interaction.user)
            await thread.send(f"Hello {interaction.user.mention}, please answer the following questions for NSFW verification:")

            questions = [
                "1. What is your Discord username and ID?",
                "2. How old are you?",
                "3. Do you consent to seeing NSFW content? (Yes/No)",
                "4. Have you read and agreed to the NSFW rules? (Yes/No)",
                "5. Please upload a screenshot showing your age (blur everything else)."
            ]

            for q in questions:
                await thread.send(q)

            await interaction.response.send_message("I've created a private verification thread for you. Please check!", ephemeral=True)

# Staff can manually approve via command in VR Channel
@bot.command()
@commands.has_permissions(manage_roles=True)
async def approve(ctx, member: discord.Member):
    nsfw_role = get(ctx.guild.roles, id=NSFW_ROLE_ID)
    await member.add_roles(nsfw_role)
    await member.send("Your NSFW verification has been approved. You now have access to NSFW sections of Lounge PH.")
    await ctx.send(f"{member.mention} has been approved and given the NSFW Verified role.")

# Staff can reject
@bot.command()
@commands.has_permissions(manage_roles=True)
async def reject(ctx, member: discord.Member):
    await member.send("Your NSFW verification has been rejected. Contact Moderators if you think this was a mistake.")
    await ctx.send(f"{member.mention}'s NSFW verification has been rejected.")

keep_alive()
bot.run(os.getenv('TOKEN'))
