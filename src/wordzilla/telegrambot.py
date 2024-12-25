"""Telegram Bot."""
import asyncio
import signal
from telegram import Update
from telegram._message import Message
from telegram.ext import (
    ApplicationBuilder, MessageHandler, ContextTypes, filters
)
from pandas import read_csv
import re
from typing import cast, Optional

from wordzilla.log import log
from wordzilla.user import User
from wordzilla.word import Word
from wordzilla.credentials import get_credentials


class TelegramBot():
  """Telegram bot."""

  def __init__(self, token):
    """Initialize the bot with a given token."""
    self.token = token
    # Build the application instance with the provided token.
    self.application = ApplicationBuilder().token(self.token).build()

  def send_message(self, chat_id: int, text: str):
    """Send a message to a specific Telegram chat."""
    # Use asyncio to run the bot's send_message method synchronously.
    asyncio.run(self.application.bot.send_message(chat_id=chat_id, text=text))

  async def handle_bot_replies(
      self, update: Update, context: ContextTypes.DEFAULT_TYPE
  ):
    """Handle replies to messages previously sent by the bot."""
    # Extract the user message and the message being replied to.
    user_message = cast(Message, update.message)
    bot_message = cast(Message, user_message.reply_to_message)

    # Check if the original message was sent by the bot.
    bot_sent_previous_message = (
        bot_message.from_user is not None
        and bot_message.from_user.id == context.bot.id
    )
    valid_format = _validate_format(bot_message.text)

    log.debug(
        f'User message: {user_message.text};'
        f'Bot message: {bot_message.text};'
        f'bot_message.from_user: {bot_message.from_user};'
        f'valid_format: {valid_format};'
    )

    # Process the reply only if it targets a valid bot message.
    if bot_message and bot_sent_previous_message and valid_format:
      # Retrieve the user information from the update.
      user = self.get_user_info(user_message.from_user)
      log.debug(f'User: {user}')

      # Extract the user's response message.
      response_message = user_message.text
      log.debug(f'User response: {response_message}')

      # Extract and parse the original bot message.
      original_message = str(bot_message.text)

      # Find the word in the dataset using parsed name and type.
      word = _look_for_word_in_data(
          name=original_message.split(' (')[0],
          type=_extract_text_in_parentheses(original_message)
      )

      # Concatenate definitions for the response.
      definitions = ''
      for definition in word.definitions:
        definitions += f'▶️ {definition}\n'

      # Send the definitions back to the user.
      await context.bot.send_message(
          chat_id=user_message.chat_id,
          text=definitions,
          reply_to_message_id=user_message.message_id
      )

  @staticmethod
  def get_user_info(user) -> User:
    """Extract user information from the update."""
    # Format the username, defaulting to '?' if unavailable.
    nick = (f'@{user.username}' if user.username else '?')
    return User(user.full_name, nick, user.id)

  async def start(self):
    """Start the bot and begin polling for updates."""
    # Add a message handler to process text messages.
    self.application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND, self.handle_bot_replies
        )
    )
    log.info('Starting bot.')
    # Initialize and start the application.
    await self.application.initialize()
    await self.application.start()
    if self.application.updater:
      await self.application.updater.start_polling(drop_pending_updates=True)

  async def stop(self):
    """Stop the bot gracefully."""
    log.info('Stopping bot...')
    # Stop the updater and application.
    if self.application.updater:
      await self.application.updater.stop()
    await self.application.stop()
    log.info('Bot stopped.')


def _look_for_word_in_data(name: str, type: str) -> Word:
  """Search for a word and its definitions in the dataset."""
  # Load the dataset from the specified CSV file.
  data = read_csv('data_etl/2_load/union.csv')
  # Filter rows based on the given name and type.
  rows = data[
      (data.name == name) & (data.type == type)
  ]
  # Extract the definitions from matching rows.
  definitions = [row['description'] for _, row in rows.iterrows()]
  return Word(
      name=name,
      type=type,
      definitions=definitions
  )


def _validate_format(text: Optional[str]) -> bool:
  """Validate the format of a given text message."""
  if text is None:
    return False
  else:
    # Ensure the text matches the format: "word (type)" or "word (?)".
    pattern = r'^[\w\s]+ \([\w\s?,]+\)$'
    return bool(re.match(pattern, text))


def _extract_text_in_parentheses(text: str) -> str:
  """Extract text contained within parentheses."""
  match = re.search(r'\((.*?)\)', text)
  return match.group(1) if match else ''


def run_bot():
  """Initialize and run the bot."""
  # Retrieve the token from environment or credentials.
  cds = get_credentials()
  token = cds['telegram'].get('token')
  if not token:
    raise ValueError('Environment variable TELEGRAM_TOKEN is not set')

  bot = TelegramBot(token)
  loop = asyncio.get_event_loop()
  stop_event = asyncio.Event()

  # Define a handler for termination signals.
  def stop_handler(*_):
    log.info('Received stop signal.')
    stop_event.set()

  # Register signal handlers for graceful termination.
  for sig in (signal.SIGINT, signal.SIGTERM):
    loop.add_signal_handler(sig, stop_handler)

  try:
    # Start the bot and wait for a termination signal.
    loop.run_until_complete(bot.start())
    loop.run_until_complete(stop_event.wait())
  finally:
    # Stop the bot and close the event loop.
    loop.run_until_complete(bot.stop())
    loop.close()
