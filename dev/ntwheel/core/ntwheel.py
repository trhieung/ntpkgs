import os
import sys
import json
import shlex
import subprocess

from pathlib import Path
from typing import Optional

from ntwheel.base.public.models import EnvModel

class NTWheel:
    def __init__(
        self,
        session_name:str,
        env: EnvModel,
        noxfile_path: Optional[str] = None,
        envdir_path: Optional[str] = None,
        report_path: Optional[str] = None,
    ):
        self.env = env

        core_dir = Path(__file__).parent
        self.session_name = session_name

        self.noxfile_path = str(noxfile_path or (core_dir / "noxfile.py"))
        self.envdir_path = str(envdir_path or (core_dir / ".nox" / f"py{env.python_version.replace('.', '')}_{self.session_name}"))
        self.report_path = str(report_path or (core_dir / "report.json"))

    def run(self):
        cmd = [
            "nox",
            "--noxfile", self.noxfile_path,
            "--envdir", self.envdir_path,
            "-s", self.session_name,
        ]

        current_folder = Path(__file__).resolve().parent
        pkg_dir = current_folder.parent.parent

        proc_env = os.environ.copy()
        proc_env["PYTHONPATH"] = str(pkg_dir) 
        proc_env["NTWHEEL_ENV"] = json.dumps(self.env.to_dict())
        proc_env["PYTHON_VERSION"] = self.env.python_version
        
        print(f"[NTWheel] Running: {' '.join(shlex.quote(arg) for arg in cmd)}")

        try:
            subprocess.run(cmd, check=True, env=proc_env)
        except subprocess.CalledProcessError as e:
            print(f"[NTWheel] Nox failed with exit code {e.returncode}")
        except FileNotFoundError:
            print("[NTWheel] Error: 'nox' command not found. Did you install it?")
