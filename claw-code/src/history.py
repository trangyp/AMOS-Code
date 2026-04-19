from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class HistoryEvent:
    title: str
    detail: str


@dataclass
class HistoryLog:
    events: List[HistoryEvent] = field(default_factory=list)

    def add(self, title: str, detail: str) -> None:
        self.events.append(HistoryEvent(title=title, detail=detail))

    def as_markdown(self) -> str:
        lines = ["# Session History", ""]
        lines.extend(f"- {event.title}: {event.detail}" for event in self.events)
        return "\n".join(lines)
