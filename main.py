import os
import discord
from discord.ext import commands
import random
import asyncio
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

WHITESNAKE_PURPLE = 0x6B21A8
ACID_GREEN = 0x39FF14
ACID_COLOR = 0x00FF41

STAND_USER_ID = int(os.getenv('STAND_USER_ID', '0'))
STAND_NAME = "Whitesnake"

usuarios_programados = {}
canais_acidos = {}

def is_stand_user(ctx):
    return ctx.author.id == STAND_USER_ID

async def check_stand_user(ctx):
    if not is_stand_user(ctx):
        embed = discord.Embed(
            title="Acesso Negado",
            description="Voce nao possui o Stand necessario...",
            color=0xFF0000,
            timestamp=datetime.now()
        )
        embed.add_field(name="Stand:", value="Whitesnake", inline=False)
        await ctx.send(embed=embed)
        return False
    return True

@bot.event
async def on_ready():
    print(f'Whitesnake online! Logado como: {bot.user}')
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name="os discos de memoria"
        )
    )

@bot.command(name='standuser')
async def stand_user_info(ctx):
    embed = discord.Embed(
        title="Whitesnake",
        color=WHITESNAKE_PURPLE,
        timestamp=datetime.now()
    )
    if is_stand_user(ctx):
        embed.add_field(name="Status:", value="VOCE E O STAND USER!", inline=False)
    else:
        embed.add_field(name="Stand User:", value=f"<@{STAND_USER_ID}>", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='ajuda')
async def ajuda(ctx):
    if not is_stand_user(ctx):
        await ctx.send("Apenas o Stand User pode usar comandos!")
n        return
    
    embed = discord.Embed(
        title="Comandos do Whitesnake",
        color=WHITESNAKE_PURPLE
    )
    embed.add_field(name="!standuser", value="Ver informacoes do Stand", inline=False)
    embed.add_field(name="!acido [segundos]", value="Ativar modo lento no canal", inline=False)
    embed.add_field(name="!cancelaracido", value="Remover modo lento", inline=False)
    embed.add_field(name="!removerdisco @usuario", value="Dar timeout no usuario", inline=False)
    embed.add_field(name="!inserirdisco @usuario frase", value="Programar usuario", inline=False)
    embed.add_field(name="!dissolver [quantidade]", value="Limpar mensagens", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='acido')
async def acido(ctx, segundos: int = 10):
    if not await check_stand_user(ctx):
        return
    
    if segundos < 1:
        segundos = 1
    elif segundos > 21600:
        segundos = 21600
    
    try:
        canais_acidos[ctx.channel.id] = ctx.channel.slowmode_delay
        await ctx.channel.edit(slowmode_delay=segundos)
        
        embed = discord.Embed(
            title="ACIDO ATIVADO",
            description=f"Modo lento: {segundos} segundos",
            color=ACID_COLOR,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Use !cancelaracido para remover")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Erro: {str(e)}")

@bot.command(name='cancelaracido')
async def cancelar_acido(ctx):
    if not await check_stand_user(ctx):
        return
    
    try:
        if ctx.channel.id in canais_acidos:
            anterior = canais_acidos.pop(ctx.channel.id)
            await ctx.channel.edit(slowmode_delay=anterior)
        else:
            await ctx.channel.edit(slowmode_delay=0)
        
        await ctx.send("Acido neutralizado!")
    except Exception as e:
        await ctx.send(f"Erro: {str(e)}")

@bot.command(name='removerdisco')
async def remover_disco(ctx, membro: discord.Member):
    if not await check_stand_user(ctx):
        return
    
    try:
        duracao = random.randint(30, 300)
        await membro.timeout(timedelta(seconds=duracao), reason="Whitesnake removeu o disco")
        
        embed = discord.Embed(
            title="DISCO REMOVIDO",
            description=f"{membro.mention} perdeu as memorias...",
            color=WHITESNAKE_PURPLE
        )
        embed.add_field(name="Duracao:", value=f"{duracao} segundos", inline=False)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Erro: {str(e)}")

@bot.command(name='inserirdisco')
async def inserir_disco(ctx, membro: discord.Member, *, frase):
    if not await check_stand_user(ctx):
        return
    
    usuarios_programados[membro.id] = frase.lower()
    
    embed = discord.Embed(
        title="DISCO INSERIDO",
        description=f"{membro.mention} esta sob controle!",
        color=ACID_GREEN
    )
    embed.add_field(name="Comando:", value=frase, inline=False)
    await ctx.send(embed=embed)

@bot.command(name='dissolver')
async def dissolver(ctx, quantidade: int = 10):
    if not await check_stand_user(ctx):
        return
    
    if quantidade > 100:
        quantidade = 100
    elif quantidade < 1:
        quantidade = 1
    
    try:
        await ctx.channel.purge(limit=quantidade + 1)
        msg = await ctx.send(f"{quantidade} mensagens dissolvidas!")
        await asyncio.sleep(3)
        await msg.delete()
    except Exception as e:
        await ctx.send(f"Erro: {str(e)}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.author.id in usuarios_programados:
        frase_esperada = usuarios_programados[message.author.id]
        conteudo = message.content.lower()
        
        if frase_esperada not in conteudo:
            respostas = [
                f"Whitesnake: {message.author.mention}, diga exatamente: {usuarios_programados[message.author.id]}",
                f"Whitesnake: Sua memoria foi alterada. OBEY.",
                f"Disco de {message.author.name} falhando... REPITA!"
            ]
            await message.channel.send(random.choice(respostas))
            
            if random.randint(1, 10) == 1:
                del usuarios_programados[message.author.id]
                await message.channel.send(f"Disco de {message.author.mention} quebrou! Liberdade!")
    
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Especifique o alvo!")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Usuario nao encontrado!")
    elif isinstance(error, commands.CommandNotFound):
        return
    else:
        print(f"Erro: {error}")

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("ERRO: DISCORD_TOKEN nao configurado!")
    elif STAND_USER_ID == 0:
        print("ERRO: STAND_USER_ID nao configurado!")
    else:
        print(f"Iniciando...")
        bot.run(token)
