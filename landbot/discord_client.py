#!python3

"""LandBot - Discord chatbot serving the landcore community.

(c) 2020 Yalishanda.
"""

from discord import Client, Intents, Message, Member
import transliterate

import random

import landbot.commands as commands
from landbot.external_api.rhymes.mixed_fallback import MixedFallbackAPI


def help() -> str:
    return """И ето пак команда с '.' се задава.
LandBot-a я вижда и веднага отговаря.

Ето някои примери:
* `.rhyme robot`
Ще дам няколко рими на 'robot'.
* `.rhyme robot 22`
Ще дам най-много 22 рими на 'robot'.
* `.римувай кон`
Ще дам няколко рими на 'кон'.
* `.поздрав фми`
Ще пратя в чата песента 'ФМИ' (демек линк към YouTube видеото).
* `.link live`
Ще пратя всички лайв ландкор изгъзици.
* `.песен`
Ще пратя случайно-избрана песен.
* `.test`
Ще те разсмея. Може би. Нз. Ама при всеки случай ще разбереш дали съм онлайн.
* `.help`
Ще напиша това, което четеш сега.

Повече инфо винаги има тук: https://github.com/yalishanda42/landbot.
Очаква се да мога да правя и още неща в бъдеще.
Приятно ландкориране.
"""


class LandBot(Client):
    """Bot implementation."""

    # Constants

    COMMAND_START_SYMBOL = "."

    _TEST_CMD = ("test", "t", ".", "ping", "pong")

    _HELP_CMD = ("help", "introduce", "h", "?", "pomosht")

    _RHYME_CMD = (
        "rh",
        "rhyme",
        "rhymes",
        "rimi",
        "rima",
        "rimichki",
        "rimichka",
        "rimuvay",
    )

    _LINK_CMD = (
        "l",
        "s",
        "yt",
        "link",
        "song",
        "pesen",
        "youtube",
        "pozdrav",
        "greetings",
        "greet",
    )

    _WELCOME_MESSAGES = (
        "И ето пак във ~~вратата~~ сървъра влезе {0}",
        "Раз, два, три, четири... айде пет\n"
        "В сървъра влезе {0}, пожелавам им късмет",
        "{0} стиска ви здраво ръката",
        "Схема 1, схема 2, при {0} всичко е добре."
    )

    _WELCOME_USER_DM = """Добре дошъл в сървъра! Аз съм ландкор бота.
Само да знаеш, че мога изпълявам команди, започващи с точка.
Може да пробваш тука .help за повече информация."""

    # Factory

    @classmethod
    def create(cls):
        """Create a new LandBot instance with all the necessary intents."""
        intents = Intents(members=True, messages=True)
        return cls(intents=intents)


    # Overrides

    async def on_ready(self):
        """Client is connected."""
        print(f"Bot logged in as {self.user}.")

    async def on_member_join(self, member: Member):
        """Handle a user joining the server."""
        print(f"User {member} joined the server!")

        if member.bot:
            return

        out_format = random.choice(self._WELCOME_MESSAGES)
        out_msg = out_format.format(f"**{member.name}**")
        for channel in member.guild.channels:
            if channel.name == 'general':  # welp...
                await channel.send(out_msg)

        usr_msg = self._WELCOME_USER_DM
        await member.send(usr_msg)

    async def on_message(self, message: Message):
        """Listen for patterns and execute commands."""
        if message.author == self.user:
            return

        msg = message.content.lower()
        msg_parts = msg.split()
        msg_parts[0] = transliterate.translit(msg_parts[0],
                                              "bg",
                                              reversed=True)

        if "bafta" in msg or "бафта" in msg:
            await message.channel.send("*hahaa*")

        if len(msg_parts) < 1 or not msg[0] == self.COMMAND_START_SYMBOL:
            return

        print(f"Received command: {msg}")

        msg_parts[0] = msg_parts[0][len(self.COMMAND_START_SYMBOL):]

        out_msg = ""

        if msg_parts[0] in self._TEST_CMD:
            out_msg = commands.ping()

        elif msg_parts[0] in self._RHYME_CMD:
            # 'Rhyme' command synthax:
            # .{command} {term} [{max_rhymes}]
            term = msg_parts[1]
            max_rhymes = 10 if len(msg_parts) < 3 else int(msg_parts[2])

            rhymeslist = commands.rhymes(term, max_rhymes, api=MixedFallbackAPI())
            
            rows = [f"> {rhyme}" for rhyme in rhymeslist]
            out_msg = "\n".join(rows) if rows else "Нема рими батко"

        elif msg_parts[0] in self._HELP_CMD:
            out_msg = help()

        elif msg_parts[0] in self._LINK_CMD and len(msg_parts) >= 2:
            out_msg = commands.link(" ".join(msg_parts[1:]))

        elif msg_parts[0] in self._LINK_CMD and len(msg_parts) == 1:
            out_msg = commands.random_link()

        if not out_msg:
            return

        await message.channel.send(out_msg)
    
