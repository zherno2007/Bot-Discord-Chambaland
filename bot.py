import discord
from discord.ext import commands
import random
import string
import time
import os

# ========= CONFIG =========
TOKEN = os.getenv("TOKEN")

CANAL_VERIFICACION_ID = 1471608546620739604  # donde escriben el código
CANAL_LOGS_ID = 1471656681195966586          # canal SOLO logs del bot

ROL_VERIFICADO_ID = 1471637465700892673
ROL_CHAMBALITOS_ID = 1467028217045975245

# user_id: {codigo, expira}
codigos_verificacion = {}

# ========= BOT =========
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ========= BOTÓN =========
class VerificacionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Verificarse",
        style=discord.ButtonStyle.success,
        emoji="✅",
        custom_id="verificar_boton"
    )
    async def verificar(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(interaction.user.id)
        rol_verificado = interaction.guild.get_role(ROL_VERIFICADO_ID)

        if rol_verificado in member.roles:
            await interaction.response.send_message(
                "❌ Ya estás verificado.",
                ephemeral=True
            )
            return

        codigo = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

        codigos_verificacion[member.id] = {
            "codigo": codigo,
            "expira": time.time() + 120
        }

        try:
            await member.send(
                "🔐 **Verificación del servidor**\n\n"
                f"Tu código es: **`{codigo}`**\n"
                "⏱️ Expira en **2 minutos**\n\n"
                "📌 Escríbelo en el canal de verificación."
            )
            await interaction.response.send_message(
                "📩 Código enviado a tu MD.",
                ephemeral=True
            )
        except:
            await interaction.response.send_message(
                "❌ No puedo enviarte MD. Actívalos.",
                ephemeral=True
            )


# ========= EVENTOS =========
@bot.event
async def on_ready():
    bot.add_view(VerificacionView())
    print(f"Bot conectado como {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id != CANAL_VERIFICACION_ID:
        return

    await message.delete()

    user_id = message.author.id
    texto = message.content.strip()

    if user_id not in codigos_verificacion:
        return

    datos = codigos_verificacion[user_id]

    logs = message.guild.get_channel(CANAL_LOGS_ID)

    # Código expirado
    if time.time() > datos["expira"]:
        del codigos_verificacion[user_id]
        if logs:
            await logs.send(f"⏱️ Código expirado — **{message.author}**")
        try:
            await message.author.send("❌ Tu código expiró. Presiona verificar otra vez.")
        except:
            pass
        return

    # Código incorrecto
    if texto != datos["codigo"]:
        if logs:
            await logs.send(f"❌ Código incorrecto — **{message.author}**")
        return

    # Código correcto
    guild = message.guild
    member = guild.get_member(user_id)

    rol_verificado = guild.get_role(ROL_VERIFICADO_ID)
    rol_chambalitos = guild.get_role(ROL_CHAMBALITOS_ID)

    await member.add_roles(rol_verificado, rol_chambalitos)

    del codigos_verificacion[user_id]

    if logs:
        await logs.send(f"✅ Usuario verificado — **{member}**")

    try:
        await member.send(
            "✅ **Verificación completada**\n\n"
            "Ya tienes acceso al servidor. ¡Bienvenido!"
        )
    except:
        pass


bot.run(TOKEN)
