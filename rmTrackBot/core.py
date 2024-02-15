import os
import re
import logging
import telegram
import requests
from uuid import uuid4
from typing import Optional
from urllib.parse import urlparse, ParseResult
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update


TIMEOUT = 5
DESC_MAX_LEN = 64

url_pattern = re.compile(
    r'https?://(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|'
    r'www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|'
    r'https?://(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|'
    r'www\.[a-zA-Z0-9]+\.[^\s]{2,}'
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

bot = telegram.Bot(token=os.environ["BOT_TOKEN"])


def refresh_url(url: str) -> str:
    r = requests.get(url, timeout=TIMEOUT)
    # r.raise_for_status()
    return r.url


def shorten_url(parsed: ParseResult) -> str:
    """
    Shorten URL just for display
    :param parsed:
    :return:
    """
    netloc = parsed.netloc.replace('www.', '')
    path = parsed.path
    url = f'{netloc}{path}'
    if len(url) > DESC_MAX_LEN:
        url = f'{url[:DESC_MAX_LEN//2 - 2]}...{url[-DESC_MAX_LEN//2 + 2:]}'
    return url


def decode_url(url: str) -> list[dict[str, str]]:
    results = []

    if not url:
        results.append(
            {
                'title': '未找到网址',
                'description': '无法在您的输入中找到网址',
                'content': '请重新输入有效网址',
            }
        )
        return results

    parse_url = urlparse(url)
    clean_url = f'{parse_url.scheme}://{parse_url.netloc}{parse_url.path}'
    try:
        new_url = refresh_url(url)
        assert url_pattern.match(new_url)
    except Exception as e:
        logging.error(f'\nERROR getting {url}:\n  {e}\n\n')
        results.append(
            {
                'title': '离线解析',
                'description': shorten_url(parse_url),
                'content': clean_url,
            }
        )
        return results

    parse_new_url = urlparse(new_url)
    clean_new_url = f'{parse_new_url.scheme}://{parse_new_url.netloc}{parse_new_url.path}'

    if clean_url != clean_new_url:
        # convert from short link
        results.append(
            {
                'title': '原链结果',
                'description': shorten_url(parse_url),
                'content': clean_url,
            }
        )

    results.append(
        {
            'title': '解析结果',
            'description': shorten_url(parse_new_url),
            'content': clean_new_url,
        }
    )

    return results


def inline_query(update: Update) -> Optional[bool]:
    query = update.inline_query.query
    if not query:
        return logging.info('inline: not update.inline_query.query')

    match_url = url_pattern.match(query) or ''
    results = decode_url(match_url)

    articles = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=result['title'],
            description=result['description'],
            input_message_content=InputTextMessageContent(result['content']),
        )
        for result in results
    ]
    return update.inline_query.answer(articles)


def start() -> str:
    return (
        '欢迎使用本机器人！\n'
        '使用方式：\n'
        '`@rmTrackBot <url>`'
    )
