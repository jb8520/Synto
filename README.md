# Synto

Synto is a powerful discord bot with many utility and quality of life functions, including but not limited to: automatic voice channel functionality, games and other server activity boosting features, all of which are fully customisable via a graphical configuration command.

For help, support, or more information about the bot, head to the [Synto Support Server](https://discord.gg/MdsMmJvaJt), where you can open a ticket in the `#📩┃support` channel.



## Why Use Synto?
Whether you're running a small community or a large server, Synto brings useful features that make moderation, communication, and interaction more engaging — without needing 10 separate bots.



## Features

**Synto** gives you powerful tools for managing your server:
- 🔊 Automatic Voice Channels
- 🎲 Mini-games (TicTacToe, Connect 4)
- 💸 Casino and economy system
- 🔐 Full role/permission configuration
- 🎛️ Interactive configuration panel using Discord UI
- and many more!



## Getting Started

### Prerequisites

- Python 3.8+
- A Discord bot application created in the [Developer Portal](https://discord.com/login?redirect_to=%2Fdevelopers) (you'll need the bot token)
- MySQL Server (or compatible)
- Packages (requirements.txt):
    - discord.py==2.5.2
    - mysql-connector==1.1.0
    - python-dotenv==2.2.9


### Installation

```bash
git clone https://github.com/jb8520/synto.git
cd synto
pip install -r requirements.txt
```

Create a .env file and add your Discord bot token and database credentials (mysql.connector specific in this example):
```ini
BOT_OWNER_ID=
BOT_ID=

BOT_TOKEN=

DATABASE_HOST=
DATABASE_NAME=
DATABASE_PASSWORD=
DATABASE_USER=
```



## Usage

Run the bot:
```bash
python main.py
```



## Setup & Configuration

Use the `/setup` command to show information surrounding setting the bot up in a new discord server.
The `/configuration` command opens the configuration interface where the specific setup can be changed on a per server basis.



## Commands

#### Supported Commands

**Setup/Configuration:**
- `/setup`, guides the user through the setup process of the bot.
- `/configuration`, allows the user to customise the server specific settings of the bot.

**General:**
- `/bot-info`, displays information about the bot, such as latency and uptime.
- `/ping`, displays the latency of the bot.

**Auto Voice Channel:**
- `/control_panel`, puts the auto voice channel control panel into the channel the command is run.

**Counting Game:**
- `/counting_stats`, displays information about the server's counting progress, such as highscore and the current score achieved.

**Games:**
- `/tictactoe`, starts a 2 player game of tictactoe.
- `/connect4`, starts a 2 player game of connect 4.
- `/rps`, allows the user to play rock paper scissors against the bot.



## Contributing

Pull requests and issues are welcome! Please follow the coding style and add tests where possible.



## License

GNU AFFERO GENERAL PUBLIC LICENSE Version 3, © jb8520, James Boss
