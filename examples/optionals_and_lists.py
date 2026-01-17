from datetime import datetime
from typing import NamedTuple

from autotui import prompt_namedtuple


# describe a meeting with one or more people
class Meeting(NamedTuple):
    when: datetime
    where: str | None  # asks if you want to add this
    people: list[str]  # asks if you want to add another item


m = prompt_namedtuple(Meeting)
print(m)
