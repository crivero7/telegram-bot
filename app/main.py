from modules import TelegramBot
import os

if __name__ == '__main__':
    # Obtenemos informacion de nuestro bot
    token = os.getenv('TOKEN')
    company = os.getenv('COMPANY')
    mode = os.getenv('MODE')
    app = TelegramBot(token, company)
    app.run(mode=mode)