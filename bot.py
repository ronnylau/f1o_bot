#code is based on https://github.com/SmCTwelve/f1-bot
#credits to https://github.com/SmCTwelve for your good base

import logging
import os

import f1.config

logger = logging.getLogger(__name__)
logger.warning('Starting bot...')


commands.bot.run(os.getenv('BOT_TOKEN', f1.config.CONFIG['BOT']['TOKEN']))
