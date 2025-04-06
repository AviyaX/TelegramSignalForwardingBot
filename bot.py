"""Telegram bot for forwarding and processing trading messages.

This module initializes and runs the Telegram client that handles message forwarding.
"""

import logging
import sys
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from config import api_id, api_hash, phone, source_groups
from handlers.forwarder import register_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize Telegram client
client = TelegramClient('session_name', api_id, api_hash)

async def main():
    """Main function to run the bot."""
    try:
        # Connect and sign in if necessary
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            logger.info("Please check your Telegram account for the login code.")
            try:
                await client.sign_in(phone)
            except SessionPasswordNeededError:
                logger.error("Two-step verification is enabled. Please disable it or implement password handling.")
                return

        # Log source groups
        logger.info(f"Monitoring the following source groups: {source_groups}")

        # Register message handlers
        register_handlers(client)
        
        logger.info("Bot started successfully. Listening for messages...")
        await client.run_until_disconnected()
        
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        raise

if __name__ == "__main__":
    # Start the client
    with client:
        client.loop.run_until_complete(main())
