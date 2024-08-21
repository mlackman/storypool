from typing import Literal
import dataclasses


@dataclasses.dataclass
class Issue:
    id: str
    status: Literal['To Do', 'In Progress', 'Done']
    type: Literal['Feature', 'Bug', 'Epic']
    priority: Literal['High', 'Medium', 'Low']


@dataclasses.dataclass
class Stats:
    checked_at: str
    todo_count: int
    done_count: int


@dataclasses.dataclass
class VelocityStats:
    done_per_day: float
    estimated_done_date: str
