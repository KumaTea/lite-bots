import os
import re
import logging
import telegram
import requests
from uuid import uuid4
from typing import Optional
from dataclasses import dataclass
from auth import inline_from_valid_user
from urllib.parse import urlparse, ParseResult
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update


TIMEOUT = 5
DESC_MAX_LEN = 64
CONTENT_MAX_SIZE = 4096

WELCOME = (
    '欢迎使用本 bot!\n'
    '使用方式：\n'
    '`@rmTrackBot <url>`\n\n'
    '本 bot 不向TG大会员提供服务 '
    '('
    '[1](https://t.me/KumaSpace/1220) '
    '[2](https://t.me/KumaSpace/1225) '
    '[3](https://t.me/KumaSpace/1288)'
    ')'
)


@dataclass
class WebResult:
    title: str
    description: str
    content: str
    no_preview: bool = False


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
    r = requests.get(url, stream=True, timeout=TIMEOUT)
    # r.raise_for_status()
    content = b''
    for chunk in r.iter_content(chunk_size=1024):
        content += chunk
        if len(content) > CONTENT_MAX_SIZE:
            break
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


def decode_url(url: str) -> list[WebResult]:
    results = []

    if not url:
        results.append(
            WebResult(
                title='未找到网址',
                description='无法在您的输入中找到网址',
                content='请重新输入有效网址',
                no_preview=True,
            )
        )
        return results

    parse_url = urlparse(url)
    clean_url = f'{parse_url.scheme}://{parse_url.netloc}{parse_url.path}'
    try:
        new_url = refresh_url(url)
        assert url_pattern.search(new_url)
    except Exception as e:
        logging.error(f'\nERROR getting {url}:\n  {e}\n\n')
        results.append(
            WebResult(
                title='离线解析',
                description=shorten_url(parse_url),
                content=clean_url,
            )
        )
        return results

    parse_new_url = urlparse(new_url)
    clean_new_url = f'{parse_new_url.scheme}://{parse_new_url.netloc}{parse_new_url.path}'

    if clean_url != clean_new_url:
        # convert from short link
        results.append(
            WebResult(
                title='原链结果',
                description=shorten_url(parse_url),
                content=clean_url,
            )
        )

    results.append(
        WebResult(
            title='解析结果',
            description=shorten_url(parse_new_url),
            content=clean_new_url,
        )
    )
    results.append(
        WebResult(
            title='关闭预览',
            description=shorten_url(parse_new_url),
            content=clean_new_url,
            no_preview=True,
        )
    )

    return results


def inline_query(update: Update) -> Optional[bool]:
    query = update.inline_query.query
    if not query:
        return logging.info('inline: not update.inline_query.query')

    if inline_from_valid_user(update):
        search_url = url_pattern.search(query)
        if search_url:
            match_url = search_url.group()
        else:
            match_url = ''
        results = decode_url(match_url)
    else:
        results = [
            WebResult(
                title='非法请求',
                description='拒绝服务，请私聊 bot 查看帮助',
                content='未收到有效请求，请私聊 @rmTrackBot 查看帮助。',
            )
        ]

    articles = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=result.title,
            description=result.description,
            input_message_content=InputTextMessageContent(
                result.content,
                disable_web_page_preview=result.no_preview,
            ),
        )
        for result in results
    ]
    return update.inline_query.answer(articles)
