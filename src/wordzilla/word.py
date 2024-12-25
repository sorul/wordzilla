from typing import List


# class Definition:
#   def __init__(self, type: str, definition: str):
#     self.type = type
#     self.definition = definition


class Word:
  def __init__(
      self,
      name: str,
      type: str,
      definitions: List[str]
  ):
    self.name = name
    self.type = type
    self.definitions = definitions
