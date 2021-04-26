from functools import wraps
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from modules.parser_html import ParserHTML


def verify_credentials(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        self = args[0]
        update = args[1]
        first_name = update['message']['chat']['first_name']
        username = update['message']['chat']['username']
        if username in self.admin:
        
            return func(*args, **kwargs)

        return ParserHTML.open('success.html', first_name=first_name)

    return wrapper

def telegram_handler(func):
    
    @wraps(func)
    def wrapper(*args, **kwargs):

        self = args[0]
        self.dp.add_handler(CommandHandler(func.__name__, func))
        
        update = args[1]
        context = args[2]
        user_id = update['message']['chat']['id']

        msg = func(*args, **kwargs)

        context.bot.sendMessage(
            chat_id=user_id,
            parse_mode="HTML",
            text=msg)

    return wrapper
