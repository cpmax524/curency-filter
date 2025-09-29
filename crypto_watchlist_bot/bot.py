import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from . import data_collector, analysis

# --- Report Generation Logic ---

async def generate_watchlist_report() -> str:
    """
    Fetches top tokens from Dune, filters them based on analysis,
    and generates a formatted string report.
    """
    try:
        # 1. Get the initial list of top tokens
        top_tokens = data_collector.get_top_tokens()
        if not top_tokens:
            return "Could not retrieve top tokens from Dune Analytics. The report cannot be generated."
    except Exception as e:
        # Make sure to catch potential exceptions from the data_collector, like the ValueError for the missing API key.
        print(f"Error during token fetching: {e}")
        return f"⚠️ Error: Could not fetch tokens from Dune Analytics. Please ensure the DUNE_API_KEY is set correctly. Details: {e}"

    # 2. Filter the tokens using the analysis logic
    # This function now contains the loop and API calls with delays
    promising_tokens = analysis.filter_tokens(top_tokens)

    # 3. Format the final report message
    if not promising_tokens:
        return "✅ Analysis complete. No tokens were found matching the specified criteria today."

    message = "📈 *Promising Token Watchlist Report* 📈\n\n"
    message += "Here are the tokens that meet the criteria (GT Score > 70, Top 10 Holders < 50%):\n"

    for token in promising_tokens:
        message += "\n"
        # Using MarkdownV2 requires escaping some characters, but the default Markdown parse mode is more lenient.
        # Let's stick to simple Markdown. Using `<code>` for the address is good practice.
        message += f"🔹 *Name:* {token.get('name', 'N/A')} ({token.get('symbol', 'N/A')})\n"
        message += f"   *Address:* `{token.get('address', 'N/A')}`\n"

        market_cap = token.get('market_cap')
        if isinstance(market_cap, (int, float)):
            message += f"   *Market Cap:* ${market_cap:,.2f}\n"
        else:
            message += f"   *Market Cap:* {market_cap or 'N/A'}\n"

        gt_score = token.get('gt_score')
        if isinstance(gt_score, (int, float)):
            message += f"   *GT Score:* {gt_score:.2f}\n"
        else:
            message += f"   *GT Score:* {gt_score or 'N/A'}\n"

        top_10_holders = token.get('top_10_holders')
        if isinstance(top_10_holders, (int, float)):
            message += f"   *Top 10 Holders %:* {top_10_holders:.2f}%\n"
        else:
            message += f"   *Top 10 Holders %:* {top_10_holders or 'N/A'}%\n"

    return message


# --- Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message when the /start command is issued."""
    welcome_text = (
        "Welcome to the Automated Crypto Watchlist Bot! 🤖\n\n"
        "This bot automatically scans for promising new tokens based on Dune Analytics data and GeckoTerminal scores.\n\n"
        "Here are the commands you can use:\n"
        "*/start* - Show this welcome message\n"
        "*/run* - Manually generate and send the latest token report"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def run_report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /run command, generating and sending the report."""
    await update.message.reply_text("⏳ Generating your report... This may take a few minutes as it involves analyzing multiple tokens.")
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
    application.add_handler(CommandHandler("run", run_report_command))

    return application

def run(application: Application):
    """Runs the bot's polling loop."""
    print("Bot is starting to poll for messages...")
    application.run_polling()