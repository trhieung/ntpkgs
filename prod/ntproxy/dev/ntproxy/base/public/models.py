
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProxyModel:
    type: str
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None

    TYPES = ['socks5h']

    def __post_init__(self):
        if self.type not in self.TYPES:
            raise ValueError(f"Unsupported proxy type: {self.type}")