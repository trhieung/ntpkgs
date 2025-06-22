import importlib
import inspect
import re

from importlib.util import module_from_spec
from sys import modules
from typing import Dict
from pathlib import Path
from dataclasses import dataclass

class NTDocs:
    def __init__(self, pkg_name: str, save_dir: Path):
        self.pkg_name = pkg_name
        self.docs_dir = save_dir / "documentations"
        self.templates: Dict[str, Dict[str, str]] = {}

        self.release_order = [
            "technical/index.md",
            "technical/installation.md",
            "technical/usage.md",
            "modules/techincal_details.md",
            "modules/<ALL_MODULES>",
            "technical/changelog.md"
        ]

        self.setup_template()

    def setup_template(self):
        """Set up default technical documentation template."""
        technical = {
            "index.md": "# Overview\n\nThis package provides tools for...",
            "installation.md": "# Installation\n\n```bash\npip install yourlib\n```",
            "usage.md": "# Usage\n\nExample usage patterns for the main functions.",
            "technical_details.md": "# Technical details",
            "changelog.md": "# Changelog\n\n- v0.1.0: Initial release",
        }

        self.add_template(name="technical", tree=technical)

    def add_template(self, name: str, tree: Dict[str, str]):
        """Add a new documentation template under a named category."""
        self.templates[name] = tree

    def build_templates(self):
        """Generate the documentation files from templates."""
        for section, files in self.templates.items():
            section_dir = self.docs_dir / section
            section_dir.mkdir(parents=True, exist_ok=True)

            for filename, content in files.items():
                file_path = section_dir / filename
                file_path.write_text(content, encoding="utf-8")

    def build_modules(self):
        """Extract public classes/functions from symbols in __all__ and write docs."""
        try:
            top_module = importlib.import_module(self.pkg_name)
        except ImportError as e:
            print(f"Error importing {self.pkg_name}: {e}")
            return

        if not hasattr(top_module, "__all__"):
            print(f"Module {self.pkg_name} has no __all__ attribute.")
            return

        modules: Dict[str, Dict[str, str]] = {}

        for symbol_name in top_module.__all__:
            try:
                obj = getattr(top_module, symbol_name)
            except AttributeError:
                continue

            public_members = {}

            # For classes: include public methods
            if inspect.isclass(obj):
                for name, member in inspect.getmembers(obj):
                    if name.startswith("_"):
                        continue
                    if inspect.isfunction(member) or inspect.ismethod(member):
                        doc = inspect.getdoc(member) or "*No docstring provided.*"
                        public_members[name] = doc

            # For functions directly in __all__
            elif inspect.isfunction(obj):
                doc = inspect.getdoc(obj) or "*No docstring provided.*"
                public_members[symbol_name] = doc

            if public_members:
                modules[symbol_name] = public_members

        # Generate Markdown files
        module_docs_dir = self.docs_dir / "modules"
        module_docs_dir.mkdir(parents=True, exist_ok=True)

        for modname, contents in modules.items():
            doc_lines = [f"## `{modname}`\n"]
            for symbol, docstring in contents.items():
                doc_lines.append(f"### `{symbol}`\n\n{docstring}\n")
            doc_text = "\n".join(doc_lines)

            doc_path = module_docs_dir / f"{modname}.md"
            doc_path.write_text(doc_text, encoding="utf-8")

    def build_release(self):
        release_lines = []
        toc_lines = ["# Table of Contents\n"]
        modules_dir = self.docs_dir / "modules"

        for item in self.release_order:
            if item == "modules/<ALL_MODULES>":
                all_mod_files = sorted(
                    f for f in modules_dir.glob("*.md")
                    if f.name != "technical_details.md"
                )
                for f in all_mod_files:
                    content = f.read_text()
                    release_lines.append(content)
                    toc_lines.extend(self._extract_headers_for_toc(content))
            else:
                fpath = self.docs_dir / item
                if fpath.exists():
                    content = fpath.read_text()
                    release_lines.append(content)
                    toc_lines.extend(self._extract_headers_for_toc(content))

        toc = "\n".join(toc_lines)
        full_release = toc + "\n\n" + "\n\n".join(release_lines)
        (self.docs_dir / "release.md").write_text(full_release, encoding="utf-8")

    def _extract_headers_for_toc(self, content: str) -> list[str]:
        """Extract Markdown headers and convert them to TOC links."""
        toc_entries = []
        for line in content.splitlines():
            match = re.match(r"^(#{1,6})\s+(.*)", line)
            if match:
                level, title = match.groups()
                indent = "  " * (len(level) - 1)
                slug = self._slugify(title)
                toc_entries.append(f"{indent}- [{title}](#{slug})")
        return toc_entries
    
    def _slugify(self, text: str) -> str:
        return re.sub(r"[^\w]+", "-", text.strip().lower()).strip("-")
