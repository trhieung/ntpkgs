import logging
from ntlog import NTLog  # type: ignore

nt:logging.Logger = NTLog.get_default()
nt.info(f"hi")
nt.warning(f"hu")
nt.critical(f"hic")