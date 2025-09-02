import os
import schedule
import time
import threading
import asyncio
from dotenv import load_dotenv
from . import bot

def job(application):
    """The scheduled job that sends the report."""
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not chat_id:
        print("SCHEDULE: TELEGRAM_CHAT_ID not set, cannot send scheduled report.")
        return

    print("SCHEDULE: Generating scheduled report...")

    # We need to run the async function from this synchronous thread
    # The bot's application object gives us a running asyncio loop
    async def send_report():
        report = await bot.generate_watchlist_report()
        await application.bot.send_message(chat_id=chat_id, text=report, parse_mode='Markdown')
        print("SCHEDULE: Report sent successfully.")

    asyncio.run_coroutine_threadsafe(send_report(), application.loop)


def run_scheduler():
    """Runs the scheduler loop."""
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    """
    Main entry point for the application.
    Loads environment variables, sets up scheduling, and starts the bot.
    """
    print("Loading environment variables...")
    load_dotenv()

    try:
        application = bot.setup()
    except ValueError as e:
        print(f"FATAL: {e}")
        return

    # --- Scheduling Setup ---
    # You can change the schedule here.
    # For testing, you might use: schedule.every(1).minutes.do(job, application)
    schedule.every().day.at("08:00").do(job, application)
    print(f"Scheduled to run daily at 08:00. Current time: {time.strftime('%H:%M:%S')}")

    # Run the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # Start the bot
    bot.run(application)

if __name__ == "__main__":
    main()
