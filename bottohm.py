import discord
from discord.ext import commands
import random
import asyncio
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.members = True
GUILD_ID = 1158256248827957300  # replace with your server ID
OWNER_ID = 1189246954950099128  # replace with YOUR Discord user ID
BOT_CHANNEL_ID = [1417127300918542486,1417127300918542486]
SWITCH_DELAY = 2

def get_prefix(bot, message):
    # Everyone can use "t"
    prefixes = ["t"]

    # Only owner can use "jarvis"
    if message.author and message.author.id == OWNER_ID:
        prefixes.append("jarvis ")

    return prefixes

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

# ----------------------

# Text-based Commands

# ----------------------

@bot.command()

async def permtest(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("Nah cuh u aint got no permission")
        return
    await ctx.send("Yeah cuh u rock")
@bot.command()

async def gay(ctx, target: discord.Member):
    if ctx.channel.id not in BOT_CHANNEL_ID:
        return  # silently ignore if not in the bot channel
    percent = random.randint(1, 100)
    await ctx.send(f"Mức độ gay của {target.mention} là {percent}%")

@bot.command()
async def punch(ctx, target: discord.Member):
    if ctx.channel.id not in BOT_CHANNEL_ID:
        return  # silently ignore if not in the bot channel
    await ctx.send(f"{ctx.author.mention} đã đấm vỡ mồm {target.mention}")

@bot.command()
async def reply(ctx, *, question):
    answers = [
        "Ok đc", "Có", "U não hay gì mà hỏi", "Có, rất có là đằng khác", "Đéo", "Cũng đc idk", "Hỏi ngu vl hỏi câu khác đê", 
        "Bố m cũng chịu", "Im mẹ mồm đi đừng hỏi nữa" , "Tuyệt đối óc chó, hỏi ngu vl" , "Câu hỏi rất hay, có" , "bruh <:damn:1415394717562048522> ",
        "Từ từ đang lọ", "Đang lọ chờ tí hỏi lúc khác đi", "Yé" , "Có" , "<:water:1158256693344485447> "
    ]
    await ctx.send(f"🎱 {ctx.author.mention}, {random.choice(answers)}")

@bot.command(name="say")
async def say(ctx, *, message: str = None):
    if ctx.author.id != OWNER_ID:
        return
    """
    Bot repeats your message (and attachments).
    - If used while replying: bot replies to that same message.
    - If mentions someone: bot just pings them in the text.
    - Otherwise: bot just says the text.
    """
    files = []
    for attachment in ctx.message.attachments:
        file = await attachment.to_file()
        files.append(file)

    target_message = ctx.message.reference  # check if user replied to someone

    if target_message:
        # User replied to a message → bot replies to the same one
        replied_msg = await ctx.channel.fetch_message(target_message.message_id)
        await replied_msg.reply(content=message, files=files, mention_author=False)
    else:
        # Normal say (with mentions included as plain text)
        if message or files:
            await ctx.send(content=message, files=files)
        else:
            await ctx.send("⚠️ Nothing to say!")

    # Clean up the command
    await ctx.message.delete()

# ----------------------

# Gambling commands

# ----------------------

# ----------------------

# Bet command

# ----------------------

# Track active luck per user
user_luck = {}  # user_id -> (multiplier, expires_at)
SLOT_COUNT_NORMAL = 13  # total slots for normal/unlucky roll
SLOT_COUNT_LUCKY = 11   # total slots for lucky 2× roll
SLOT_COUNT_UNLUCKY = 10 # total slots for unlucky roll

@bot.command()
async def bet(ctx):
    if ctx.channel.id not in BOT_CHANNEL_ID:
        return  # silently ignore if not in the bot channel
    user_id = ctx.author.id
    now = asyncio.get_event_loop().time()

    # Prevent stacking: user cannot use while effect active
    if user_id in user_luck:
        _, expires = user_luck[user_id]
        remaining = int(expires - now)
        if remaining > 0:
            await ctx.send(f"{ctx.author.mention}, chờ đê cu! Đợi {remaining} giây nhá")
            return
        else:
            del user_luck[user_id]  # remove expired

    # Roll for luck
    luck_roll = random.random()
    if luck_roll < 0.5:  # 50% chance lucky
        multiplier = 2      # double luck
        duration = 20       # 20 seconds
        await ctx.send(f"{ctx.author.mention} nhận may mắn! 2× luck trong {duration} giây 🍀")
    else:
        multiplier = 0.75   # unlucky
        duration = 60       # 60 seconds
        await ctx.send(f"{ctx.author.mention} nhọ vl, 0.75× luck trong {duration} giây <:troll:1416091220790345869>")

    expires_at = now + duration
    user_luck[user_id] = (multiplier, expires_at)

    # Auto-remove luck after duration
    async def remove_luck_later():
        await asyncio.sleep(duration)
        if user_id in user_luck and user_luck[user_id][1] <= asyncio.get_event_loop().time():
            del user_luck[user_id]

    asyncio.create_task(remove_luck_later())

# ----------------------

# Roll command

# ----------------------

@bot.command()
async def roll(ctx):
    if ctx.channel.id not in BOT_CHANNEL_ID:
        return  # silently ignore if not in the bot channel

    # Determine luck multiplier
    multiplier = 1
    slot_count = SLOT_COUNT_NORMAL
    user_id = ctx.author.id
    now = asyncio.get_event_loop().time()
    if user_id in user_luck:
        mult, expires = user_luck[user_id]
        if now < expires:
            multiplier = mult
            if multiplier > 1:
                slot_count = SLOT_COUNT_LUCKY  # lucky rolls fewer slots
            if multiplier < 1:
                slot_count = SLOT_COUNT_UNLUCKY  # unlucky rolls fewer slots
        else:
            del user_luck[user_id]

    # Base emojis
    base_emojis = ["🍒", "🍋", "💎"]

    # Adjust emoji pool based on luck
    if multiplier > 1:
        # Lucky → reduce emoji types to increase chance of all matching
        emoji_pool = base_emojis
    elif multiplier < 1:
        # Unlucky → increase emoji types to make jackpot harder
        emoji_pool = base_emojis + ["🍉", "🍊"]  # 5 total emojis
    else:
        emoji_pool = base_emojis

    # Create slots
    slots = [random.choice(emoji_pool) for _ in range(slot_count)]
    rolled_string = "".join(slots)

    # Check for jackpot: all slots are the same
    if all(slot == slots[0] for slot in slots):
        if multiplier > 1:
            # Lucky → Windfall role
            role_name = "Windfall (1 in 388k)"
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role:
                await ctx.author.add_roles(role)
                await ctx.send(
                    f"Rolled: {rolled_string}\n💰 {ctx.author.mention} roll trúng **{role.name}**"
                    f"\nVới tỉ lệ xảy ra là 1 trong 388,888.5!!! <:dante:1416229833607876628>"
                )
            else:
                await ctx.send(f"Rolled: {rolled_string}\nRole **{role_name}** đéo tồn tại...")

        elif multiplier < 1:
            # Unlucky → Grand Prize role
            role_name = "El Gran Premio (1 in 2M)"
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role:
                await ctx.author.add_roles(role)
                await ctx.send(
                    f"Rolled: {rolled_string}\n:boom: Nhọ vl, NHƯNG {ctx.author.mention} ĐÃ ROLL ĐƯỢC **{role.name}** KỂ CẢ KHI DÍNH CHƯỞNG!!!"
                    f"\nVới tỉ lệ xảy ra là 1 in 1,000,000!!! <:67:1419013396136722472>"
                )
            else:
                await ctx.send(f"Rolled: {rolled_string}\nRole **{role_name}** đéo tồn tại...")

        else:
            # Normal → Jackpot role
            role_name = "Jackpot (1 in 777k)"
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role:
                await ctx.author.add_roles(role)
                await ctx.send(
                    f"Rolled: {rolled_string}\n🎉 VL!!! {ctx.author.mention} đã roll được **{role.name}**"
                    f"\nVới tỉ lệ xảy ra là 1 trong 777,777!!! <:omg:1416412227828977766>"
                )
            else:
                await ctx.send(f"Rolled: {rolled_string}\nRole **{role_name}** đéo tồn tại...")
    else:
        await ctx.send(f"{ctx.author.mention} rolled: {rolled_string}\nHơi nhọ, thử lại đê")

# ----------------------

# Role boogie / end boogie command

# ----------------------

# Replace these with the actual Discord role IDs
BOOGIE_ROLE_1_ID = 1423865476336979998  # Poseidon? role ID
BOOGIE_ROLE_2_ID = 1423948584138834020  # Yellow Poseidon role ID
BOOGIE_ROLE_3_ID = 1424381421883101215  # Evil Poseidon role ID

boogie_task = None  # Track the background task

async def boogie_loop(guild):
    role1 = guild.get_role(BOOGIE_ROLE_1_ID)
    role2 = guild.get_role(BOOGIE_ROLE_2_ID)
    role3 = guild.get_role(BOOGIE_ROLE_3_ID)

    try:
        while True:
            member = await guild.fetch_member(OWNER_ID)

            # Step 1: Add role1
            await member.add_roles(role1)
            await asyncio.sleep(SWITCH_DELAY)

            # Step 2: Add role2
            await member.add_roles(role2)
            await member.remove_roles(role1)
            await asyncio.sleep(SWITCH_DELAY)

            # Step 3: Add role3
            await member.add_roles(role3)
            await member.remove_roles(role2)
            await asyncio.sleep(SWITCH_DELAY)

            # Step 4: Remove role3
            await member.remove_roles(role3)
            await asyncio.sleep(SWITCH_DELAY)

    except asyncio.CancelledError:
        # Cleanup
        member = await guild.fetch_member(OWNER_ID)
        for r in [role1, role2, role3]:
            if r in member.roles:
                try:
                    await member.remove_roles(r)
                except discord.HTTPException:
                    pass

@bot.command()
async def endboogie(ctx):
    global boogie_task, boogie_active
    if ctx.author.id != OWNER_ID:
        return  # silently ignore

    if boogie_task and not boogie_task.done():
        boogie_task.cancel()
        boogie_active = False  # make sure it won’t auto-resume
    else:
        await ctx.send(f"{ctx.author.mention}, lệnh có chạy đéo đâu mà dừng")
        
@bot.command()
async def resumeboogie(ctx):
    global boogie_task, boogie_active
    if ctx.author.id != OWNER_ID:
        return  # only you can use it

    if boogie_task and not boogie_task.done():
        await ctx.send(f"{ctx.author.mention}, boogie is already running!")
        return

    guild = ctx.guild
    role1 = guild.get_role(BOOGIE_ROLE_1_ID)
    role2 = guild.get_role(BOOGIE_ROLE_2_ID)
    role3 = guild.get_role(BOOGIE_ROLE_3_ID)

    if not role1 or not role2 or not role3:
        await ctx.send("❌ Một trong ba role đéo tồn tại")
        return

    async def boogie_loop(guild):
        try:
            while True:
                member = await guild.fetch_member(OWNER_ID)

                await member.add_roles(role1)
                await asyncio.sleep(SWITCH_DELAY)

                await member.add_roles(role2)
                await member.remove_roles(role1)
                await asyncio.sleep(SWITCH_DELAY)

                await member.add_roles(role3)
                await member.remove_roles(role2)
                await asyncio.sleep(SWITCH_DELAY)

                await member.remove_roles(role3)
                await asyncio.sleep(SWITCH_DELAY)

        except asyncio.CancelledError:
            member = await guild.fetch_member(OWNER_ID)
            for r in [role1, role2, role3]:
                if r in member.roles:
                    try:
                        await member.remove_roles(r)
                    except discord.HTTPException:
                        pass
            await ctx.send(f"{ctx.author.mention} đã ngắt mạch lệnh 🛑")

    boogie_task = asyncio.create_task(boogie_loop(ctx.guild))
    boogie_active = True
    await ctx.send(f"{ctx.author.mention} đã resume boogie! ⚡")

# ----------------------

# Role grant command

# ----------------------

@bot.command()
async def grant(ctx, target: discord.Member, *, role_name: str):
    if ctx.author.id != OWNER_ID:
        return
    # Find the role by name
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if not role:
        await ctx.send(f"Role **{role_name}** đéo tồn tại...")
        return

    try:
        await target.add_roles(role)
        await ctx.send(f"{ctx.author.mention} đã ban cho {target.mention} role **{role.name}** 🎉")
    except discord.Forbidden:
        await ctx.send("Bot đéo có quyền thêm role này")
    except discord.HTTPException:
        await ctx.send("Có lỗi khi thêm role, thử lại sau đi cu")

# ----------------------

# Role remove command

# ----------------------

@bot.command()
async def remove(ctx, target: discord.Member, *, role_name: str):
    if ctx.author.id != OWNER_ID:
        return
    # Find the role by name
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if not role:
        await ctx.send(f"Role **{role_name}** đéo tồn tại...")
        return

    try:
        await target.remove_roles(role)
        await ctx.send(f"{ctx.author.mention} đã gỡ role **{role.name}** khỏi {target.mention} 🗑️")
    except discord.Forbidden:
        await ctx.send("Bot đéo có quyền gỡ role này")
    except discord.HTTPException:
        await ctx.send("Có lỗi khi gỡ role, thử lại sau đi cu")

# ----------------------

# Reaction command

# ----------------------

@bot.command()
async def react(ctx, member: discord.Member, emoji: str):
    """React to the 10 latest messages of a specific user in the channel."""
    if ctx.author.id != OWNER_ID:
        return
    count = 0
    async for message in ctx.channel.history(limit=50):
        if message.author == member:
            try:
                await message.add_reaction(emoji)
                count += 1
            except Exception as e:
                await ctx.send(f"Couldn't react to a message: {e}")
            if count >= 10:
                break
    #await ctx.send(f"Reacted to {count} messages of {member.display_name} with {emoji}")

@bot.command()
async def reactall(ctx, emoji: str):
    """React to the 10 latest messages in the channel."""
    if ctx.author.id != OWNER_ID:
        return
    count = 0
    async for message in ctx.channel.history(limit=50):
        if message.author.bot:
            continue  # skip bot messages if you want
        try:
            await message.add_reaction(emoji)
            count += 1
        except Exception as e:
            await ctx.send(f"Couldn't react to a message: {e}")
        if count >= 10:
            break
    #await ctx.send(f"Reacted to {count} messages in this channel with {emoji}")
    
# Track active auto-reaction per channel
active_reactors = {}  # channel_id -> emoji

@bot.command()
async def keepreact(ctx, emoji: str):
    if ctx.author.id != OWNER_ID:
        return  # owner-only

    active_reactors[ctx.channel.id] = emoji
    # no confirmation message

@bot.command()
async def endreact(ctx):
    if ctx.author.id != OWNER_ID:
        return  # owner-only

    if ctx.channel.id in active_reactors:
        del active_reactors[ctx.channel.id]
    # no confirmation message

# ----------------------

# Un/Crucify command

# ----------------------

CRUCIFIED_ROLE_NAME = "CRUCIFIED"  # Make sure this role exists in your server

@bot.command()
async def crucify(ctx, target: discord.Member):
    if ctx.author.id != OWNER_ID:
        return  # owner-only

    role = discord.utils.get(ctx.guild.roles, name=CRUCIFIED_ROLE_NAME)
    if not role:
        await ctx.send("Role 'Crucified' đéo tồn tại, tạo đi rồi thử lại")
        return

    await target.add_roles(role)
    await ctx.send(f"✝️ Đã thanh trừng {target.mention}")

@bot.command()
async def uncrucify(ctx, target: discord.Member):
    if ctx.author.id != OWNER_ID:
        return  # owner-only

    role = discord.utils.get(ctx.guild.roles, name=CRUCIFIED_ROLE_NAME)
    if not role:
        await ctx.send("Role 'Crucified' đéo tồn tại")
        return

    await target.remove_roles(role)
    await ctx.send(f"✨ Đã giải thanh trừng {target.mention}")

# ----------------------

# Debuff roles and effects

# ----------------------

DEBUFF_ROLES = {
    "Sloth": "⏳ 20s Slowmode (Auto xoá tin nhắn nếu không chờ)",
    "Confusion": "😵 Không gửi được embed hoặc ảnh",
    "Sharpshot": "🎯 Xoá tin nhắn ngẫu nhiên"
}

DEBUFF_DURATION = 600  # 10 minutes in seconds

@bot.command()
async def debuff(ctx, target: discord.Member):
    if ctx.author.id != OWNER_ID:
        return  # owner-only

    # Check if target already has a debuff
    for role_name in DEBUFF_ROLES.keys():
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role and role in target.roles:
            await ctx.send(f"{target.mention} đã bị debuff sẵn rồi")
            return

    # Pick random debuff
    role_name = random.choice(list(DEBUFF_ROLES.keys()))
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        role = await ctx.guild.create_role(name=role_name)
    
    await target.add_roles(role)
    await ctx.send(f"💀 {ctx.author.mention} đã debuff {target.mention} bằng **{role_name}**! ({DEBUFF_ROLES[role_name]})")

    # Remove debuff after duration
    async def remove_debuff():
        await asyncio.sleep(DEBUFF_DURATION)
        if role in target.roles:
            await target.remove_roles(role)
            #await ctx.send(f"⏳ Debuff {role_name} của {target.mention} đã hết hiệu lực!")

    asyncio.create_task(remove_debuff())

# ------------------------

# Effects handling + keep reactions

# ------------------------

WATCH_CHANNEL_ID = 1417408911861874708  # replace with channel ID you want to monitor
NOTIFY_CHANNEL_ID = 1417408911861874708  # replace with channel ID where you get pinged


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # -------------------
    # DM relay
    # -------------------
    if isinstance(message.channel, discord.DMChannel) and not message.author.bot:
        # Ignore if it's you or an ignored user
        if message.author.id == OWNER_ID or message.author.id in dm_ignore_list:
            return

        channel = bot.get_channel(DM_REPORT_CHANNEL_ID)
        if channel:
            files = [await att.to_file() for att in message.attachments]

            relay_msg = f"<@{OWNER_ID}> **{message.author.mention}** said:\n"
            if message.content:
                relay_msg += message.content

            # Stickers
            if message.stickers:
                relay_msg += "\n🖼️ Stickers: " + ", ".join([s.name for s in message.stickers])

            await channel.send(relay_msg, files=files)

        return  # stop here so DMs don't go through command checks

    # -------------------
    # Auto notify
    # -------------------
    if message.channel.id == WATCH_CHANNEL_ID:
        notify_channel = bot.get_channel(NOTIFY_CHANNEL_ID)
        if notify_channel:
            await notify_channel.send(f"<@{OWNER_ID}> duyệt đơn gỡ ban kìa cu")

    guild = message.guild
    member = message.author
    if not guild:
        return
    
    # Auto-react check
    if message.channel.id in active_reactors:
        emoji = active_reactors[message.channel.id]
        try:
            await message.add_reaction(emoji)
        except Exception:
            pass  # silently fail if invalid emoji
    
    # Crucify check first (override everything)
    crucified = discord.utils.get(guild.roles, name=CRUCIFIED_ROLE_NAME)
    if crucified and crucified in member.roles:
        await asyncio.sleep(1)
        try:
            await message.delete()
        except discord.NotFound:
            pass
        return  # stop processing debuffs

    # -------------------
    # Debuff effects
    # -------------------
    sloth = discord.utils.get(guild.roles, name="Sloth")
    confusion = discord.utils.get(guild.roles, name="Confusion")
    sharpshot = discord.utils.get(guild.roles, name="Sharpshot")

    # Sloth effect (20s cooldown)
    if sloth and sloth in member.roles:
        if not hasattr(bot, "last_sloth"):
            bot.last_sloth = {}
        last_time = bot.last_sloth.get(member.id, 0)
        now = asyncio.get_event_loop().time()
        if now - last_time < 20:
            await message.delete()
            return
        bot.last_sloth[member.id] = now

    if confusion and confusion in member.roles:
        try:
            # Any attachments or embeds
            if message.attachments or message.embeds:
                await message.delete()
                return

            # Any stickers (server or global)
            if getattr(message, "stickers", None) and len(message.stickers) > 0:
                await message.delete()
                return

            # Some versions have sticker_items
            if getattr(message, "sticker_items", None) and len(message.sticker_items) > 0:
                await message.delete()
                return

            # Optional: empty placeholder (some stickers)
            if message.content.strip() == "":
                await message.delete()
                return
        except Exception:
            pass

    # Sharpshot effect (50% chance to delete)
    if sharpshot and sharpshot in member.roles:
        if random.random() < 0.5:
            await message.delete()
            return

    # process commands after checks
    await bot.process_commands(message)

# ----------------------

# Mass remove role command

# ----------------------

@bot.command()
@commands.has_permissions(manage_roles=True)
async def massremove(ctx, role: discord.Role):
    """Remove a role from everyone who has it."""
    if ctx.guild is None:
        await ctx.send("This command can only be used in a server.")
        return

    if role >= ctx.guild.me.top_role:
        await ctx.send("Đ gỡ đc role cao vl")
        return

    # Fetch all members (modern way)
    all_members = [member async for member in ctx.guild.fetch_members(limit=None)]

    members_with_role = [member for member in all_members if role in member.roles]

    if not members_with_role:
        await ctx.send(f"Không ai có role {role.name} cả")
        return

    removed_count = 0
    for member in members_with_role:
        try:
            await member.remove_roles(role)
            removed_count += 1
        except:
            pass

    await ctx.send(f"Đã gỡ {role.name} khỏi {removed_count} thành viên")

# ----------------------

# Mute command

# ----------------------

from datetime import timedelta

@bot.command()
async def mute(ctx, member: discord.Member, duration: str, *, reason: str = "No reason provided"):
    """
    Mute a member for a specific duration (server timeout).
    Duration format: 10s, 5m, 2h, 1d
    """
    if ctx.author.id != OWNER_ID:
        return  # only owner can use

    time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    unit = duration[-1]
    if unit not in time_units:
        return await ctx.send("Sai đơn vị thời gian, xài s, m, h, hoặc d đê")
    try:
        seconds = int(duration[:-1]) * time_units[unit]
    except:
        return await ctx.send("Sai lượng thời gian")

    try:
        await member.timeout(timedelta(seconds=seconds), reason=reason)
        await ctx.send(f"{member.mention} đã bị khoá mõm trong {duration}. Lý do: {reason}")
    except discord.Forbidden:
        await ctx.send("❌ Bot đéo có quyền mute thành viên này")
    except Exception as e:
        await ctx.send(f"⚠️ Có lỗi xảy ra khi mute: {e}")

@bot.command()
async def unmute(ctx, member: discord.Member):
    """Unmute a member (remove timeout)."""
    if ctx.author.id != OWNER_ID:
        return  # only owner can use

    try:
        await member.timeout(None, reason="Unmuted by owner")
        await ctx.send(f"{member.mention} đã được mở khoá mõm")
    except discord.Forbidden:
        await ctx.send("❌ Bot đéo có quyền unmute thành viên này")
    except Exception as e:
        await ctx.send(f"⚠️ Có lỗi xảy ra khi unmute: {e}")

# ----------------------

# Purge command

# ----------------------

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int, member: discord.Member = None):
    """
    Delete a number of messages. Optionally filter by user.
    """
    def is_member(m):
        return m.author == member if member else True

    deleted = await ctx.channel.purge(limit=amount + 1, check=is_member)
    await ctx.send(f"Deleted {len(deleted)-1} messages{' from ' + member.display_name if member else ''}.", delete_after=5)

# ----------------------

# Mass ping command

# ----------------------

@bot.command(name="massping")
async def massping(ctx, member: discord.Member, number: int):
    if ctx.author.id != OWNER_ID:
        return
    """
    Ping a user multiple times in separate messages.
    Usage: !massping @user 5
    """
    if number > 20:  # safety limit
        return await ctx.send("❌ Maximum 20 pings allowed at once!")
    await ctx.message.delete()
    for _ in range(number):
        await ctx.send(member.mention)
        await asyncio.sleep(0.5)  # small delay to avoid ratelimits
        
# ----------------------

# DM relay system (silent)

# ----------------------

DM_REPORT_CHANNEL_ID = 1424992515681157201  # change to your chosen report channel ID
dm_ignore_list = set()  # users ignored from DM relay

@bot.command()
async def dm(ctx, target: discord.Member, *, content: str = None):
    if ctx.author.id != OWNER_ID:
        return
    try:
        files = [await att.to_file() for att in ctx.message.attachments]
        if content or files:
            await target.send(content, files=files)
        # no ctx.send() → silent
    except:
        pass  # fail silently

@bot.command()
async def dmignore(ctx, target: discord.Member):
    if ctx.author.id != OWNER_ID:
        return
    dm_ignore_list.add(target.id)
    # silent, no response


# ----------------------

# Evil Ping system (silent)

# ----------------------

import random
import asyncio

evilping_task = None
evilping_active = False

# ----------------------
# Evil Ping system (silent)
# ----------------------

evilping_task = None
evilping_active = False

@bot.command()
async def evilping(ctx, target: discord.Member):
    global evilping_task, evilping_active
    if ctx.author.id != OWNER_ID:
        return
    if evilping_active:
        await ctx.send("⚠️ Evilping is already running!")
        return

    evilping_active = True
    await ctx.send(f"👹 Evilping started on {target.mention}! (Random pings every 10s–10min)")

    async def evilping_loop():
        try:
            while evilping_active:
                delay = random.randint(10, 600)  # 10s to 10min
                await asyncio.sleep(delay)
                msg = await ctx.channel.send(target.mention)
                await asyncio.sleep(1)
                try:
                    await msg.delete()
                except discord.NotFound:
                    pass
        except asyncio.CancelledError:
            pass

    evilping_task = asyncio.create_task(evilping_loop())

@bot.command()
async def endevilping(ctx):
    global evilping_task, evilping_active
    if ctx.author.id != OWNER_ID:
        return
    if evilping_task and not evilping_task.done():
        evilping_active = False
        evilping_task.cancel()
        await ctx.send("🛑 Evilping stopped.")
    else:
        await ctx.send("⚠️ Evilping is not currently running.")
        
# ----------------------

# Grant role with role command

# ----------------------        
        
@bot.command()
async def role2role(ctx, role1: discord.Role, role2: discord.Role):
    """Give role2 to everyone who has role1 (owner-only)."""
    if ctx.author.id != OWNER_ID:
        return  # owner-only

    if role2 >= ctx.guild.me.top_role:
        await ctx.send("❌ Bot đéo có quyền thêm role cao hơn mình")
        return

    # Fetch all members
    all_members = [m async for m in ctx.guild.fetch_members(limit=None)]
    members_with_role1 = [m for m in all_members if role1 in m.roles]

    if not members_with_role1:
        await ctx.send(f"❌ Không ai có role {role1.name} cả")
        return

    added_count = 0
    for member in members_with_role1:
        try:
            if role2 not in member.roles:
                await member.add_roles(role2)
                added_count += 1
        except:
            pass

    await ctx.send(f"✅ Đã thêm role **{role2.name}** cho {added_count} thành viên có role **{role1.name}**")
    
# ----------------------

# Translate command

# ----------------------
    
from googletrans import Translator

translator = Translator()

@bot.command()
async def translate(ctx, lang: str = "en"):
    """
    Reply to a message and run:
    - translate → translates to English
    - translate vi → translates to Vietnamese
    - translate [lang_code] → translates to that language (ex: 'fr', 'ja', 'ko')
    """
    if not ctx.message.reference:
        await ctx.send("⚠️ Reply to a message to translate it!")
        return

    try:
        # Fetch the replied message
        replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        text = replied_msg.content.strip()

        if not text:
            await ctx.send("⚠️ No text found to translate.")
            return

        # Translate to chosen language
        result = translator.translate(text, dest=lang)

        await ctx.send(
            f"🌐 Detected **{result.src}** → **{lang}**:\n{result.text}"
        )

    except Exception as e:
        await ctx.send(f"⚠️ Translation failed: {e}")
        
# ----------------------

# Guard command

# ----------------------

@bot.command()
async def guard(ctx, target: discord.Member):
    if ctx.author.id != OWNER_ID:
        return  # owner-only
    
    """
    Scare a user by announcing they're under surveillance.
    Usage: tguard @user
    """
    await ctx.send(f"{target.mention} đã bị giám sát.")
        
# ----------------------

# Help command

# ----------------------

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📜 Lệnh của BoTTôhm",
        description="Dưới đây là lệnh có thể sử dụng:",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="<a:gambling:1424223038903156837> Gacha",
        value=(
            "`troll` → Gacha kéo role hiếm\n"
            "`tbet` → Cược để được 20 giây 2x luck hoặc 60 giây 0,75x luck"
        ),
        inline=False
    )

    embed.add_field(
        name="<:steamhappy:1415394962916249681> Giải trí",
        value=(
            "`tgay @user` → Xem mức độ gay của ai đó\n"
            "`tpunch @user` → Đấm vỡ mồm ai đó\n"
            "`treply [câu hỏi]` → Trả lời câu hỏi một cách ngẫu nhiên"
        ),
        inline=False
    )
    embed.add_field(
        name="<:Jarvis:1418204830169694318> Tiện dụng (Chủ sv - 1/2)",
        value=(
            "`treact @user :emoji:` → React emoji đến 10 tin nhắn của ai đó\n"
            "`treactall :emoji:` → React emoji đến 10 tin nhắn trong kênh đó\n"
            "`tkeepreact :emoji:` → Liên tục react tin nhắn trong kênh đó\n"
            "`tendreact` → Ngắt keepreact\n"
            "`tcrucify @user` → Thanh trừng ai đó\n"
            "`tuncrucify @user` → Giải thanh trừng ai đó\n"
            "`tgrant @user [@role]` → Ban role cho ai đó\n"
            "`tremove @user [@role]` → Gỡ role cho ai đó\n"
            "`tmassremove [@role]` → Gỡ tất cả role đó\n"
            "`trole2role [@role1] [@role2]` → Cấp role2 cho ai có role1\n"
        ),
        inline=False
    )
    
    embed.add_field(
        name="<:Jarvis:1418204830169694318> Tiện dụng (Chủ sv - 2/2)",
        value=(
            "`tdebuff @user` → Ban một lời nguyền ngẫu nhiên cho ai đó\n"
            "`tmute @user [duration] [reason]` → Khoá mõm ai đó\n"
            "`tunmute @user` → Mở khoá mõm ai đó\n"
            "`tpurge [number] @user` → Xoá tin nhắn từ ai đó\n"
            "`tsay [text]` → Nhét chữ vào mồm bot\n"
            "`tmassping @user [number]` → Ping ai đó x lần\n"
            "`tdm @user [message]` → Nhắn tin riêng cho ai đó\n"
            "`tdmignore @user` → Đéo quan tâm người đó trong DM nữa\n"
            "`tevilping @user` → Ping ai đó ngẫu nhiên\n"
            "`tendevilping` → Ngắt lệnh evilping\n"
            "`tresumeboogie` → Resume chuyển role liên tục\n"
            "`tendboogie` → Ngắt chuyển role\n"
            "`tpermtest` → Test bot còn sống hay không\n"
        ),
        inline=False
    )

    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

# ----------------------

# Bot Events

# ----------------------

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    global boogie_task
    guild = bot.get_guild(GUILD_ID)

    if guild and (not boogie_task or boogie_task.done()):
        boogie_task = asyncio.create_task(boogie_loop(guild))
        print("⚡ Roleboogie started automatically!")

# ----------------------

# Run Bot

# ----------------------

bot.run("MTQxNzUxNTc5MDk5OTIyODQ2Ng.GbrM8A.zRX2a-ejDVdNVdwwZJhARA17RwRjg78u0Nx2pQ")