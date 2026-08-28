from bot import Synto

from settings import settings


def main():
    bot = Synto()

    bot.run(settings.bot_token)


if __name__ == '__main__':
    main()