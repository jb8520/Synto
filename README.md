# Synto

Synto is a powerful discord bot with many utility and quality of life functions, including but not limited to: automatic voice channel functionality, a counting game, welcome messages, and mini-games, all of which are fully customisable via a graphical configuration menu.

For help, support, or more information about the bot, head to the [Synto Support Server](https://discord.gg/MdsMmJvaJt), where you can open a ticket in the `#📩┃support` channel.



## Why Use Synto?

Whether you're running a small community or a large server, Synto brings useful features that make moderation, communication, and interaction more engaging — without needing 10 separate bots.



## Features

**Synto** gives you powerful tools for managing your server:
- 🔊 Automatic Voice Channels, fully owner-managed (lock, hide, rename, kick, invite, user limit)
- 🔢 A Counting game, with an optional double-count rule and a 60-second "Counting Save" grace period to undo a mistake
- 👋 Customisable Welcome Messages
- 🎲 Mini-games (TicTacToe, Connect 4, Rock Paper Scissors)
- 🛠️ A General settings section: admin role overrides, per-feature enable/disable toggles, and an announcements channel
- ✨ Synto Premium: unlocks multiple Auto VC setups and many other features
- 🎛️ Everything configurable through one interactive `/settings` menu, no text commands to memorise



## Getting Started

### Prerequisites

- Python 3.11+
- A Discord bot application created in the [Developer Portal](https://discord.com/login?redirect_to=%2Fdevelopers) (you'll need the bot token)
- MySQL Server (or compatible)
- If you want the Premium/Counting Saves monetisation features: a Guild Subscription SKU and three Consumable SKUs configured for your application under Monetization in the Developer Portal
- Packages (requirements.txt):
    - discord.py==2.5.2
    - mysql-connector==2.2.9
    - python-dotenv==1.2.2


### Installation

```bash
git clone https://github.com/jb8520/synto.git
cd synto
pip install -r requirements.txt
```

Create a `.env` file with your bot token, database credentials, and SKU IDs. The `DEV_*` variants are only needed if you run the bot with `--dev` (see [Usage](#usage)) — they let you develop against a separate bot application and database without touching production.

```ini
BOT_OWNER_ID=
BOT_ID=
DEV_BOT_ID=

BOT_TOKEN=
DEV_BOT_TOKEN=

DATABASE_HOST=
DATABASE_NAME=
DATABASE_USER=
DATABASE_PASSWORD=

DEV_DATABASE_HOST=
DEV_DATABASE_NAME=
DEV_DATABASE_USER=
DEV_DATABASE_PASSWORD=

# Synto Premium (Guild Subscription SKU)
SYNTO_PREMIUM_SKU_ID=
DEV_SYNTO_PREMIUM_SKU_ID=

# Counting Saves (Consumable SKUs)
COUNTING_SAVE_1_SKU_ID=
COUNTING_SAVE_3_SKU_ID=
COUNTING_SAVE_10_SKU_ID=
DEV_COUNTING_SAVE_1_SKU_ID=
DEV_COUNTING_SAVE_3_SKU_ID=
DEV_COUNTING_SAVE_10_SKU_ID=

# Optional - grants a role to Premium purchasers in your own support server.
# Leave unset to disable; the bot works fine without them.
SUPPORT_SERVER_ID=
SUPPORTER_ROLE_ID=
```


### Database Setup

Synto doesn't create its own tables on startup, so this has to be run manually once (and again after pulling any update that adds new tables/columns - it's safe to re-run, every statement is idempotent):

```bash
python database/schema.py
```

If you're migrating data from an older, pre-rework instance of the bot (its old `Auto_Vc`/`Counting`/`Welcome_Message`/`Metrics` tables), run the one-time migration afterwards:

```bash
python database/migrate_old_tables.py
```

This second script always targets the production database credentials directly (`DATABASE_*`, no `--dev` support) - only run it if you actually have old data to bring across.



## Usage

Run the bot against production:
```bash
python main.py
```

Run against your dev bot application and dev database instead:
```bash
python main.py --dev
```

Run your dev bot application against the production database (useful for testing against real data without a second database):
```bash
python main.py --dev --prod-db
```



## Setup & Configuration

The `/settings` (`/configuration` in earlier bot versions) command opens Synto's interactive configuration menu, where every feature below is set up and customised on a per-server basis - no other setup command is needed.



## Commands

#### Supported Commands

**Settings/Setup:**
- `/settings`, `/configuration` — opens the Synto settings menu.

**General:**
- `/bot-info`, displays information about the bot, such as latency and uptime.
- `/ping`, displays the latency of the bot.
- `/buy-me-a-coffee`, support Synto's development.

**Premium:**
- `/premium`, view or purchase Synto Premium for the current server.
- `/premium-status`, check whether the current server has Synto Premium.
- `/counting-saves`, buy Counting Saves - these belong to you, not a server, and work in any server that has them enabled.

**Auto Voice Channel:**
- `/control-panel`, puts the auto voice channel control panel into the channel the command is run.

**Counting Game:**
- `/counting-stats`, displays information about the server's counting progress, such as highscore and the current score achieved.

**Games:**
- `/tictactoe`, starts a 2 player game of tictactoe.
- `/connect4`, starts a 2 player game of connect 4.
- `/rps`, allows the user to play rock paper scissors against the bot.



## Contributing

Pull requests and issues are welcome! Please follow the coding style and add tests where possible.



## License

GNU AFFERO GENERAL PUBLIC LICENSE Version 3, © jb8520, James Boss