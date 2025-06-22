import ntexample

from ntdocs import NTDocs  # type: ignore
from pathlib import Path

prod_dir = Path(__file__).parent.parent

nt = NTDocs(pkg_name="ntexample", save_dir=prod_dir/"release") # type: ignore
nt.build_templates()
nt.build_modules()
nt.build_release()
