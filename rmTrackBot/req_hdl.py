from telegram import Update
from flask import request as FlaskRequest
from core import bot, inline_query, WELCOME, logging


def req_handler(request: FlaskRequest) -> str:
    res = ''
    try:
        if not request.method == 'POST':
            return 'I am working!'
        update = Update.de_json(request.get_json(force=True), bot)
        if update.inline_query:
            res = inline_query(update)
        elif update.message:
            msg = update.message
            if msg.chat.id > 0:
                res = msg.reply_text(WELCOME, parse_mode='Markdown', disable_web_page_preview=True)
        else:
            logging.info('Undefined update type, ignoring...')
    except Exception as e:
        logging.error(
            f'\nERROR:\n'
            f'  Incoming request: {str(request.get_json(force=True))}\n'
            f'  Exception: {str(e)}\n'
        )
    return str(res) if res else ''
