import discord
from discord.ext import commands
from discord import utils
import random
import os
import asyncio
import time
import requests
import json
from bs4 import BeautifulSoup as BS

bot = commands.Bot(command_prefix='$')
client = discord.Client()

finance = {}

profile = {}

minefinance = {}

jackpot = 10000

dt = int(time.time())
dt = dt // 60

brawlplayers = {}


@bot.event
async def on_ready():
    print("Bot logged as {}".format(bot.user))


@bot.event
async def on_message(message):
    global dt
    newdt = int(time.time())
    newdt = newdt // 60

    if message.author.id == 706401122721595444:
        return

    if newdt == dt:
        pass
    else:
        for id in minefinance.keys():
            if minefinance.get(id) == None:
                minefinance[id] = 0
            else:
                minefinance[id] = minefinance[id] + newdt - dt
    dt = newdt

    if profile.get(message.author.id) == None:
        profile[message.author.id] = [0, 0]
    else:
        profile[message.author.id][0] += 1
        if profile[message.author.id][0] >= 100:
            profile[message.author.id][1] += 1
            profile[message.author.id][0] = 0

    if finance.get(message.author.id) == None:
        finance[message.author.id] = 2
    else:
        finance[message.author.id] += 1

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send('Команда не найдена')


@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)


@bot.command()
async def stavka(ctx, arg: int):
    if profile.get(ctx.author.id) == None:
        profile[ctx.author.id] = [0, 0]
    arg = int(arg)
    if arg > finance[ctx.author.id] or arg <= 0:
        await ctx.send("Число введено неверно.")
    else:
        multi = random.randint(0, 20) / 10
        pot = random.randint(0, 100)
        finalresult = int(arg * multi)
        finance[ctx.author.id] -= arg
        global jackpot
        jackpot += arg
        jackpot -= finalresult
        if pot == 5:
            finance[ctx.author.id] += jackpot
            await ctx.send(
                "{}, поздравляем!Вы забрали джекпот!!!Он составлял {} монет!!!".format(ctx.author.mention, jackpot))
            jackpot = 10000
        else:
            finance[ctx.author.id] += finalresult
            await ctx.send("{}, вы выиграли {} монет".format(ctx.author.mention, finalresult))


@bot.command()
async def balans(ctx, member: discord.Member):
    if finance.get(member.id) == None:
        finance[member.id] = 2
    await ctx.send("{}, ваш баланс: {}".format(member.mention, finance[member.id]))
    member = member


@bot.command()
async def profiler(ctx, member: discord.Member):
    if profile.get(member.id) == None:
        profile[member.id] = [0, 0]
    await ctx.send(
        "{}, ваши очки: {}, уровень: {}".format(member.mention, profile[member.id][0],
                                                profile[member.id][1]))
    member = member


@bot.command()
async def top(ctx):
    if ctx.author.id == 706401122721595444:
        return
    topfinance = finance
    torr = list(finance.values())
    torr.sort()
    torr.clear()
    checked = []
    ind1 = "Нет информации"
    ind2 = "Нет информации"
    ind3 = "Нет информации"
    ind4 = "Нет информации"
    ind5 = "Нет информации"
    for i in range(len(topfinance.items())):
        biggest = 0
        bigkey = 0
        for k, v in topfinance.items():
            if v > biggest and k not in checked:
                biggest = v
                bigkey = k
        checked.append(bigkey)
        if bigkey > 0 and biggest > 0:
            torr.append([biggest, bigkey])
    ind1 = ("Первое место - {} - {}".format(bot.get_user(torr[0][1]), torr[0][0]))
    if len(torr) >= 2:
        ind2 = ("Второе место - {} - {}".format(bot.get_user(torr[1][1]), torr[1][0]))
    if len(torr) >= 3:
        ind3 = ("Третье место - {} - {}".format(bot.get_user(torr[2][1]), torr[2][0]))
    if len(torr) >= 4:
        ind4 = ("Четвертое место - {} - {}".format(bot.get_user(torr[3][1]), torr[3][0]))
    if len(torr) >= 5:
        ind5 = ("Пятое место - {} - {}".format(bot.get_user(torr[4][1]), torr[4][0]))
    await ctx.send("{}\n{}\n{}\n{}\n{}".format(ind1, ind2, ind3, ind4, ind5))


@bot.command(pass_context=True)
async def give(ctx, member: discord.Member, arg):
    rolarr = []
    for role in ctx.author.roles:
        rolarr.append(role.id)
    moder = 706208121487360030
    if moder not in rolarr:
        await ctx.channel.send("У вас недостаточно прав")
        return
    if finance.get(member.id) == None:
        finance[member.id] = int(arg)
        await ctx.channel.send("{} вам выдано {} монет".format(member.mention, arg))
        return
    arg = int(arg)
    finance[member.id] += arg
    await ctx.channel.send("{} вам выдано {} монет".format(member.mention, arg))
    member = member


@bot.command()
async def jackpot_info(ctx):
    await ctx.send("Джекпот составляет {} монет.".format(jackpot))


@bot.command()
async def mine_info(ctx, member: discord.Member):
    global dt
    newdt = int(time.time())
    newdt = newdt // 60
    if minefinance.get(member.id) == None:
        minefinance[member.id] = 0
    else:
        minefinance[member.id] = minefinance[member.id] + newdt - dt
    dt = newdt
    await ctx.channel.send("{} , вы намайнили {} монет.".format(member.mention, minefinance[member.id]))


@bot.command()
async def miningvivod(ctx, arg: int):
    if finance.get(ctx.author.id) == None:
        finance[ctx.author.id] = 2
    if minefinance.get(member.id) == None:
        minefinance[ctx.author.id] = 2
    if arg > minefinance[ctx.author.id] or arg <= 0:
        await ctx.send("Число введено неверно.")
    else:
        finance[ctx.author.id] += arg
        minefinance[ctx.author.id] -= arg
        await ctx.send("Вы успешно вывели {} монет".format(arg))


@bot.command()
async def dollar(ctx):
    r = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
    course = r.json()
    course = course['Valute']['USD']['Value']
    await ctx.send("Курс доллара: {} рублей".format(course))


@bot.command()
async def registr(ctx, usertag):
    r = requests.get("https://www.starlist.pro/stats/profile/{}".format(usertag))
    html = BS(r.content, "html.parser")
    user = {}
    club = {}
    club["name"] = (html.select(".shadow-normal"))[30].text
    club["trophies"] =
    user["name"] = (html.select(".display-4"))[0].text
    user["trophies"] = (html.select(".shadow-normal"))[22].text
    user["club"] = (html.select(".shadow-normal"))[30].text
    brawlplayers[ctx.author.id] = user
    await ctx.send(
        "Вы успешно зарегистрировались на нашем сервере! Ваш никнейм в игре Brawl Stars: {}! Если это не так , то обратитесь за помощью к модераторам!".format(
            user["name"]))


@bot.command()
async def brawltrophies(ctx, member: discord.Member):
    if brawlplayers.get(member.id) == None:
        await ctx.send(
            "Пользователь {} еще не зарегистрировался! Чтобы зарегистрироваться прейдите в канал 'регистрация'!".format(
                member.mention))
    else:
        await ctx.send("У вас {} кубков в игре Brawl Stars".format(brawlplayers[member.id]["trophies"]))


@bot.command()
async def brawlclub(ctx, member: discord.Member):
    if brawlplayers.get(member.id) == None:
        await ctx.send(
            "Пользователь {} еще не зарегистрировался! Чтобы зарегистрироваться прейдите в канал 'регистрация'!".format(
                member.mention))
    else:
        await ctx.send()



token = os.environ.get('BOT_TOKEN')
bot.run(str(token))
