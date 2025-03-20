import discord
from discord.ext import commands
import json
import asyncio

# استيراد الملفات الخاصة باللعبة
from game.game_manager import GameManager
from game.voting import VotingSystem
from game.roles import ROLES
from game.messages import get_game_message
from utils.helpers import create_embed

# إعداد البوت
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# إدارة اللعبة
game_manager = GameManager()  # تأكد أن الكائن موجود
voting_system = VotingSystem()

# ✅ عند تشغيل البوت
@bot.event
async def on_ready():
    print(f"🔹 تم تسجيل الدخول كبوت: {bot.user.name}")

# ✅ أمر بدء اللعبة
@bot.command(name="game")
async def start_game(ctx):
    if game_manager.is_running:
        await ctx.send("⚠️ اللعبة قيد التشغيل بالفعل!")
        return

    game_manager.start_game()

    embed = create_embed(
        title="🎭 لعبة المستذئب 🎭",
        description="مرحبًا بكم في لعبة المستذئب! يمكنكم الانضمام عبر الضغط على الزر أدناه.",
        footer="تم برمجة البوت من قبل 7MOD"
    )

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="🟢 انضم", custom_id="join", style=discord.ButtonStyle.green))
    view.add_item(discord.ui.Button(label="🔴 خروج", custom_id="leave", style=discord.ButtonStyle.red))
    view.add_item(discord.ui.Button(label="🚀 بدء اللعبة", custom_id="start", style=discord.ButtonStyle.blurple))
    view.add_item(discord.ui.Button(label="📜 شرح اللعبة", custom_id="info", style=discord.ButtonStyle.gray))
    view.add_item(discord.ui.Button(label="❓ دعم ومساعدة", custom_id="support", style=discord.ButtonStyle.gray))

    await ctx.send(embed=embed, view=view)

# ✅ التعامل مع الأزرار
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if not interaction.data.get("custom_id"):
        return

    custom_id = interaction.data["custom_id"]

    print(game_manager)

    
    if custom_id == "join":
        result = game_manager.add_player(interaction.user)
        await interaction.response.send_message(result, ephemeral=True)

    elif custom_id == "leave":
        result = game_manager.remove_player(interaction.user)
        await interaction.response.send_message(result, ephemeral=True)

    elif custom_id == "start":
        if interaction.user != game_manager.owner:
            await interaction.response.send_message("⚠️ فقط مالك اللعبة يمكنه بدء اللعبة!", ephemeral=True)
            return

        roles_assigned = game_manager.assign_roles()
        await interaction.response.send_message("🎲 تم تعيين الأدوار! سيتم إرسالها بشكل خاص لكل لاعب.", ephemeral=True)

        # إرسال الأدوار لكل لاعب
        for player, role in game_manager.players.items():
            try:
                await player.send(f"🎭 دورك في اللعبة: **{role}**\n🔎 الوصف: {role.description}")
            except:
                print(f"❌ لم أتمكن من إرسال رسالة إلى {player.name}")

        await game_manager.start_night_phase()

    elif custom_id == "info":
        await interaction.response.send_message(get_game_message(), ephemeral=True)

    elif custom_id == "support":
        await interaction.response.send_message("📩 تواصل مع 7MOD في حال وجود أي استفسار!", ephemeral=True)

# ✅ أمر إيقاف اللعبة
@bot.command(name="stop")
async def stop_game(ctx):
    if not game_manager.is_running:
        await ctx.send("⚠️ لا توجد لعبة قيد التشغيل!")
        return

    game_manager.reset_game()
    await ctx.send("⛔ تم إنهاء اللعبة بنجاح!")


@bot.command()
async def reset_game(ctx):
    game_manager.is_running = False
    await ctx.send("🔄 تم إعادة تعيين حالة اللعبة!")


# ✅ تشغيل البوت
TOKEN = "MTM1MTI5OTUxMDg3MzIzMTUzMQ.GtiU8O.j6dWnIuzVadBS8t2cHcllmWy_kDhxDVGUT2vPQ"
bot.run(TOKEN)
