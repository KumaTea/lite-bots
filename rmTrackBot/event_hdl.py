import json
from telegram import Update
from core import bot, inline_query, start, logging


def event_handler(event, context):
    res = {
        'statusCode': 200,
        'body': ''
    }
    method = event['requestContext']['http']['method']
    try:
        if not method == "POST":
            res['body'] = 'I am working!'
            return res
        update = Update.de_json(json.loads(event['body']), bot)
        if update.inline_query:
            res['body'] = str(inline_query(update))
        elif update.message:
            msg = update.message
            if msg.chat.id > 0:
                res['body'] = str(msg.reply_text(start()))
        else:
            logging.info('Undefined update type, ignoring...')
    except Exception as e:
        logging.error(
            f'\nERROR:\n'
            f'  Incoming request: {str(event["body"])}\n'
            f'  Exception: {str(e)}\n'
        )
    return res
