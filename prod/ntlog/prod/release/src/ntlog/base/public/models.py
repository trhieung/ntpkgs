import logging

from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class LogModel:
    instance_name: str
    level: int = logging.INFO
    to_file: bool = False
    to_stream: bool = True
    log_file: Optional[Path] = None

    def __post_init__(self):
        if self.to_file and not self.log_file:
            raise ValueError("log_file must be specified if to_file is True")