"""moderation cog"""
import discord
from discord.ext import commands

from useful_commands import connect

con = connect()


class BotChange(commands.Cog):
    """
    commands with changes of bot
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def change_prefix(self, ctx, prefix="."):
        """
        changes bot prefix

        :param ctx: context
        :type ctx: commands.Context
        :param prefix: prefix to change
        :type prefix: str
        """
        with con.cursor() as cur:
            old_prefix = cur.fetch_val("SELECT prefix FROM guilds WHERE guild_id = %s;", ctx.guild.id)
            cur.execute("UPDATE guilds SET prefix = %s WHERE guild_id = %s;", prefix, ctx.guild.id)
        emb = discord.Embed(color=0x2ecc71)
        emb.title = "Обновление!!!"
        emb.add_field(name="Новый префикс!", value="Префикс успешно изменен с {} на {}".format(old_prefix, prefix))
        emb.set_footer(text="Пример команды: {}help".format(prefix))
        await ctx.send(embed=emb)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def goodbye(self, ctx, text):
        """
        set goodbye text

        :param ctx: context
        :type ctx: commands.Context
        :param text: new goodbye text
        :type text: str
        """
        with con.cursor() as cur:
            cur.execute(
                "UPDATE guilds SET goodbye = %s WHERE guild_id = %s;", text, ctx.guild.id)
        await ctx.send("Прощание успешно изменено.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx, text):
        """
        set welcome text

        :param ctx: context
        :type ctx: commands.Context
        :param text: new welcome text
        :type text: str
        """
        with con.cursor() as cur:
            cur.execute(
                "UPDATE guilds SET welcome = %s WHERE guild_id = %s;", text, ctx.guild.id)
        await ctx.send("Приветствие успешно изменено.")


class UserChange(commands.Cog):
    """
    commands for users change
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def give(self, ctx, member: discord.Member, money):
        """

        :param ctx: context
        :type ctx: commands.Context
        :param member: member to give him some money
        :type member: discord.Member
        :param money: money to give
        :type money: int
        """
        money = int(money)
        with con.cursor() as cur:
            cur.execute("UPDATE users SET money = money+%s WHERE user_id = %s AND guild_id = %s;", money,
                        member.id,
                        ctx.guild.id)
        await ctx.send("{} вам выдано {} монет".format(member.mention, money))


def setup(bot):
    """
    setups bot

    :param bot: bot to setup
    :type bot: commands.Bot
    """
    bot.add_cog(BotChange(bot))
    bot.add_cog(UserChange(bot))
    print("Moderation finished")
