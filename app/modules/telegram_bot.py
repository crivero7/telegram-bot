import logging
import os
import sys
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
from .parser_html import ParserHTML
from extensions import verify_credentials, telegram_handler


class TelegramBot:
    r"""
    Documentation here
    """

    def __init__(self, token, company):
        
        # Configurar Logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s,"
        )

        self.logger = logging.getLogger()
        self.admin = ['Crivero7']
        self.COMPANY = company
        self.token = token
        self._PEN_VES = None
        self._CLP_VES = None

        self.bot = telegram.Bot(token=token)
    
        # Enlazamos nuestro updater con nuestro bot
        self.updater = Updater(self.bot.token, use_context=True)

        # Creamos un despachador
        self.dp = self.updater.dispatcher

        # Creamos los manejadores
        self.dp.add_handler(CommandHandler("start", self.start))
        self.dp.add_handler(CommandHandler("horario", self.horario))
        self.dp.add_handler(CommandHandler("PEN_VES", self.PEN_VES))
        self.dp.add_handler(CommandHandler("CLP_VES", self.CLP_VES))
        self.dp.add_handler(CommandHandler("reset_exchanges", self.reset_exchanges))
        self.dp.add_handler(CommandHandler("get_admins", self.get_admins))
        self.dp.add_handler(MessageHandler(Filters.text, self.handler_message))

    @verify_credentials
    @telegram_handler
    def get_admins(self, update, context):
        r"""
        Documentation here
        """
        msg = ''
        for admin in self.admin:

            msg += '<b>{}</b>\n'.format(admin)
        
        return msg

    def run(self, mode='dev'):

        if mode=='dev':
            self.updater.start_polling()
            self.updater.idle()
        
        elif mode=='prod':
            PORT = int(os.environ.get('PORT', '8443'))
            HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
            #Code from https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
            self.updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=self.token)
            self.updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, self.token))

        else:
            self.logger.INFO("No se especifico el mode")
            sys.exit()

    @telegram_handler
    def start(self, update, context):
        r"""
        Documentation here
        """
        first_name = update['message']['chat']['first_name']
        username = update['message']['chat']['username']
        msg = ParserHTML.open('start.html', first_name=first_name, company=self.COMPANY)
        if username in self.admin:
        
            msg = ParserHTML.open('start_admin.html', first_name=first_name, company=self.COMPANY)
        
        return msg

    @telegram_handler
    def horario(self, update, context):
        r"""
        Documentation here
        """
        first_name = update['message']['chat']['first_name']
        msg = ParserHTML.open('horario.html', first_name=first_name)
        
        return msg

    @telegram_handler
    def PEN_VES(self, update, context):
        
        msg = "<b>PEN_VES</b>\n{}".format(self._PEN_VES)
        if not self._PEN_VES:
            first_name = update['message']['chat']['first_name']
            msg = "<b>{}</b>, No tenemos tasa disponible".format(first_name)
        
        return msg

    @telegram_handler
    def CLP_VES(self, update, context):
        r"""
        Documentation here
        """

        first_name = update['message']['chat']['first_name']
        msg = "<b>CLP_VES</b>\n{}".format(self._CLP_VES)
        if not self._CLP_VES:
            
            msg = "<b>{}</b>, No tenemos tasa disponible".format(first_name)
        
        return msg
    
    def calculadora(self, update, context):
        r"""
        Documentation here
        """
        pass

    def handler_message(self, update, context):
        r"""
        Documentation here
        """
        first_name = update['message']['chat']['first_name']
        username = update['message']['chat']['username']
        user_id = update['message']['chat']['id']
        text = update.message.text

        if text.startswith('set exchange'):
            
            if username in self.admin:

                value = text.split(': ')[-1]
                currency =  text.split(': ')[0]
                currency =  currency.split('set exchange ')[-1]
                func_name = text.split(':')[0].replace(' ', '_')
                
                if hasattr(self, func_name):
                    func = getattr(self, func_name)
                    func(value)
                    msg = ParserHTML.open('success.html', first_name=first_name)

                    context.bot.sendMessage(
                        chat_id=user_id,
                        parse_mode="HTML",
                        text=msg)
                
                else:

                    msg = ParserHTML.open('currency_not_available.html', first_name=first_name, currency=currency)

                    context.bot.sendMessage(
                        chat_id=user_id,
                        parse_mode="HTML",
                        text=msg)

            else:
            
                msg = ParserHTML.open('not_allowed.html', first_name=first_name)

                context.bot.sendMessage(
                    chat_id=user_id,
                    parse_mode="HTML",
                    text=msg)

        elif text.startswith('add admin'):

            new_admin = text.split('add admin: ')[-1]

            msg = self.add_admin(update, context, username=new_admin)

            context.bot.sendMessage(
                chat_id=user_id,
                parse_mode="HTML",
                text=msg)


        elif text.startswith('remove admin'):

            user = text.split('remove admin: ')[-1]

            msg = self.remove_admin(update, context, username=user)

            context.bot.sendMessage(
                chat_id=user_id,
                parse_mode="HTML",
                text=msg)

    def set_exchange_PEN_VES(self, value):
        r"""
        Documentation here
        """
        self._PEN_VES = value

    def set_exchange_CLP_VES(self, value):
        r"""
        Documentation here
        """
        self._CLP_VES = value

    @verify_credentials
    @telegram_handler
    def reset_exchanges(self, update, context):
        r"""
        Documentation here
        """
        first_name = update['message']['chat']['first_name']
        self._PEN_VES = None
        self._CLP_VES = None
            
        return ParserHTML.open('success.html', first_name=first_name)

    @verify_credentials
    def add_admin(self, update, context, username=None):
        r"""
        Documentation here
        """
        first_name = update['message']['chat']['first_name']
        if username not in self.admin:
            
            self.admin.append(username)
            
            return ParserHTML.open('success.html', first_name=first_name)

        return '<b>{}</b> ya es un administrador'.format(username)

    @verify_credentials
    def remove_admin(self, update, context, username=None):
        r"""
        Documentation here
        """
        first_name = update['message']['chat']['first_name']
        if username in self.admin:
            
            self.admin.remove(username)
            
            return ParserHTML.open('success.html', first_name=first_name)

        return '<b>{}</b> no era administrador'.format(username)

