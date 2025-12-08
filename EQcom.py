import os
import discord, asyncio
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import random as r
from datetime import datetime

#------------------------------------------------ Basic Neccesities ------------------------------------------------------#
# Load Token
load_dotenv(".env")
TOKEN = os.getenv("TOKEN")

# Intents are permissions for the bot that are enabled based on the features necessary to run the bot
bot = commands.Bot(intents=discord.Intents.all(), command_prefix=TOKEN)

#------------------------------------------------ Presets ------------------------------------------------------#
# Members 
EQcom_id = 1372989774066876608
equinox_id = 882061427265921055
equinox_pfp = "https://cdn.discordapp.com/avatars/882061427265921055/d2dcf9ac35ef5a87677ce76d87811d4c.png?size=4096"
server_icon = "https://cdn.discordapp.com/attachments/935672317512650812/1373037472501731379/bright_logo.jpeg?ex=6828f44b&is=6827a2cb&hm=2a7fe3de4eb277a91041da88574ca11e212eba85b91a718d2c58ef27e7ad1612&"
equinox_community_server_id = 909605610641825842

# Channels
solstice_log_channel_id = 1032086398179737670
member_log_channel_id = 1081452487736832080
ask_for_help_unverified_channel_id = 934519651063443506
ask_for_help_verified_channel_id = 1029081817585831937
verify_instructions_channel_id = 934514301136408586
welcome_channel_id = 946184062337437717
exit_channel_id = 946184197628891166
bot_mailbox_channel_id = 1133886027057090560

# Roles
unverified_role_id = 934701008494399490
viewer_role_id = 1150880487976484895
verified_role_id = 934514425933725798
member_role_id = 909964707060940820
noob_role_id = 909900628350881812

# ------------------------------------------------------ Start Up ---------------------------------------------------#
# Bot activity status and custom status
@bot.event
async def on_ready():
    print("Equinox's Community Bot is online")

    # Sync the slash commands to Discord (necessary)
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except:
        print(f'Failed to sync slash commands')

    # Activity Status
    await bot.change_presence(status=discord.Status.online, activity = discord.Game(name = "🌵 The Wild West"))
        
# ------------------------------------------------------ Events ------------------------------------------------------#
@bot.event
async def on_message(message):

    # Return (ignore) if from bot
    if message.author.id == bot.user.id:
        return
    
    # Lowercase everything
    msg_content = message.content.lower()
    # Blacklisted words
    blacklisted_words = [word.strip() for word in (os.getenv("BLACKLISTED_WORDS", "").split(","))]
    # Randomize time to deletion
    time = r.randint(300, 5400) # Between 5 mins and 1.5 hrs
    minutes = int(time/60)
    
    # Delete if the words match blacklisted word list
    if any(word in msg_content for word in blacklisted_words):
        print(f'Will delete message from {message.author} in {minutes} minutes. Message content: {msg_content}')
        try:
            await asyncio.sleep(time)
            await message.delete()
            print(f'Deleted message from {message.author}. Message content: {msg_content}')
        except discord.NotFound:
            print(f"Message already deleted: {message.content}")
        except discord.Forbidden:
            print(f"Missing permissions to delete message from {message.author}")
        except Exception as e:
            print(f"Error deleting message: {e}")

    # Redirect all DMs sent to bot to Discord channel
    if isinstance(message.channel, discord.DMChannel):
        if message.author.id == EQcom_id:
            return  # Ignore bot's own DMs

        channel = bot.get_channel(bot_mailbox_channel_id)
        await channel.send(f"{message.author.id}") # Plain text ID for quick copying on mobile

        # Embed for messages received by Bot
        mail_embed = discord.Embed(title = "📮 Dm Received", colour = discord.Color.from_rgb(226,226,226))
        mail_embed.add_field(name = f"DM received from {message.author.name}", value = (f"{message.content}"))
        mail_embed.set_thumbnail(url=message.author.display_avatar.url)
        mail_embed.set_footer(text=f"ID: {message.author.id}") # User's ID in footer
        mail_embed.timestamp = datetime.now() # Timestamp of when event occured

        # Handle GIFs, set to None if no GIFs
        gif_content = None
        if "https://tenor.com/view/" in message.content:
            gif_content = message.content

        # Handle attachments
        if message.attachments:
            urls = [att.url for att in message.attachments]

            # Show as embed image if there's only one image attachment
            if len(urls) == 1 and urls[0].endswith(('.jpg', '.jpeg', '.png', '.gif')):
                mail_embed.set_image(url=urls[0])
            else:
                urls = urls[:50] # Limit to 50 attachments
                chunk_size = 10

                for i in range(0, len(urls), chunk_size):
                    chunk = urls[i:i + chunk_size]
                    field_content = "\n".join(f"{i + j + 1}. {url}" for j, url in enumerate(chunk))
                    mail_embed.add_field(name=f"Attachments ({i + len(chunk)})", value=field_content, inline=False)

        # Send the embed
        await channel.send(embed=mail_embed)

        # Send GIF link separately (if needed)
        if gif_content:
            await channel.send(gif_content)

    # End of on_message section
    await bot.process_commands(message) # Commands fix

@bot.event
async def on_member_remove(member):
    try:
        # Check if server is Equinox's Community
        if member.guild.id != equinox_community_server_id:
            return
        
        print(f"User left. Name: {member.name} ID: {member.id}")

        # Send exit message
        exit_channel = bot.get_channel(exit_channel_id)
        await exit_channel.send(f"**{member.name}** just left the server")

    # Member left or other Error
    except discord.NotFound:
        print(f"Member not found. Name: {member.name} ID: {member.id}")
        return
    except Exception as e:
        print(f"Error {member.name} ({member.id}) left server: {e}")
        return

# Verification roles & Member updating section
@bot.event
async def on_member_join(member):
    print(f"User joined. Name: {member.name} ID: {member.id}")

    # Check if server is Equinox's Community
    if member.guild.id != equinox_community_server_id:
        return

    # Send welcome message and DM embed
    welcome_channel = bot.get_channel(welcome_channel_id)
    await welcome_channel.send(f"Hey {member.mention}, welcome to **{member.guild.name}**!")

    try:
        log_embed = discord.Embed(title = "Welcome to Equinox's Community", colour = discord.Color.from_rgb(13, 115, 237))
        log_embed.set_thumbnail(url = member.guild.icon.url)
        log_embed.add_field(name = "", value = f"There are a few steps you have to complete before getting full access to the server.\n\n"
                            f"1. Verify your Roblox account through Bloxlink. More info can be found in <#{verify_instructions_channel_id}>. Bloxlink links your Roblox account to your Discord account (no Roblox login info is needed).\n\n"
                            "2. Head over to the rules channel and read through them. Once you have completed that, click the ✅ at the bottom agreeing to them. You will not be able to see or accept the rules until step 1 is complete.\n\n"
                            f"🎉 Congrats you are now a Member and have full access to the Discord Server. Have a great time here in **{member.guild.name}**!", inline = False)

        await member.send(embed=log_embed)
        await asyncio.sleep(2)

    except Exception as e:
        print(f"Unable to send welcome DM to {member}: {e}")

    # Roles & Channels
    noob_role = discord.utils.get(member.guild.roles, id=noob_role_id)
    member_role = discord.utils.get(member.guild.roles, id=member_role_id)
    verified_role = discord.utils.get(member.guild.roles, id=verified_role_id)
    viewer_role = discord.utils.get(member.guild.roles, id=viewer_role_id)
    unverified_role = discord.utils.get(member.guild.roles, id=unverified_role_id)

    # Add Unverified Role
    if unverified_role not in member.roles:
        await member.add_roles(unverified_role) # Adds Unverified
        await role_log_embed(1, "Unverified", member) # Send embed
    
    # Count iterations, so loop does not run forever
    iteration_counter = 0

    # Loop until user has verified & member roles
    while ((verified_role not in member.roles) or (member_role not in member.roles) or (unverified_role in member.roles) or (viewer_role in member.roles)) or iteration_counter <= 10000:
        await asyncio.sleep(30) # Cooldown

        try:
            # Has Noob role
            if noob_role in member.roles:

                # Does not have Member role
                if member_role not in member.roles: 
                    await member.add_roles(member_role) # Adds Member
                    await role_log_embed(1, "Member", member) # Send embed

                if verified_role not in member.roles:
                    await member.add_roles(verified_role) # Adds Verified
                    await role_log_embed(1, "Verified", member) # Send embed

                # Has Unverified role
                if unverified_role in member.roles:
                    await member.remove_roles(unverified_role) # Removes Unverified
                    await role_log_embed(0, "Unverified", member) # Send embed

                # Has Viewer role
                if viewer_role in member.roles:
                    await member.remove_roles(viewer_role) # Removes Viewer
                    await role_log_embed(0, "Viewer", member) # Send embed

            # Has Member role
            elif member_role in member.roles:

                # Does not have Verified role
                if verified_role not in member.roles:
                    await member.add_roles(verified_role) # Adds Verified
                    await role_log_embed(1, "Verified", member) # Send embed

                # Has Unverified role
                if unverified_role in member.roles:
                    await member.remove_roles(unverified_role) # Removes Unverified
                    await role_log_embed(0, "Unverified", member) # Send embed

                # Has Viewer role
                if viewer_role in member.roles:
                    await member.remove_roles(viewer_role) # Removes Viewer
                    await role_log_embed(0, "Viewer", member) # Send embed

            # Has Verified role
            elif verified_role in member.roles:
                await asyncio.sleep(60) # Cooldown (To read rules)

                # Does not have Member role
                if member_role not in member.roles:
                    await member.add_roles(member_role) # Adds Member
                    await role_log_embed(1, "Member", member) # Send embed

                # Has Unverified role
                if unverified_role in member.roles:
                    await member.remove_roles(unverified_role) # Removes Unverified
                    await role_log_embed(0, "Unverified", member) # Send embed

                # Has Viewer role
                if viewer_role in member.roles:
                    await member.remove_roles(viewer_role) # Removes Viewer
                    await role_log_embed(0, "Viewer", member) # Send embed
                    
            # Has Unverified role
            elif unverified_role in member.roles:

                # Does not have Viewer role
                if viewer_role not in member.roles:
                    await member.add_roles(viewer_role) # Adds Viewer
                    await role_log_embed(1, "Viewer", member) # Send embed

        # Member left or other Error
        except discord.NotFound:
            print(f"Member not found. Name: {member.name} ID: {member.id}")
            return
        except Exception as e:
            print(f"Error updating verification roles for {member.name} ({member.id}): {e}")
            return
        
        # Increment iteration counter
        iteration_counter+=1

    if iteration_counter >= 10000:
        # Loop ended because of timeout
        print(f"Verification process timeout. Name: {member.name} ID: {member.id}")
    else:
        # Loop ended, verification process complete
        print(f"User completed verification process. Name: {member.name} ID: {member.id}")

# Notice when a new role is given to a Member
@bot.event
async def on_member_update(before, after):

    # Check if server is Equinox's Community
    if after.guild.id != equinox_community_server_id:
        return
    
    # Roles & Channels
    member_role = discord.utils.get(after.guild.roles, id=member_role_id)
    verified_role = discord.utils.get(after.guild.roles, id=verified_role_id)
    viewer_role = discord.utils.get(after.guild.roles, id=viewer_role_id)
    unverified_role = discord.utils.get(after.guild.roles, id=unverified_role_id)
    channel = bot.get_channel(solstice_log_channel_id)

    if len(before.roles) < len(after.roles):
        added_role = next((role for role in after.roles if role not in before.roles), None)

        try:
            # StopIteration error fix 
            if not added_role:
                return

            # Viewer role recieved, send message to assist with verification
            elif added_role.name == 'Viewer':
                await asyncio.sleep(5)
                channel = bot.get_channel(ask_for_help_unverified_channel_id)
                msg_sent = await channel.send(f"Welcome to Equinox's Community, {after.mention}! It looks like you don’t have full Member permissions yet. To unlock additional access, please complete verification with Bloxlink. You’ll find step-by-step instructions in <#{verify_instructions_channel_id}>")
                await asyncio.sleep(10800) # 3 Hours
                await msg_sent.delete()

            # Verified role recieved, now update roles
            elif added_role.name == 'Verified':
                await asyncio.sleep(120) # Cooldown (from verification process)

                # Does not have Member role
                if member_role not in after.roles:
                    await after.add_roles(member_role) # Adds Member
                    await role_log_embed(1, "Member", after) # Send embed
                # Has Unverified role
                if unverified_role in after.roles:
                    await after.remove_roles(unverified_role) # Removes Unverified
                    await role_log_embed(0, "Unverified", after) # Send embed
                # Has Viewer role
                if viewer_role in after.roles:
                    await after.remove_roles(viewer_role) # Removes Viewer
                    await role_log_embed(0, "Viewer", after) # Send embed

                print(f"User verification process auto-completed. Name: {after.name} ID: {after.id}")

            # Member role recieved, now update roles
            elif added_role.name == 'Member':
                await asyncio.sleep(120) # Cooldown (from verification process)

                # Does not have Verified role
                if verified_role not in after.roles:
                    await after.add_roles(verified_role) # Adds Verified
                    await role_log_embed(1, "Verified", after) # Send embed

                # Has Unverified role
                if unverified_role in after.roles:
                    await after.remove_roles(unverified_role) # Removes Unverified
                    await role_log_embed(0, "Unverified", after) # Send embed

                # Has Viewer role
                if viewer_role in after.roles:
                    await after.remove_roles(viewer_role) # Removes Viewer
                    await role_log_embed(0, "Viewer", after) # Send embed

                # Rules Accepted and Member role given to ask-for-help
                rules_askforhelp_channel = bot.get_channel(ask_for_help_verified_channel_id)
                await rules_askforhelp_channel.send((f"{after.mention} has accepted the rules"))

                print(f"User verification process auto-completed. Name: {after.name} ID: {after.id}")

        except Exception as e:
            print(f"Error tracking {after.mention} roles: {e}")
    
    if len(before.roles) > len(after.roles):
        removed_role = next((role for role in before.roles if role not in after.roles), None)

        try:
            # StopIteration error fix
            if removed_role is None:
                return

            # Member role removed, update roles accordingly
            elif removed_role.name == 'Member':
                await asyncio.sleep(120) # Cooldown

                # Has Verified role, Re-add Member role
                if verified_role in after.roles and member_role not in after.roles:
                    await after.add_roles(member_role) # Adds Member
                    await role_log_embed(1, "Member", after) # Send embed

            elif removed_role.name == 'Verified':
                await asyncio.sleep(120) # Cooldown

                # Has Member role
                if member_role in after.roles:
                    await after.remove_roles(member_role) # Removes Member
                    await role_log_embed(0, "Member", after) # Send embed

                # Does not have Unverified role
                if unverified_role not in after.roles:
                    await after.add_roles(unverified_role) # Adds Unverified
                    await role_log_embed(1, "Unverified", after) # Send embed

                # Does not have Viewer role
                if viewer_role not in after.roles:
                    await after.add_roles(viewer_role) # Adds Viewer
                    await role_log_embed(1, "Viewer", after) # Send embed

        except Exception as e:
            print(f"Error tracking {after.mention} roles: {e}")

#------------------------------------------------ Slash Commands ------------------------------------------------------#
tree = app_commands.CommandTree

# Makes the is_owner requirement to be used in slash commands
def is_owner():
    def predicate(interaction : discord.Interaction):
        if interaction.guild and interaction.user.id == interaction.guild.owner_id:
            return True
    return app_commands.check(predicate)

# /ping - Check the bot's latency
@bot.tree.command(name = "ping", description = "Check the bot's latency")
@is_owner()
async def ping(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral = True)  # Extend timeout

    embed = discord.Embed()
    embed.set_author(name = f"Ping: {round(bot.latency * 1000)}ms", icon_url = "https://cdn.discordapp.com/attachments/935672317512650812/1155259162553503864/Ping_Icon.png") 
    await interaction.followup.send(embed=embed, ephemeral=True)

# /say - Make the bot say something
@bot.tree.command(name = "say", description = "Make the bot say something")
@app_commands.describe(message = "The message you want the bot to repeat", channel = "Optional: Channel to send the message in")
@is_owner()
async def say(interaction: discord.Interaction, message: str, channel: discord.TextChannel = None):
    await interaction.response.defer(ephemeral = True)  # Extend timeout

    # Use selected or current channel
    target_channel = channel or interaction.channel
    try:
        await target_channel.send(message)
        await interaction.followup.send(f"Message sent in {target_channel.mention}", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("I don't have permission to send messages in that channel.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Failed to send message: {e}", ephemeral=True)

# /dm - Send a DM through the bot
@bot.tree.command(name = "dm", description = "Send a DM through the bot")
@app_commands.describe(user = "The user to DM", message = "The message the bot will send")
@is_owner()
async def dm(interaction: discord.Interaction, user: discord.User, message: str):
    await interaction.response.defer(ephemeral = True)  # Extend timeout

    # Send the DM
    try:
        await user.send(message)
        await interaction.followup.send(f"DM successfully sent to {user.mention}", ephemeral=True)

        # Send embed to log channel
        log_channel = bot.get_channel(bot_mailbox_channel_id)
        log_embed = discord.Embed(title = "📧 DM Sent", colour = 0x3498db)
        log_embed.add_field(name = f"DM sent by Equinox's Community to {user.name}", value = (f"{message}"))
        log_embed.set_thumbnail(url=bot.user.display_avatar.url)
        log_embed.set_footer(text=f"ID: {user.id}")
        log_embed.timestamp = datetime.now()
        await log_channel.send(f"{user.id}")
        await log_channel.send(embed = log_embed)
        
    except (discord.Forbidden, discord.HTTPException):
        await interaction.followup.send(f"Unable to send DM to to {user.mention}", ephemeral=True)

# /accept-rules - Give a verified user the member role
@bot.tree.command(name = "accept-rules", description = "Accept the server rules")
async def acceptrules(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral = False)  # Extend timeout

    # User is not verified
    if not any(role.id == verified_role_id for role in interaction.user.roles):
        await interaction.followup.send(f"You must have the <@&{verified_role_id}> role to use this command.", ephemeral=True)
        return

    # User already has the member role
    elif any(role.id == member_role_id for role in interaction.user.roles):
        await interaction.followup.send(f"You have already accepted the rules.", ephemeral=True)
        return

    # User is able to accept rules
    else:
        member_role = discord.utils.get(interaction.guild.roles, id=member_role_id)
        await interaction.user.add_roles(member_role)
        await role_log_embed(1, "Member", interaction.user)
        await interaction.followup.send("✅ You have accepted the rules!", ephemeral=False)

# /unverified-dm - Send a DM through the bot
@bot.tree.command(name = "unverified-dm", description = "Send a DM to all Unverified members")
@is_owner()
async def dmunverified(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral = True) # Extend timeout
    asyncio.create_task(process_unverified_dms(interaction, interaction.guild)) # Create background task

# Run background task, so interaction does not fail
async def process_unverified_dms(interaction: discord.Interaction, guild: discord.Guild):
    status_message = await interaction.channel.send("<a:loading:1374067466107359303> Sending DMs to all Unverified users")
    role = discord.utils.get(guild.roles, id = unverified_role_id)

    # Counters
    sent_count = 0
    failed_count = 0

    # Loop through all server members, sending DM if they are unverified
    for member in guild.members:
        if role in member.roles:
            await asyncio.sleep(15) # Cooldown (Don't want bot to get banned)
            try:
                log_embed = discord.Embed(title = f"👋 Hello {member.display_name.capitalize()},", colour = discord.Color.from_rgb(13, 115, 237))
                log_embed.set_thumbnail(url = guild.icon.url)
                log_embed.add_field(name = "", value = f"I noticed you are still unverified in Equinox's Community even though you joined the server on {member.joined_at.strftime('%m/%d/%y')}.", inline = False)
                log_embed.add_field(name = "Here are some steps to help you get verified:", value = f"1. Check <#{verify_instructions_channel_id}> for steps on verifying with Bloxlink.", inline = False)
                log_embed.add_field(name = "", value = ("2. Watch these videos from Bloxlink:\n"
                            "<:YouTube:1374526830995832853> https://www.youtube.com/watch?v=SbDltmom1R8&t=0s\n"
                            "<:YouTube:1374526830995832853> https://www.youtube.com/watch?v=RhC8AIv1Mfk&t=0s"), inline = False)
                log_embed.add_field(name = "", value = f"3. Ping <@{equinox_id}> in <#{ask_for_help_unverified_channel_id}> for help with verification.", inline = False)
                log_embed.add_field(name = "", value = "**Until you verify, your permissions will be limited and you will be unable to participate in Giveaways.**", inline = False)
                log_embed.set_footer(text="Message sent from Equinox's Community")
                log_embed.timestamp = datetime.now()

                await member.send(embed=log_embed)
                sent_count += 1

            except Exception as e:
                failed_count += 1
                print(f"Unable to send DM to {member}: {e}")
                continue
            
            # Update status message every 10 iterations
            if (sent_count + failed_count) % 10 == 0:
                try:
                    await status_message.edit(content = f"<a:loading:1374067466107359303> Sending DMs | Sent: {sent_count} | Failed: {failed_count}")
                except Exception as e:
                    print(f"Failed to update status message: {e}")

    # Send final status message
    await status_message.edit(content = f"📨 Finished sending DMs | Sent: {sent_count} | Failed: {failed_count}")

# /update-all - Send a DM through the bot
@bot.tree.command(name = "update-all", description = "Update all members' roles")
@is_owner()
async def updateall(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    asyncio.create_task(process_updateall(interaction, interaction.guild))

# Run background task, so interaction does not fail
async def process_updateall(interaction: discord.Interaction, guild: discord.Guild):
    status_message = await interaction.channel.send("<a:loading:1374067466107359303> Updating all members...")

    # Counter
    updated_count = 0

    # Define roles
    noob_role = discord.utils.get(guild.roles, id=noob_role_id)
    member_role = discord.utils.get(guild.roles, id=member_role_id)
    verified_role = discord.utils.get(guild.roles, id=verified_role_id)
    viewer_role = discord.utils.get(guild.roles, id=viewer_role_id)
    unverified_role = discord.utils.get(guild.roles, id=unverified_role_id)

    # Loop through all server members, updating roles
    for member in guild.members:
        changed = False

        try:
            if noob_role in member.roles:
                if member_role not in member.roles:
                    await member.add_roles(member_role)
                    await role_log_embed(1, "Member", member)
                    changed = True

                if verified_role not in member.roles:
                    await member.add_roles(verified_role)
                    await role_log_embed(1, "Verified", member)
                    changed = True

                if unverified_role in member.roles:
                    await member.remove_roles(unverified_role)
                    await role_log_embed(0, "Unverified", member)
                    changed = True

                if viewer_role in member.roles:
                    await member.remove_roles(viewer_role)
                    await role_log_embed(0, "Viewer", member)
                    changed = True

            elif member_role in member.roles:
                if verified_role not in member.roles:
                    await member.add_roles(verified_role)
                    await role_log_embed(1, "Verified", member)
                    changed = True

                if unverified_role in member.roles:
                    await member.remove_roles(unverified_role)
                    await role_log_embed(0, "Unverified", member)
                    changed = True

                if viewer_role in member.roles:
                    await member.remove_roles(viewer_role)
                    await role_log_embed(0, "Viewer", member)
                    changed = True

            elif verified_role in member.roles:
                if member_role not in member.roles:
                    await member.add_roles(member_role)
                    await role_log_embed(1, "Member", member)
                    changed = True

                if unverified_role in member.roles:
                    await member.remove_roles(unverified_role)
                    await role_log_embed(0, "Unverified", member)
                    changed = True

                if viewer_role in member.roles:
                    await member.remove_roles(viewer_role)
                    await role_log_embed(0, "Viewer", member)
                    changed = True

            elif unverified_role in member.roles:
                if viewer_role not in member.roles:
                    await member.add_roles(viewer_role)
                    await role_log_embed(1, "Viewer", member)
                    changed = True

            if changed:
                updated_count += 1
                await asyncio.sleep(2)

        except Exception as e:
            print(f"Error updating {member}: {e}")
            continue

        # Update status message every 10 iterations
        if updated_count % 10 == 0:
            try:
                await status_message.edit(content = f"<a:loading:1374067466107359303> Updating members | Total updated: {updated_count}")
            except Exception as e:
                print(f"Error editing status message: {e}")

    # Send final status message
    await status_message.edit(content = f"✅ Finished updating members | Total updated: {updated_count}")

# /log-members - Send a DM through the bot
@bot.tree.command(name = "log-members", description = "Log all members' roles")
@is_owner()
async def logmembers(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    asyncio.create_task(process_logmembers(interaction, interaction.guild))

# Run background task, so interaction does not fail
async def process_logmembers(interaction: discord.Interaction, guild: discord.Guild):

    # Variables
    channel = bot.get_channel(member_log_channel_id)  # Your log channel
    total_members = len(guild.members)
    counter = 0
    update_threshold = 5

    status_message = await interaction.channel.send(f"📋 Logging started...")

    # Loop through all server members, updating roles
    for member in guild.members:
        await asyncio.sleep(2) # Cooldown

        # Embed Message
        logging = discord.Embed(title = '', description = f'{member.mention}', colour = discord.Color.from_rgb(46, 164, 255)) # Member's name and embed color
        logging.set_author(name = f"{member}", icon_url = str(member.display_avatar)) # Member's ID at top
        roles = [role.mention for role in member.roles[1:]]
        num_of_roles = (str(len(roles)))
        roles = (" ".join(roles))
        logging.add_field(name = 'Account Created:', value = f'{member.created_at.strftime("%m/%d/%y")}', inline = True) # Discord join date
        logging.add_field(name = 'Joined Server:', value = f'{member.joined_at.strftime("%m/%d/%y")}', inline = True) # Server join date
        logging.add_field(name = f'<:check:1374528468615823413> Roles [{num_of_roles}]', value = f"{roles}", inline = False) # List out the member's roles
        logging.set_footer(text=f"{member.id}") # Text + ID in footer
        logging.timestamp = datetime.now() # Timestamp of when event occured
        await channel.send(embed = logging)

        # Counter system
        counter +=1
        if counter % update_threshold == 0:
            await status_message.edit(content = f"**<a:loading:1374067466107359303> {counter} out of {total_members} currently logged.**")

    # Send final status message
    await status_message.edit(content = "📋 **Finished logging all Members.**")

# ------------------------------------------------------ Embed Logs ----------------------------------------------#
# Embed for verification process (1 = Add, 0 = Remove)
async def role_log_embed(arg, role_name, member):
    channel = bot.get_channel(solstice_log_channel_id)
    
    # Embed log for removed role
    if arg == 0:
        role_embed = discord.Embed(title = f"⛔️ {role_name} Role Removed", colour = 0xe74c3c)
        role_embed.add_field(name = "Information:", value = (f"I removed the {role_name} role from {member.mention}"))
        role_embed.set_footer(text=f"ID: {member.id}")
        role_embed.timestamp = datetime.now()
        await channel.send(embed = role_embed)
        print(f"I removed the {role_name} role from {member.name}. ID: {member.id}")

    # Embed log for added role
    elif arg == 1:
        role_embed = discord.Embed(title = f"✅ {role_name} Role Added", colour = 0x2ecc71)
        role_embed.add_field(name = "Information:", value = (f"I gave {member.mention} the {role_name} role"))
        role_embed.set_footer(text=f"ID: {member.id}")
        role_embed.timestamp = datetime.now()
        await channel.send(embed = role_embed)
        print(f"I added the {role_name} role to {member.name}. ID: {member.id}")

# Embed for errors
async def error_warning(ctx, message):
    warning_embed_icon = "https://cdn.discordapp.com/attachments/935672317512650812/1154896305320112139/warning_2.png"
    warning_embed_color = discord.Color.from_rgb(255,50,50)

    # Send warning embed
    warning_embed = discord.Embed(colour = warning_embed_color)
    warning_embed.set_author(name = message, icon_url = warning_embed_icon) 
    warning_msg = await ctx.send(embed = warning_embed)
    await asyncio.sleep(10)
    await warning_msg.delete()

# Embed for slash command used
@bot.event
async def on_app_command_completion(interaction: discord.Interaction, command: app_commands.Command):
    channel = bot.get_channel(solstice_log_channel_id)

    # Log embed
    embed = discord.Embed(title = "Slash Command Used", colour = 0xf1c40f)
    embed.set_author(name = f"{interaction.user.name}", icon_url = interaction.user.display_avatar.url)
    embed.set_thumbnail(url = interaction.user.display_avatar.url)
    embed.add_field(name="Command", value=f"`/{interaction.command.name}`", inline=False)
    embed.add_field(name="Channel", value=interaction.channel.mention if interaction.channel else "DM", inline=False)
    embed.set_footer(text=f"Author ID: {interaction.user.id}") # Author's ID in footer
    embed.timestamp = datetime.now() # Timestamp of when event occured

    await channel.send(embed=embed)

# Embed for slash command error
@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    channel = bot.get_channel(solstice_log_channel_id)
    
    # Log embed
    embed = discord.Embed(title = "Slash Command Error", colour = 0xf1c40f)
    embed.set_author(name = f"{interaction.user.name}", icon_url = interaction.user.display_avatar.url)
    embed.set_thumbnail(url = interaction.user.display_avatar.url)
    embed.add_field(name="Command", value=f"`/{interaction.command.name}`", inline=False)
    embed.add_field(name="Channel", value=interaction.channel.mention if interaction.channel else "DM", inline=False)
    embed.add_field(name="Error Message", value=f"`{str(error)}`", inline=False)
    embed.set_footer(text=f"Author ID: {interaction.user.id}") # Author's ID in footer
    embed.timestamp = datetime.now() # Timestamp of when event occured

    await channel.send(embed=embed)

#------------------------------------------------ Error Messages ------------------------------------------------------#

@bot.event
async def on_command_error(ctx, error):
    print("Running Errors Section")

    # Cooldown error (deletes command)
    if isinstance(error, commands.CommandOnCooldown):
        error_msg_1 = "This command is on cooldown, please try again in {:.0f} seconds.".format(error.retry_after)
        await ctx.message.delete()
        print(f"Error 1, cooldown: {error}")
        await error_warning(ctx, error_msg_1)

    # Missing role error (deletes command)
    elif isinstance(error, commands.MissingRole):
        error_msg_2 = "You do not have the role needed to run this command."
        await ctx.message.delete()
        print(f"Error 2, missing role: {error}")
        await error_warning(ctx, error_msg_2)

    # Missing permissions error (deletes command)
    elif isinstance(error, commands.MissingPermissions):
        error_msg_3 = "You do not have the permissions needed to run this command."
        await ctx.message.delete()
        print(f"Error 3, missing permissions: {error}")
        await error_warning(ctx, error_msg_3)

    # Missing argument error (deletes command)
    elif isinstance(error, commands.MissingRequiredArgument):
        error_msg_4 = "You did not provide a required argument needed to run this command."
        await ctx.message.delete()
        print(f"Error 4, missing argument: {error}")
        await error_warning(ctx, error_msg_4)
    
    # Invalid command (ignore)
    elif isinstance(error, commands.CommandNotFound):
        error_msg_5 = "Command does not exist."
        await ctx.message.delete()
        print(f"Error 5, invalid command: {error}")
        await error_warning(ctx, error_msg_5)

    # Bot missing permissions error
    elif isinstance(error, commands.BotMissingPermissions):
        bot_error_msg_1 = "I do not have the permissions needed to run this command."
        await ctx.message.delete()
        print(f"Bot Error 1, missing permissions: {error}")
        await error_warning(ctx, bot_error_msg_1)

    # Bot missing role error
    elif isinstance(error, commands.BotMissingRole):
        bot_error_msg_2 = "I do not have the role needed to run this command."
        await ctx.message.delete()
        print(f"Bot Error 2, missing role: {error}")
        await error_warning(ctx, bot_error_msg_2)
    
    # There was an undefined Error
    else:
        await error_warning(ctx, "There was an error performing this action.")

# ------------------------------------------------------ TESTING ----------------------------------------------#
## PURGE COMMAND
@bot.tree.command(name = "purge", description = "Mass delete recent messages from a specific user")
@app_commands.describe(member = "The member whose messages you want to delete", limit = "Number of messages to delete (max 30)")
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, member: discord.Member, limit: int):
    await interaction.response.defer(ephemeral=True)
    max_purge = 35

    # Adjust limit if needed
    attempted = limit
    if limit > max_purge:
        limit = max_purge

    messages_to_delete = []
    async for message in interaction.channel.history(limit = 250):
        if message.author == member:
            messages_to_delete.append(message)
        if len(messages_to_delete) >= limit:
            break

    if not messages_to_delete:
        await interaction.followup.send("No messages found to delete.", ephemeral=True)
        return

    await interaction.channel.delete_messages(messages_to_delete)

    await interaction.followup.send(
        f"✅ Deleted {len(messages_to_delete)} message(s) from {member.mention} (attempted {attempted}).",
        ephemeral=True
    )
# ------------------------------------------------------ Running the Bot ----------------------------------------------#

# Run the Bot
bot.run(TOKEN)