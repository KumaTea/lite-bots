from telegram import Update


known_user_ids = [
    # fill when deploy
]

bl_users = [
    # fill when deploy
]


def inline_from_valid_user(update: Update) -> bool:
    if not update.inline_query:
        return False
    if not update.inline_query.from_user:
        return False
    if update.inline_query.from_user.id in known_user_ids:
        return True
    if update.inline_query.from_user.id in bl_users:
        return False
    if update.inline_query.from_user.is_premium:
        return False
    return True
