# Extend the package path to support namespace packages
import pkgutil
__path__ = pkgutil.extend_path(__path__, __name__)

from .core.ntdocs import NTDocs

__all__ = [
    "NTDocs"
]