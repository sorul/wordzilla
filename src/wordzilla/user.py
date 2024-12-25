"""User clas."""


class User:
  """User object for telegram bot."""

  def __init__(self, fullname: str, nick: str, id: str):
    """Construct."""
    self.fullname = fullname
    self.nick = nick
    self.id = id

  def __str__(self) -> str:
    """Returns a string."""
    return f'{self.fullname}:{self.nick}:{self.id}'
