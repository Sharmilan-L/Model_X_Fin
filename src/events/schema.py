# src/events/schema.py

from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict
from uuid import uuid4
from datetime import datetime

@dataclass
class Event:
    id: str
    source_type: str          # 'gov', 'news', 'weather', 'youtube', 'gdelt'
    raw_source: str           # e.g. 'Disaster Management Centre', 'Ada Derana'
    title: str
    summary: str
    url: Optional[str]
    timestamp: str            # ISO string
    event_type: Optional[str] = None     # will be filled by classifier later
    severity: Optional[float] = None     # will be filled by scorer later
    districts: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    extra: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


def make_event_id() -> str:
    return f"EVT-{uuid4().hex[:12].upper()}"


def now_utc_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"
