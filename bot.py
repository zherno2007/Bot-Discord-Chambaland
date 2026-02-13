import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import random
import string

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# CONFIGURACIÓN
ROL_VERIFICADO = "Verificado"
ROL_CHAMBALITOS = "Chambalitos"
CANAL_LOGS_ID = 1471656681195966586

codigos_verificacion = {}

# ---------------- BOT LISTO ---------------- #

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# ---------------- BOTÓN DE VERIFICACIÓN ---------------- #

class VerificacionView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verificarse", style=discord.ButtonStyle.success, emoji="✅")
    async def verificar(self, interaction: discord.Interaction, button: Button):
        member = interaction.user
        guild = interaction.guild

        if guild is None:
            return

        rol_verificado = discord.utils.get(guild.roles, name=ROL_VERIFICADO)

        if rol_verificado in member.roles:
            await interaction.response.send_message(
                "⚠️ Ya estás verificado.", ephemeral=True
            )
            return

        # Generar código de 6 caracteres
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        codigos_verificacion[member.id] = codigo

        await interaction.response.send_message(
            f"Tu código es: `{codigo}`\nEscríbelo en el chat para verificarte.\nExpira en 2 minutos.",
            ephemeral=True
        )

# ---------------- COMANDO PARA ENVIAR PANEL ---------------- #

@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):
    embed = discord.Embed(
        title="Sistema de Verificación",
        description="Haz clic en el botón para verificarte.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=VerificacionView())

# ---------------- VERIFICACIÓN POR MENSAJE ---------------- #

@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.author.bot:
        return

    if message.author.id in codigos_verificacion:
        if message.content == codigos_verificacion[message.author.id]:

            member = message.author
            guild = message.guild

            rol_verificado = discord.utils.get(guild.roles, name=ROL_VERIFICADO)
            rol_chambalitos = discord.utils.get(guild.roles, name=ROL_CHAMBALITOS)

            roles_a_agregar = []

            if rol_verificado:
                roles_a_agregar.append(rol_verificado)

            if rol_chambalitos:
                roles_a_agregar.append(rol_chambalitos)

            if roles_a_agregar:
                await member.add_roles(*roles_a_agregar)

            del codigos_verificacion[member.id]

            await message.channel.send(f"✅ {member.mention} ahora está verificado.")

            # LOGS
            canal_logs = bot.get_channel(CANAL_LOGS_ID)
            if canal_logs:
                embed = discord.Embed(
                    title="Nuevo Usuario Verificado",
                    description=f"Usuario: {member.mention}\nID: {member.id}",
                    color=discord.Color.blue()
                )
                await canal_logs.send(embed=embed)

# ---------------- INICIAR BOT ---------------- #

bot.run(os.getenv("TOKEN"))
