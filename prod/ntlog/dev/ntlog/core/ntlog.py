import logging
import sys
from pathlib import Path
from ntlog.base.public.models import LogModel
from ntlog.base.private.abstract import Helper

# ANSI color codes
COLOR_CODES = {
    'DEBUG': '\033[94m',    # Blue
    'INFO': '\033[92m',     # Green
    'WARNING': '\033[93m',  # Yellow
    'ERROR': '\033[91m',    # Red
    'CRITICAL': '\033[95m', # Magenta
}
RESET_CODE = '\033[0m'


class NTLog(Helper):
    def __init__(self, config: LogModel):
        if config.to_file and not config.log_file:
            raise ValueError("log_file must be specified if to_file is True")
        self.config: LogModel = config

    def get(self) -> logging.Logger:
        logger = logging.getLogger(self.config.instance_name)
        logger.setLevel(self.config.level)

        if not logger.handlers:
            base_fmt = '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'

            # File handler (no color)
            if self.config.to_file:
                if not self.config.log_file:
                    raise ValueError("log_file must be specified if to_file is True")
                
                log_path = Path(self.config.log_file)
                log_dir = log_path.parent
                if log_dir and not log_dir.exists():
                    log_dir.mkdir(parents=True, exist_ok=True)

                file_handler = logging.FileHandler(str(log_path), encoding='utf-8')
                file_handler.setFormatter(logging.Formatter(base_fmt))
                logger.addHandler(file_handler)

            # Stream handler (with inline color logic)
            if self.config.to_stream:
                stream_handler = logging.StreamHandler()
                stream_handler.setFormatter(logging.Formatter(base_fmt))

                def emit_colored(self, record: logging.LogRecord):
                    color = COLOR_CODES.get(record.levelname, "")
                    if 'utf-8' in (sys.stdout.encoding or '').lower() and color:
                        record.levelname = f"{color}{record.levelname}{RESET_CODE}"
                        record.msg = f"{color}{record.msg}{RESET_CODE}"
                    return logging.StreamHandler.emit(self, record)

                # Patch emit with color logic
                stream_handler.emit = emit_colored.__get__(stream_handler, logging.StreamHandler)
                logger.addHandler(stream_handler)

        if not (self.config.to_stream or self.config.to_file):
            print("Warning: Logger configured with no output targets.")

        return logger

    @staticmethod
    def get_default() -> logging.Logger:
        return NTLog(LogModel(
            instance_name="DefaultLogger",
            level=logging.DEBUG,
            to_stream=True
        )).get()
