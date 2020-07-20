import discord
from discord.ext import commands, tasks
import random
import os
import sys
import platform
import asyncio
import requests
import psycopg2
import dbl

try:
    import configs
except ModuleNotFoundError:
    TOKEN = os.environ.get("DBL_TOKEN")
    DATABASE_URL = os.environ.get('DATABASE_URL')
    token = os.environ.get('BOT_TOKEN')
else:
    TOKEN = configs.dbltoken
    DATABASE_URL = configs.database
    token = configs.token

bot = commands.Bot(command_prefix='.')
client = discord.Client()
bot.remove_command("help")

dblpy = dbl.DBLClient(bot, TOKEN, autopost=True)
conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cursor = conn.cursor()

jackpot = 10000

brawlplayers = {}

colors = [0x9b59b6, 0x1abc9c, 0x2ecc71, 0x3498db,
          0x34495e, 0x16a085, 0x27ae60, 0x2980b9, 0x8e44ad, 0x2c3e50,
          0xf1c40f, 0xe67e22, 0xe74c3c, 0xecf0f1,
          0x95a5a6, 0xf39c12, 0xd35400, 0xc0392b, 0xbdc3c7, 0x7f8c8d
          ]


def is_moder(ctx):
    for role in ctx.author.roles:
        if role.permissions.administrator:
            return True
    return False


@bot.event
async def on_ready():
    global conn, cursor
    await bot.change_presence(activity=discord.Game(".help | {} servers".format(len(bot.guilds))))
    for guild in bot.guilds:
        if len(guild.members) >= 10000 or guild.id == 264445053596991498:
            if len(guild.text_channels) <= 0:
                pass
            else:
                try:
                    await guild.text_channels[0].send(
                        "Ваш сервер слишком велик для нашего бота для того , чтобы он работал надо задонатить!!!")
                except:
                    pass
            continue
        if guild.system_channel is None:
            pass
        else:
            await guild.system_channel.send("Хей, я снова онлайн!")
        cursor.execute("SELECT * FROM guilds WHERE guild_id = %s;", (str(guild.id),))
        guilds = cursor.fetchall()
        if len(guilds) == 0:
            cursor.execute(
                "INSERT INTO guilds (guild_id, welcome, goodbye, jackpot) VALUES (%s , %s , %s , %s);",
                [str(guild.id), "Здарова, {}", "Прощай, {}", 10000])
        for member in guild.members:
            if member.bot:
                continue
            cursor.execute(
                "SELECT * FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(member.id, guild.id))
            users = cursor.fetchall()
            if len(users) == 0:
                cursor.execute(
                    "INSERT INTO users (user_id,level,money,minemoney,points,guild_id) VALUES ('{}',{},{},{},{},'{}');".format(
                        member.id, 0, 5, 0, 0, guild.id))
            conn.commit()
    print("Bot logged as {}".format(bot.user))


@bot.event
async def on_message(message):
    global cursor, conn
    if message.guild is None:
        return
    if message.guild.id == 264445053596991498:
        return
    if message.author.bot:
        return
    cursor.execute(
        "SELECT points FROM users WHERE user_id = %s AND guild_id = %s;", (
            str(message.author.id), str(message.guild.id),))
    points = cursor.fetchall()
    points = int(points[0][0]) + 1
    cursor.execute(
        "SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(
            message.author.id, message.guild.id))
    level = cursor.fetchall()
    level = level[0][1]
    if points >= 100:
        level += 1
        points -= 100
    cursor.execute(
        "UPDATE users SET money = money + 1 WHERE user_id = '{}' AND guild_id = '{}';".format(message.author.id,
                                                                                              message.guild.id))
    cursor.execute(
        "UPDATE users SET points = {} WHERE user_id = '{}' AND guild_id = '{}';".format(points, message.author.id,
                                                                                        message.guild.id))
    cursor.execute(
        "UPDATE users SET level = {} WHERE user_id = '{}' AND guild_id = '{}';".format(level, message.author.id,
                                                                                       message.guild.id))
    conn.commit()
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    user_id = 530751275663491092
    user = bot.get_user(user_id)
    await user.send("Произошла ошибка:\n{}".format(error))
    await ctx.send("Произошла ошибка, информация для дебага уже отправлена разработчикам.")


@bot.event
async def on_member_join(member):
    global conn, cursor
    guild = member.guild
    channel = guild.system_channel
    if guild.id == 264445053596991498:
        return
    cursor.execute(
        "SELECT welcome FROM guilds WHERE guild_id = %s;", (str(guild.id),))
    text = str(cursor.fetchall[0][0])
    cursor.execute(
        "INSERT INTO users (user_id,level,money,minemoney,points,guild_id) VALUES ('{}',{},{},{},{},'{}');".format(
            member.id, 0, 5, 0, 0, guild.id))
    conn.commit()
    await channel.send(text.format(member.mention))


@bot.event
async def on_member_remove(member):
    global cursor, conn
    guild = member.guild
    channel = guild.system_channel
    if guild.id == 264445053596991498:
        return
    cursor.execute(
        "SELECT goodbye FROM guilds WHERE guild_id = %s;", (str(guild.id),))
    text = str(cursor.fetchall()[0][0])
    cursor.execute("DELETE FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(
        member.id, guild.id))
    conn.commit()
    await channel.send(text.format(member))


@bot.event
async def on_guild_join(guild):
    global colors
    user_id = 530751275663491092
    user = bot.get_user(user_id)
    emb = discord.Embed(color=random.choice(colors))
    emb.title = "У нас новый сервер !!!"
    emb.description = "Название сервера: {}".format(guild.name)
    emb.set_image(url=guild.icon)
    await user.send(embed=emb)
    channel = guild.system_channel
    emb = discord.Embed(color=random.choice(colors),
                        description="Пожалуйста настройте бота!!!\nВведите .help и просмотрите комнады в секции 'модерация'\nНадеюсь бот вам понравится!\nSUPPORT email: progcuber@gmail.com")
    await channel.send(embed=emb)


@bot.event
async def on_guild_remove(guild):
    channel = guild.owner
    await channel.send("Эхххх....Жаль , что я вам не пригодился....\nP.S. Все данные удаляются")


@bot.event
async def on_disconnect():
    cursor.execute("UPDATE botinfo SET worktime = 0;")
    print("DISCONNECTED")


@tasks.loop(minutes=5.0)
async def mine():
    global cursor, conn
    for guild in bot.guilds:
        if guild.id == 264445053596991498:
            continue
        for member in guild.members:
            cursor.execute("UPDATE users SET minemoney = minemoney + 1 WHERE user_id = %s AND guild_id = %s;",
                           (str(member.id), str(guild.id),))
            conn.commit()


mine.start()


@tasks.loop(hours=1.0)
async def reconnect():
    global cursor, conn
    try:
        cursor.execute("SELECT * FROM guilds;")
    except psycopg2.InterfaceError:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        cursor = conn.cursor()
    else:
        conn.close()
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        cursor = conn.cursor()


reconnect.start()


@tasks.loop(hours=1.0)
async def statuschange():
    await bot.change_presence(activity=discord.Game(".help | {} servers".format()))


statuschange.start()


@tasks.loop(minutes=1.0)
async def worktime():
    cursor.execute("UPDATE botinfo SET worktime = worktime + 1;")


worktime.start()


# ready
@bot.command()
async def stavka(ctx, arg: int):
    global cursor, jackpot, colors, conn
    cursor.execute(
        "SELECT * FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(ctx.author.id, ctx.guild.id))
    userfinance = cursor.fetchall()
    arg = int(arg)
    if arg > userfinance[0][2] or arg <= 0:
        await ctx.send("❌Число введено неверно.")
    else:
        multi = random.randint(0, 20) / 10
        pot = random.randint(0, 100)
        finalresult = int(arg * multi)
        firstfinance = userfinance[0][2] - arg
        cursor.execute(
            "UPDATE users SET money = {} WHERE user_id = '{}' AND guild_id = '{}';".format(firstfinance,
                                                                                           ctx.author.id,
                                                                                           ctx.guild.id))
        jackpot += arg
        jackpot -= finalresult
        emb = discord.Embed(color=random.choice(colors))
        emb.title = ("Ставка: {}$\nМножитель: {}\nВыигрыш: {}$".format(
            arg, multi, finalresult))
        if pot == 5:
            jackpotfinance = jackpot + userfinance[0][2]
            cursor.execute(
                "UPDATE users SET money = {} WHERE user_id = '{}' AND guild_id = '{}';".format(jackpotfinance,
                                                                                               ctx.author.id,
                                                                                               ctx.guild.id))
            await ctx.send(
                "{}, поздравляем!Вы забрали джекпот!!!Он составлял {} монет!!!".format(ctx.author.mention, jackpot))
            jackpot = 10000
        else:
            lastfinance = finalresult + firstfinance
            cursor.execute(
                "UPDATE users SET money = {} WHERE user_id = '{}' AND guild_id = '{}';".format(lastfinance,
                                                                                               ctx.author.id,
                                                                                               ctx.guild.id))
            await ctx.send(embed=emb)
    conn.commit()


# ready
@bot.command()
async def balans(ctx, member: discord.Member = None):
    global colors, cursor
    if member is None:
        member = ctx.author
    emb = discord.Embed(color=random.choice(colors))
    cursor.execute(
        "SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(
            member.id, ctx.guild.id))
    userfinance = cursor.fetchall()
    emb.set_author(name="Баланс {} : {}$".format(
        member, userfinance[0][2]), icon_url=member.avatar_url)
    await ctx.send(embed=emb)


@bot.command()
async def usercard(ctx, member: discord.Member = None):
    global colors, cursor, conn
    if member is None:
        member = ctx.author
    emb = discord.Embed(color=random.choice(colors))
    cursor.execute(
        "SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(
            ctx.author.id, ctx.guild.id))
    usercardcomm = cursor.fetchall()
    emb.set_thumbnail(url=member.avatar_url)
    emb.title = "Профиль участника {}".format(member)
    emb.add_field(name="Уровень", value=("{}".format(usercardcomm[0][1])))
    emb.add_field(name="Очки", value=("{}".format(usercardcomm[0][4])))
    await ctx.send(embed=emb)
    conn.commit()


@bot.command()
async def top(ctx):
    global cursor
    emb = discord.Embed(color=random.choice(colors), title="Топ сервера")
    title = "#{} - {}"
    value = "Монеты: ```{}```"
    cursor.execute(
        "SELECT * FROM users WHERE guild_id = '{}' ORDER BY money;".format(ctx.guild.id))
    topp = cursor.fetchall()
    topp.reverse()
    counter = 0
    for elem in topp:
        if counter >= 10:
            break
        biggest = elem[2]
        bigkey = int(elem[0])
        if bot.get_user(bigkey) is None:
            continue
        newtitle = title.format(counter + 1, bot.get_user(bigkey))
        newvalue = value.format(biggest)
        emb.add_field(name=newtitle, value=newvalue, inline=False)
        counter += 1
    await ctx.send(embed=emb)


@bot.command()
async def give(ctx, member: discord.Member, arg):
    global cursor, conn
    mmroles = is_moder(ctx)
    if mmroles:
        pass
    else:
        await ctx.send(
            "У вас нет модераторской роли!!! Вам нужна роль с правами администратора!")
        return
    arg = int(arg)
    cursor.execute("UPDATE users SET money = money+{} WHERE user_id = '{}' AND guild_id = '{}';".format(arg,
                                                                                                        member.id,
                                                                                                        ctx.guild.id))
    await ctx.send("{} вам выдано {} монет".format(member.mention, arg))
    conn.commit()


@bot.command()
async def jackpot_info(ctx):
    await ctx.send("Джекпот составляет {} монет.".format(jackpot))


@bot.command()
async def mine_info(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    cursor.execute(
        "SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(
            member.id, ctx.guild.id))
    minefinance = cursor.fetchall()
    minefinance = minefinance[0][3]
    await ctx.channel.send("{} , вы намайнили {} монет.".format(member.mention, minefinance))


@bot.command()
async def miningvivod(ctx, arg):
    global conn, cursor
    arg = int(arg)
    cursor.execute(
        "SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(
            ctx.author.id, ctx.guild.id))
    minefinance = cursor.fetchall()
    minefinance = minefinance[0][3]
    cursor.execute(
        "SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(
            ctx.author.id, ctx.guild.id))
    finance = cursor.fetchall()
    finance = finance[0][2]
    if arg > minefinance:
        await ctx.send("Число введено неверно.")
    else:
        anoarg = arg
        arg = int(arg * 0.95)
        finance = finance + arg
        minefinance = minefinance - arg
        cursor.execute(
            "UPDATE users SET minemoney = {} WHERE user_id = '{}' AND guild_id = '{}';".format(minefinance,
                                                                                               ctx.author.id,
                                                                                               ctx.guild.id))
        cursor.execute(
            "UPDATE users SET money = {} WHERE user_id = '{}' AND guild_id = '{}';".format(finance, ctx.author.id,
                                                                                           ctx.guild.id))
        await ctx.send("Вы успешно вывели {} монет".format(anoarg))
        conn.commit()


@bot.command()
async def dollar(ctx):
    r = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
    course = r.json()
    course = course['Valute']['USD']['Value']
    await ctx.send("Курс доллара: {} рублей".format(course))


@bot.command()
async def help(ctx, arg=None):
    global colors
    emb = discord.Embed(color=random.choice(colors))
    if arg is None:
        emb.title = "Команды бота BuCord:"
        emb.description = "<> - обязательный аргумент , [] - необязательный аргумент"
        emb.add_field(name=".help [команда]", value="выводит это сообщение")
        emb.add_field(name=".dollar", value="выводит курс доллара к рублю")
        emb.add_field(name=".jackpot_info",
                      value="выводит кол-во монет , которое составляет джекпот")
        emb.add_field(name=".balans [участник сервера]",
                      value="выводит баланс участника")
        emb.add_field(name=".give <учатсник сервера> <монеты>",
                      value="добавляет участнику указанное кол-во монет(только для модераторов)")
        emb.add_field(name=".mine_info [участник сервера]",
                      value="выводит кол-во намайненых монет участника")
        emb.add_field(name=".miningvivod <монеты>",
                      value="выводит монеты с майнинга на баланс (комиссия 5%)")
        emb.add_field(name=".stavka <монеты>",
                      value="вы ставите монеты(принцип как в казино)")
        emb.add_field(name=".top", value="выводит топ участников по монетам")
        emb.add_field(name=".usercard [участник сервера]",
                      value="выводит карточку участника")
        emb.add_field(name=".goodbye <текст , символами {} обозначьте участника>",
                      value="настраивает прощание")
        emb.add_field(name=".welcome <текст , символами {} обозначьте участника>",
                      value="настраивает приветствие")
        emb.add_field(name=".findbug \"<краткое описание бага>\" \"<полное описание бага>\" [url-адрес картинки]",
                      value="отправляет разработчикам информацию о баге")
        emb.add_field(name=".botinfo",
                      value="выводит информацию о боте")
        emb.add_field(name=".ping",
                      value="выводит пинг бота")
    await ctx.send(embed=emb)


@bot.command()
async def welcome(ctx, text):
    global conn, cursor
    mmroles = is_moder(ctx)
    if mmroles:
        pass
    else:
        await ctx.send(
            "У вас нет модераторской роли!!! Вам нужна роль с правами администратора!")
        return
    cursor.execute(
        "UPDATE guilds SET welcome = %s WHERE guild_id = %s;", (text, str(ctx.guild.id),))
    conn.commit()
    await ctx.send("Приветствие успешно изменено.")


@bot.command()
async def goodbye(ctx, text):
    global conn, cursor
    mmroles = is_moder(ctx)
    if mmroles:
        pass
    else:
        await ctx.send(
            "У вас нет модераторской роли!!! Вам нужна роль с правами администратора!")
        return
    cursor.execute(
        "UPDATE guilds SET goodbye = %s WHERE guild_id = %s;", (text, str(ctx.guild.id),))
    conn.commit()
    await ctx.send("Прощание успешно изменено.")


@bot.command()
async def findbug(ctx, title, descreption, image_url=None):
    user_id = 530751275663491092
    user = bot.get_user(user_id)
    emb = discord.Embed(title=title, description=descreption)
    if image_url:
        emb.set_image(image_url)
    emb.set_author(name=ctx.author)
    await user.send(embed=emb)
    await ctx.send("Спасибо за то , что вы помогаете нам улучшить бота.")


@bot.command()
async def botinfo(ctx):
    emb = discord.Embed(color=random.choice(colors))
    emb.add_field(name="ОС:", value=("```{}```".format(sys.platform)))
    emb.add_field(name="Сервера:", value=("```{}```".format(len(bot.guilds))))
    emb.add_field(name="CPU:", value=("```{}```".format(platform.processor())))
    cursor.execute("SELECT worktime FROM botinfo;")
    work = cursor.fetchall()
    work = work[0][0]
    hours = work // 60
    minutes = work % 60
    emb.add_field(name="Время работы:", value=("```{} часов , {} минут```".format(hours, minutes)))
    await ctx.send(embed=emb)


@bot.command()
async def ping(ctx):
    emb = discord.Embed(color=random.choice(colors))
    emb.title = "Понг!"
    emb.description = "Пинг бота составляет {} ms".format(int(bot.latency * 1000))
    await ctx.send(embed=emb)


bot.run(str(token))
