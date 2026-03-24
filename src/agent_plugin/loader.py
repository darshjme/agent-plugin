"""PluginLoader — discovers and dynamically loads Plugin subclasses from files."""

from __future__ import annotations

import importlib.util
import inspect
import sys
from pathlib import Path
from typing import List

from .plugin import Plugin


class PluginLoader:
    """Discover and load :class:`Plugin` subclasses from a directory.

    Example::

        loader = PluginLoader("/path/to/plugins")
        files = loader.discover()          # ["weather_plugin.py", …]
        plugin = loader.load_from_file("/path/to/plugins/weather_plugin.py")
        print(plugin.name)                 # "weather"
    """

    def __init__(self, plugin_dir: str) -> None:
        self.plugin_dir = Path(plugin_dir).resolve()
        if not self.plugin_dir.exists():
            raise FileNotFoundError(f"Plugin directory not found: {self.plugin_dir}")

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def discover(self) -> List[str]:
        """Return a sorted list of Python file paths that contain Plugin subclasses.

        Only files at the top level of ``plugin_dir`` are scanned (no recursion).
        Files starting with ``_`` (e.g. ``__init__.py``) are skipped.
        """
        found: List[str] = []
        for py_file in sorted(self.plugin_dir.glob("*.py")):
            if py_file.name.startswith("_"):
                continue
            if self._file_has_plugin_subclass(py_file):
                found.append(str(py_file))
        return found

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load_from_file(self, path: str) -> Plugin:
        """Dynamically import *path* and return the first concrete Plugin subclass instance.

        Raises:
            FileNotFoundError: if *path* does not exist.
            ValueError:        if the file contains no concrete Plugin subclass.
        """
        file_path = Path(path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"Plugin file not found: {file_path}")

        module = self._load_module(file_path)
        plugin_class = self._find_plugin_class(module, file_path)
        return plugin_class()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_module(self, file_path: Path):
        """Import a Python file as a module, reloading if already imported."""
        module_name = f"_agent_plugin_dynamic.{file_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot create module spec for {file_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        return module

    def _find_plugin_class(self, module, file_path: Path) -> type:
        """Return the first concrete Plugin subclass defined in *module*."""
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, Plugin)
                and obj is not Plugin
                and not inspect.isabstract(obj)
                # Only classes actually defined in this module (not imported ones)
                and obj.__module__ == module.__name__
            ):
                return obj
        raise ValueError(
            f"No concrete Plugin subclass found in {file_path}. "
            "Make sure the file defines a class that extends Plugin with a 'name' attribute."
        )

    def _file_has_plugin_subclass(self, file_path: Path) -> bool:
        """Return True if *file_path* contains a line that looks like a Plugin subclass.

        This is a fast heuristic scan (no import) to avoid executing every .py
        file in the directory during discovery.
        """
        try:
            text = file_path.read_text(encoding="utf-8")
            return "Plugin" in text and "name" in text
        except (OSError, UnicodeDecodeError):
            return False

    def __repr__(self) -> str:
        return f"<PluginLoader plugin_dir={str(self.plugin_dir)!r}>"
