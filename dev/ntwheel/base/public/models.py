from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import json


@dataclass
class EnvModel:
    python_version: str = "3.10"
    pkgs_req_dir: str = "ubuntu"
    pkg_dir: str = "dist"
    build_dir: str = "build"
    test_files: Optional[Dict[str, List[str]]] = None
    release_dir: str = "release"

    def __post_init__(self):
        # Ensure test_files is always a dict (not None or str)
        if self.test_files is None:
            self.test_files = {"test1.py": ["--arg1", "--flag"]}

    def to_dict(self) -> dict:
        """Convert the dataclass to an UPPER_CASE environment dict."""
        raw = asdict(self)
        return {k.upper(): v for k, v in raw.items()}

    @classmethod
    def from_env_dict(cls, env: Dict[str, str]) -> "EnvModel":
        """Create an EnvModel from an environment dict with UPPER_CASE keys."""
        def parse_test_files(value):
            if isinstance(value, dict):
                return value
            try:
                return json.loads(value)
            except Exception:
                return {"test1.py": ["--arg1", "--flag"]}

        normalized = {k.lower(): v for k, v in env.items()}
        return cls(
            python_version=normalized.get("python_version", "3.10"),
            pkg_dir=normalized.get("pkg_dir", "dist"),
            build_dir=normalized.get("build_dir", "build"),
            release_dir=normalized.get("release_dir", "release"),
            test_files=parse_test_files(normalized.get("test_files", {})),
            pkgs_req_dir=normalized.get("pkgs_req_dir", "ubuntu")
        )
