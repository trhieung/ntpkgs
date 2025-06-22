
from platform import release
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from venv import create
from nox.sessions import Session

class Installer:
    def __init__(self, session: Session, build_dir: Path, pkg_dir:Path, release_dir:Path):
        """
        Initialize the handler with the Nox session and build directory.

        Args:
            session (Session): The Nox session object.
            build_dir (Path): Path to the build directory where temporary files and environments will be managed.
        """
        self.session = session
        self.build_dir = build_dir
        self.pkg_dir = pkg_dir
        self.release_dir = release_dir

        self.dist_dir = self.build_dir / "dist"
        self.egg_dir = self.build_dir / "egg"
        self.build_tmp_dir = self.build_dir / "build"

    def clean_artifacts(self, target: Path) -> None:
        """
        Abstract method to clean build artifacts from a given target directory.

        Args:
            target (str): Path to the target directory to be cleaned.
        """
        pass

    def clean_pycache(self, path: Path) -> None:
        """
        Recursively removes all `__pycache__` directories from the given path.

        Args:
            path (Path): The root directory to clean.
        """
        for pycache in path.rglob("__pycache__"):
            shutil.rmtree(pycache, ignore_errors=True)


    def wheel_install(self, wheel_path: Path) -> None:
        """
        Install a package directly from a wheel file.

        Args:
            wheel_path (Path): The path to the `.whl` file to install.
        """
        if not wheel_path.exists():
            raise FileNotFoundError(f"[Installer] Wheel not found: {wheel_path}")

        self.session.install(str(wheel_path))


    def wheel_test(self, test_files: Optional[Dict[str, List[str]]]=None) -> None:
        """
        Run test files with optional arguments.

        Args:
            test_files (dict): A mapping of test script paths (str) to lists of CLI arguments.
        """
        if not test_files:
            print("[Test] ⚠️  No test files provided.")
            return
        
        for file, args in test_files.items():
            file_path = Path(file)
            if not file_path.exists():
                print(f"[Test] ⚠️  Skipping missing test: {file_path}")
                continue

            try:
                print(f"[Test] ▶️ Running: {file} {' '.join(args)}")
                self.session.run("python", str(file_path), *args)
            except Exception as e:
                print(f"[Test] ❌ Failed test {file_path}: {e}")


    def wheel_build(self) -> Path:
        """
        Build a wheel package from the source directory into a clean output directory.

        Args:
            src_dir (Path): The directory containing the Python project (with setup.py or pyproject.toml).

        Returns:
            Path: Path to the most recently modified wheel file.
        """
        # Ensure self.dist_dir exists and is empty
        self.dist_dir.mkdir(parents=True, exist_ok=True)
        for item in self.dist_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

        # Ensure egg and build directories exist
        self.egg_dir.mkdir(parents=True, exist_ok=True)
        self.build_tmp_dir.mkdir(parents=True, exist_ok=True)

        # Build the wheel using setup.py
        self.session.chdir(self.pkg_dir)
        self.session.run(
            "python", "setup.py",
            "egg_info", f"--egg-base={self.egg_dir}",
            "build", f"--build-base={self.build_tmp_dir}",
            "bdist_wheel", f"--dist-dir={self.dist_dir}",
        )

        # Collect and return the newest wheel
        wheels = list(self.dist_dir.glob("*.whl"))
        if not wheels:
            raise RuntimeError(f"No wheel was built in {self.dist_dir}")
        return max(wheels, key=lambda w: w.stat().st_mtime)

    def wheel_release(self) -> None:
        """
        Finalize the wheel build process by:
        - Creating the release directory if it doesn't exist.
        - Exporting the current environment requirements to `requirements.txt`.
        - Copying built source files from the package directory to `release/src`.
        - Copying built wheel files to `release/release`.
        """
        # Ensure release directory exists
        self.release_dir.mkdir(parents=True, exist_ok=True)

        # Export installed requirements to requirements.txt in the release folder
        requirements_path = self.release_dir / "requirements.txt"
        self.packages_requirements_sync(export=True, path=requirements_path)

        # Copy source files from pkg_dir/* to release/src/*
        src_build_path = self.pkg_dir
        dst_src_path = self.release_dir / "src"

        if not src_build_path.exists():
            raise FileNotFoundError(f"[Release] Source package directory not found: {src_build_path}")

        dst_src_path.mkdir(parents=True, exist_ok=True)

        for item in src_build_path.iterdir():
            target = dst_src_path / item.name
            if item.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)

        # Copy wheel files from dist_dir/*.whl to release/release/*.whl
        dst_release_dir = self.release_dir / "release"
        dst_release_dir.mkdir(parents=True, exist_ok=True)

        wheel_files = list(self.dist_dir.glob("*.whl"))
        for wheel in wheel_files:
            shutil.copy2(wheel, dst_release_dir / wheel.name)

        print(f"[Release] ✅ Release created at {self.release_dir}")



    def packages_offline(self, offline_dir: Path) -> None:
        """
        Install packages from wheel files located in subdirectories under `offline_dir`.

        The structure is expected to be:
        offline_dir/
        ├── build/
        │   └── *.whl
        ├── setuptools/
        │   └── *.whl
        └── ...

        Args:
            offline_dir (Path): Path to the directory containing subfolders with wheel files.
        """
        if not offline_dir.exists():
            raise FileNotFoundError(f"[Handler] Offline directory does not exist: {offline_dir}")

        for subdir in offline_dir.iterdir():
            if subdir.is_dir():
                wheel_files = list(subdir.glob("*.whl"))
                if wheel_files:
                    print(f"\n📦 Installing wheels from: {subdir.name}")
                    for wheel in wheel_files:
                        print(f"  - {wheel.name}")

                    self.session.install(
                        "--no-index", 
                        "--find-links", 
                        str(subdir), *[str(w) for w in wheel_files],
                    )

    def packages_requirements_sync(self, export: bool, path: Path) -> None:
        """
        Sync the current environment’s requirements to or from a file.

        Args:
            export (bool): If True, export installed packages to the given file.
                        If False, install packages from the requirements file.
            path (Path): The path to the requirements file.
        """
        path.parent.mkdir(parents=True, exist_ok=True)

        if export:
            with open(path, "w") as f:
                self.session.run(
                    "pip", "list", "--format=freeze", external=True, stdout=f
                )
        else:
            self.session.install("-r", str(path))

