"""Data pipeline functions."""
from pandas import DataFrame, read_excel, concat
from pathlib import Path
import os
from typing import List
import random

from wordzilla.telegrambot import TelegramBot
from wordzilla.credentials import get_credentials


def extract_cambridge(
    directory_path: str
) -> DataFrame:
  """Extract all cambridge excels to a unique dataframe.

  The dataframe will be saved in the transform directory.
  """
  # List all Excel files in the directory
  cambridge_path = Path(directory_path) / 'cambridge'
  excel_files: List[str] = [
      f for f in os.listdir(cambridge_path) if f.endswith(('.xlsx', '.xls'))
  ]

  # Load and clean each Excel file
  dataframes: List[DataFrame] = []
  for file in excel_files:
    # Read the Excel file
    df = read_excel(cambridge_path / file)
    # Drop the first row and reset the index
    df = df.iloc[1:].reset_index(drop=True)
    # Drop the last column
    df = df.iloc[:, :-1]
    # Rename the remaining columns
    df.columns = ['name', 'type', 'description']
    # Append the cleaned DataFrame
    dataframes.append(df)

  # Concatenate all cleaned DataFrames
  return concat(dataframes, ignore_index=True)


def transform(
    cambridge: DataFrame
) -> DataFrame:
  """Concatenate and clean all transformed DataFrames.

  The result will be saved in the load directory.
  """
  union = concat([
      cambridge
  ])
  return union.fillna('?').drop_duplicates()


def telegram(data: DataFrame) -> None:
  """Send a message to telegram group."""
  # Random word
  random_row = data.iloc[random.randint(0, len(data) - 1)].to_dict()

  # Instantiate the bot
  cds = get_credentials()
  token = cds['telegram']['token']
  chat_id = cds['telegram']['chat_id']
  bot = TelegramBot(token)

  # Send to group
  bot.send_message(chat_id, f'{random_row['name']} ({random_row['type']})')
