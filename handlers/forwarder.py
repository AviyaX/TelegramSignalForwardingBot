# handlers/forwarder.py

"""Message forwarding handler for the Telegram bot.

This module contains the handler for processing and forwarding trading messages.
"""

import logging
from typing import Optional

from telethon import TelegramClient, events
from telethon.tl.types import Message

from config import source_groups, destination_group
from utils.llm_processor import process_with_llm

logger = logging.getLogger(__name__)

def register_handlers(client: TelegramClient) -> None:
    """Register message handlers for the Telegram client.
    
    Args:
        client: The Telegram client instance to register handlers for.
    """
    
    @client.on(events.NewMessage(chats=source_groups))
    async def message_handler(event: events.NewMessage.Event) -> None:
        """Handle new messages from source groups.
        
        Args:
            event: The new message event from Telegram.
        """
        try:
            message: Message = event.message
            message_text: str = message.raw_text
            
            # Log which source group the message came from
            chat = await event.get_chat()
            logger.info(f"Received message from source group: {chat.title} (ID: {chat.id})")

            if not message_text:
                logger.debug("Skipping empty message")
                return

            # Process message through LLM for validation and formatting
            is_valid, reason, formatted_message = process_with_llm(message_text)
            
            if not is_valid:
                logger.debug(f"Skipping invalid trading message: {reason}")
                return
                
            if formatted_message:
                # Create a new message with the formatted text
                await client.send_message(
                    destination_group,
                    formatted_message,
                    link_preview=False  # Disable link preview for cleaner messages
                )
                
                logger.info(
                    "Successfully processed and forwarded trading message:\n"
                    f"Original:\n{message_text}\n\n"
                    f"Formatted:\n{formatted_message}"
                )
            else:
                logger.warning("LLM formatting failed, forwarding original message")
                await client.forward_messages(destination_group, message)
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            # If there's an error in processing, forward the original message as fallback
            try:
                await client.forward_messages(destination_group, event.message)
                logger.info("Forwarded original message as fallback")
            except Exception as forward_error:
                logger.error(f"Failed to forward original message: {str(forward_error)}", exc_info=True)
