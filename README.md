# AI Blockchain Watchlist Agent

This project is a personalized AI agent that suggests a crypto watchlist based on on-chain and derivatives data, interacting with the user via a Telegram bot.

The agent accepts a user-defined list of cryptocurrencies, fetches relevant data, analyzes it using a flexible, rule-based scoring system, and delivers a prioritized watchlist on a daily schedule.

## Features

- **Telegram Bot Interface**: Control the agent through simple commands on Telegram.
- **Customizable Watchlist**: Easily set and change the list of cryptocurrencies you want to monitor.
- **Rule-Based Analysis**: The agent uses a `rules.json` file to score assets. You can easily customize the rules, metrics, and scores to match your own trading strategy.
- **Prioritized Reports**: Assets are categorized into "High," "Medium," and "Low" priority tiers.
- **Scheduled Delivery**: Automatically receive your watchlist report every day at a configured time.
- **Mock Data Mode**: Runs without live API keys by using built-in mock data, allowing for easy setup and testing.

## Setup and Installation

**1. Prerequisites:**
- Python 3.8+
- A Telegram account

**2. Clone the repository:**
```bash
git clone <repository_url>
cd <repository_directory>
```

**3. Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

**4. Install dependencies:**
```bash
pip install -r crypto_watchlist_bot/requirements.txt
```

## Configuration

The agent is configured using a `.env` file. A template is provided in `.env.example`.

**1. Create the `.env` file:**
Copy the example file to a new file named `.env`:
```bash
cp crypto_watchlist_bot/.env.example .env
```

**2. Edit the `.env` file:**
You now need to fill in the values in the new `.env` file.

- **`TELEGRAM_BOT_TOKEN`**: (Required) This is the token for your Telegram bot.
    - Open Telegram and search for the **@BotFather** account.
    - Send the `/newbot` command and follow the instructions to create your bot.
    - BotFather will give you a unique API token. Copy this token and paste it into your `.env` file.

- **`TELEGRAM_CHAT_ID`**: (Required for scheduled reports) This is your personal Telegram user ID, which the bot needs to know where to send the scheduled reports.
    - Open Telegram and search for the **@userinfobot**.
    - Start a chat with it, and it will immediately reply with your User ID.
    - Copy this ID and paste it into your `.env` file.

- **API Keys**: (Optional) If you want to use live data, you need to provide API keys. If you leave these blank, the bot will use mock data.
    - `ETHERSCAN_API_KEY`: Get a free key from [https://etherscan.io/apis](https://etherscan.io/apis).
    - `COINGECKO_API_KEY`: Get a free key from [https://www.coingecko.com/en/api](https://www.coingecko.com/en/api).

## Usage

**1. Run the bot:**
Once your `.env` file is configured, you can run the bot from the root directory of the project using the following command:
```bash
python -m crypto_watchlist_bot.main
```
You should see a "Bot is starting..." message.

**2. Interact with the bot on Telegram:**
Find the bot you created on Telegram and use the following commands:
- `/start`: Shows the welcome message and list of commands.
- `/showwatchlist`: Displays the list of coins currently being monitored.
- `/setwatchlist <coin1>,<coin2>,...`: Sets your watchlist. For example: `/setwatchlist bitcoin, ethereum, chainlink`.
- `/run`: Manually triggers the generation of a new watchlist report and sends it to you immediately.

## Customization

You can change the agent's analysis logic by editing the `crypto_watchlist_bot/rules.json` file. The file is split into two main sections:

- **`rules`**: An array of rules to score assets. Each rule has:
    - `metric`: The data point to check (e.g., `funding_rate`).
    - `condition`: How to check the value (`less_than` or `greater_than`).
    - `value`: The threshold for the condition.
    - `score`: The points to add if the condition is met.
    - `reason`: The text that appears in the report.
- **`categories`**: Defines the score thresholds for each priority level.

You can add, remove, or modify these rules to fit your personal strategy without changing any Python code.
