"""Telegram Bot."""
import asyncio
from telegram import Update
from telegram._message import Message
from telegram.ext._updater import Updater
from telegram.ext import (
    ApplicationBuilder, MessageHandler, ContextTypes, filters
)
from pandas import read_csv
import re
from typing import cast, Optional

from wordzilla.log import log
from wordzilla.credentials import get_credentials
from wordzilla.user import User
from wordzilla.word import Word


class TelegramBot():
  """Telegram bot."""

  def __init__(self, token):
    """Construct."""
    self.token = token
    self.application = ApplicationBuilder().token(self.token).build()
    self.updater = cast(Updater, self.application.updater)

  def send_message(self, chat_id: int, text: str):
    """Send a message to the telegram group."""
    asyncio.run(self.application.bot.send_message(chat_id=chat_id, text=text))

  async def handle_bot_replies(
      self, update: Update, context: ContextTypes.DEFAULT_TYPE
  ):
    """Handle replies."""
    user_message = cast(Message, update.message)
    bot_message = cast(Message, user_message.reply_to_message)

    bot_sent_previous_message = (
        bot_message.from_user is not None
        and bot_message.from_user.id == context.bot.id
    )
    valid_format = _validate_format(bot_message.text)
    # If the new message responds to another
    # previous one which was sent by the bot.
    if bot_message and bot_sent_previous_message and valid_format:
      # Información del usuario que responde
      user = self.get_user_info(user_message.from_user)
      log.debug(f'User: {user}')

      # Mensaje que responde el usuario
      response_message = user_message.text
      log.debug(f'User: {response_message}')

      # Mensaje original del bot
      original_message = str(bot_message.text)

      # Buscamos la palabra en los datos
      word = _look_for_word_in_data(
          name=original_message.split(' (')[0],
          type=_extract_text_in_parentheses(original_message)
      )

      definitions = ''
      for definition in word.definitions:
        definitions += f'▶️ {definition}\n'

      # Responder al usuario
      await context.bot.send_message(
          chat_id=user_message.chat_id,
          text=definitions,
          reply_to_message_id=user_message.message_id
      )

  @staticmethod
  def get_user_info(user) -> User:
    """Returns the User object for the given user."""
    nick = (f'@{user.username}' if user.username else '?')
    return User(user.full_name, nick, user.id)

  async def run(self):
    """Run the bot."""
    await self.application.initialize()
    self.application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND, self.handle_bot_replies
        )
    )

    log.info('Starting bot.')
    try:
      await self.application.start()
      await self.updater.start_polling(drop_pending_updates=True)
      await asyncio.Future()
    finally:
      log.info('Stopping bot.')
      await self.updater.stop()
      await self.application.stop()
      await self.application.shutdown()


def _look_for_word_in_data(name: str, type: str) -> Word:
  data = read_csv('data_etl/2_load/union.csv')
  rows = data[
      (data.name == name) & (data.type == type)
  ]
  definitions = [row['description'] for _, row in rows.iterrows()]
  return Word(
      name=name,
      type=type,
      definitions=definitions
  )


def _validate_format(text: Optional[str]) -> bool:
  if text is None:
    return False
  else:
    pattern = r'^[\w\s]+ \([\w\s]+\)$'
    return bool(re.match(pattern, text))


def _extract_text_in_parentheses(text: str) -> str:
  match = re.search(r'\((.*?)\)', text)
  return match.group(1) if match else ''


if __name__ == '__main__':
  cds = get_credentials()
  token = cds['telegram']['token']
  bot = TelegramBot(token)

  try:
    asyncio.run(bot.run())
  except KeyboardInterrupt:
    log.info('Bot stopped.')
