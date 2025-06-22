from gettext import install
import os
import nox
import json

from nox.sessions import Session
from pathlib import Path

from ntwheel.base.public.models import EnvModel
from ntwheel.base.private.installer import Installer

# Dynamically set Python version from environment
python_version = os.environ.get("PYTHON_VERSION", "3.10")

@nox.session(python=python_version)
def build_test(session: Session):
    # Try to load NTWHEEL_ENV if provided (as JSON)
    env_json = os.environ.get("NTWHEEL_ENV", "")
    if not env_json:
        print("[NTWheel] Warning: NTWHEEL_ENV not set. Skipping build.")
        return

    try:
        env_dict = json.loads(env_json)
        env = EnvModel.from_env_dict(env_dict)
    except Exception as e:
        session.error(f"[NTWheel] Failed to parse NTWHEEL_ENV: {e}")
        return

    # Log all config
    print(f"📦 PKG_DIR                 = {env.pkg_dir}")
    print(f"📦 BUILD_DIR               = {env.build_dir}")
    print(f"📦 RELEASE_DIR             = {env.release_dir}")
    print(f"▶️ TEST_FILES              = {env.test_files}")
    print(f"📄 PKGS_REQ_DIR            = {env.pkgs_req_dir}")
    print(f"🐍 PYTHON_VERSION          = {env.python_version}")
    print(f"📛 SESSION_NAME            = {session.name}")

    # Install and run
    installer = Installer(
        session=session, 
        build_dir=Path(env.build_dir), 
        pkg_dir=Path(env.pkg_dir),
        release_dir=Path(env.release_dir)
    )
    installer.packages_offline(Path(env.pkgs_req_dir))
    installer.clean_pycache(Path(env.pkg_dir))
    
    wheel_path = installer.wheel_build()

    installer.wheel_install(wheel_path)
    installer.wheel_test(env.test_files)

    installer.wheel_release()
