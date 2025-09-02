import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from . import data_collector, analysis

# --- Configuration and File Handling ---

CONFIG_DIR = os.path.dirname(__file__)
WATCHLIST_FILE = os.path.join(CONFIG_DIR, "watchlist.json")
RULES_FILE = os.path.join(CONFIG_DIR, "rules.json")

def load_json(file_path: str) -> dict:
    """Loads a JSON file and returns its content."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def load_watchlist() -> list[str]:
    """Loads the watchlist from its JSON file."""
    return load_json(WATCHLIST_FILE).get("coins", [])

def save_watchlist(coins: list[str]):
    """Saves the watchlist to its JSON file."""
    with open(WATCHLIST_FILE, "w") as f:
        json.dump({"coins": coins}, f, indent=2)

# --- Report Generation Logic ---

async def generate_watchlist_report() -> str:
    """
    Fetches data, analyzes it, and generates a formatted string report.
    """
    watchlist = load_watchlist()
    rules_config = load_json(RULES_FILE)

    if not watchlist:
        return "Your watchlist is empty. Add coins with `/setwatchlist`."
    if not rules_config:
        return "⚠️ Error: `rules.json` is missing or invalid. Cannot generate report."

    # In a real app, you would load these from a secure source
    api_keys = {
        "coingecko": os.getenv("COINGECKO_API_KEY"),
        "etherscan": os.getenv("ETHERSCAN_API_KEY"),
    }

    report_parts = {
        "high": [],
        "medium": [],
        "low": [],
    }
    all_errors = []

    for coin in watchlist:
        asset_data, errors = data_collector.fetch_all_data(coin, api_keys)
        all_errors.extend(errors)

        if not asset_data:
            continue

        score, reasons = analysis.analyze_asset(asset_data, rules_config)
        category_label = analysis.categorize_score(score, rules_config)

        reason_str = ", ".join(reasons) if reasons else "No specific signals"
        report_line = f"- **{coin.upper()}**: {reason_str} (Score: {score})"

        if "High" in category_label:
            report_parts["high"].append(report_line)
        elif "Medium" in category_label:
            report_parts["medium"].append(report_line)
        else:
            report_parts["low"].append(report_line)

    # Assemble the final report message
    message = "📈 *Your Crypto Watchlist Report* 📈\n\n"
    if report_parts["high"]:
        message += "🔥 *High Priority*\n" + "\n".join(report_parts["high"]) + "\n\n"
    if report_parts["medium"]:
        message += "🔶 *Medium Priority*\n" + "\n".join(report_parts["medium"]) + "\n\n"
    if report_parts["low"]:
        message += "🧊 *Low Priority*\n" + "\n".join(report_parts["low"]) + "\n\n"

    if not any(report_parts.values()):
        message += "Could not generate a report for any coin in your watchlist.\n\n"

    if all_errors:
        message += "⚠️ *Data Retrieval Errors*\n" + "\n".join(f"- {e}" for e in all_errors)

    return message


# --- Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message when the /start command is issued."""
    welcome_text = (
        "Welcome to the AI Blockchain Watchlist Agent! 🤖\n\n"
        "Here are the commands you can use:\n"
        "*/start* - Show this welcome message\n"
        "*/showwatchlist* - Display your current watchlist\n"
        "*/setwatchlist* <COIN1,...> - Set a new watchlist\n"
        "*/run* - Manually generate and send the report"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def show_watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the user's current watchlist."""
    watchlist = load_watchlist()
    if not watchlist:
        message = "Your watchlist is currently empty. Set one using `/setwatchlist`."
    else:
        message = "Your current watchlist:\n" + "\n".join(f"- {coin.capitalize()}" for coin in watchlist)
    await update.message.reply_text(message, parse_mode='Markdown')

async def set_watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sets or updates the user's watchlist."""
    if not context.args:
        await update.message.reply_text("Please provide a comma-separated list of coins.\n*Example:* `/setwatchlist bitcoin, ethereum`", parse_mode='Markdown')
        return

    input_string = " ".join(context.args)
    new_watchlist = [coin.strip().lower() for coin in input_string.split(',') if coin.strip()]

    if not new_watchlist:
        await update.message.reply_text("The watchlist cannot be empty. Please provide at least one coin.")
        return

    save_watchlist(new_watchlist)
    confirmation_message = "✅ *Watchlist updated successfully!*\n\nYour new watchlist:\n" + "\n".join(f"- {coin.capitalize()}" for coin in new_watchlist)
    await update.message.reply_text(confirmation_message, parse_mode='Markdown')

async def run_report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /run command, generating and sending the report."""
    await update.message.reply_text("⏳ Generating your watchlist report, please wait...")
    report_message = await generate_watchlist_report()
    # Using Markdown for better formatting
    await update.message.reply_text(report_message, parse_mode='Markdown')


def setup() -> Application:
    """Sets up the bot application and command handlers."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set. Please create a .env file.")

    application = Application.builder().token(token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("showwatchlist", show_watchlist_command))
    application.add_handler(CommandHandler("setwatchlist", set_watchlist_command))
    application.add_handler(CommandHandler("run", run_report_command))

    return application

def run(application: Application):
    """Runs the bot's polling loop."""
    print("Bot is starting to poll for messages...")
    application.run_polling()
