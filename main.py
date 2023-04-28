#!/usr/bin/env python

import glob
import logging
import discord
import datetime
from importlib import import_module

from cmds import help

CMINI_CHANNEL = 1063291226243207268

commands = [x.replace('/', '.')[5:-3] for x in glob.glob('cmds/*.py')]

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

logger = logging.getLogger('discord')

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')

@bot.event
async def on_message(message: discord.Message):
    args = message.content.split()

    # Is in a DM?
    is_dm = isinstance(message.channel, discord.channel.DMChannel)

    # Restricted command?
    restricted = message.channel.id != CMINI_CHANNEL and not is_dm

    # Ignore other bots
    if message.author.bot:
        return

    # Empty message
    if not args:
        return

    # Get command
    if is_dm:
        command = args[0].lower()
    else:
        # Check triggers
        if args[0] not in ['!amini', '!bmini', '!cmini', '!dvormini']:
            return

        # Get command if any
        if len(args) > 1:
            command = args[1].lower()
        else:
            command = None

    logger.info(f'{message.author.name}: {message.content}')

    # Trigger only
    if not command:
        reply = 'Try `!cmini help`'
    # Check commands
    elif command in commands:
        mod = import_module(f'cmds.{command}')
        reply = mod.exec(message)

        if restricted and (mod.RESTRICTED if hasattr(mod, 'RESTRICTED') else True):
            channel = await bot.create_dm(message.author)
            await channel.send(reply)
            return
    # Command not found
    else:
        reply = f'Error: {command} is not an available command'

    await message.channel.send(reply, reference=message)


def main():
    date = datetime.datetime.now()

    with open('token.txt', 'r') as f:
        token = f.read()

    bot.run(token)


if __name__ == '__main__':
    main()
