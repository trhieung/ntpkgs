import sys
from pathlib import Path

# Setup paths
base = Path(__file__).parent.parent

sys.path.append(str(base / "dev"))

from ntwheel import NTWheel, EnvModel # type: ignore

def ntexample_workspace():
    ntexample_dir = base/"prod/ntexample"

    runner = NTWheel(
        session_name="build_test",
        env=EnvModel(
            python_version="3.11",
            pkgs_req_dir=str(ntexample_dir/"offline_packages/ubuntu"),
            pkg_dir=str(ntexample_dir/"dev"),
            build_dir=str(ntexample_dir/"prod/build"),
            test_files={
                str(ntexample_dir / "prod/usage/test.py"): []
            },
            release_dir = str(ntexample_dir/"prod/release"),
        ),
        envdir_path=str(ntexample_dir/"prod/build/.nox"),
    )

    runner.run()

def ntdocs_workspace():
    ntdocs_dir = base/"prod/ntdocs"

    runner = NTWheel(
        session_name="build_test",
        env=EnvModel(
            python_version="3.11",
            pkgs_req_dir=str(ntdocs_dir/"offline_packages/ubuntu"),
            pkg_dir=str(ntdocs_dir/"dev"),
            build_dir=str(ntdocs_dir/"prod/build"),
            test_files={
                str(ntdocs_dir / "prod/usage/test.py"): []
            },
            release_dir = str(ntdocs_dir/"prod/release"),
        ),
        envdir_path=str(ntdocs_dir/"prod/build/.nox"),
    )

    runner.run()

def ntlog_workspace():
    ntlog_dir = base/"prod/ntlog"

    runner = NTWheel(
        session_name="build_test",
        env=EnvModel(
            python_version="3.11",
            pkgs_req_dir=str(ntlog_dir/"offline_packages/ubuntu"),
            pkg_dir=str(ntlog_dir/"dev"),
            build_dir=str(ntlog_dir/"prod/build"),
            test_files={
                str(ntlog_dir / "prod/usage/test.py"): []
            },
            release_dir = str(ntlog_dir/"prod/release"),
        ),
        envdir_path=str(ntlog_dir/"prod/build/.nox"),
    )

    runner.run()

# ntdocs_workspace()
ntlog_workspace()