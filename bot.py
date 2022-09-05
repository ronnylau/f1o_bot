#code is based on https://github.com/SmCTwelve/f1-bot
#credits to https://github.com/SmCTwelve for your good base

import logging
import sys
import os
sys.path.append(os.path.join(sys.path[0], 'f1o', 'updatechecker'))
from f1o import commands

logger = logging.getLogger(__name__)
logger.warning('Starting bot...')

commands.bot.run(os.getenv('BOT_TOKEN'))

