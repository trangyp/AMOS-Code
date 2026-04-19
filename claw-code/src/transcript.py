from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class TranscriptStore:
    entries: List[str] = field(default_factory=list)
    flushed: bool = False

    def append(self, entry: str) -> None:
        self.entries.append(entry)
        self.flushed = False

    def compact(self, keep_last: int = 10) -> None:
        if len(self.entries) > keep_last:
            self.entries[:] = self.entries[-keep_last:]

    def replay(self) -> Tuple[str, ...]:
        return tuple(self.entries)

    def flush(self) -> None:
        self.flushed = True
