"""agent-plugin: Production plugin system for extending LLM agents."""

from .plugin import Plugin
from .registry import PluginRegistry
from .hooks import HookSystem
from .loader import PluginLoader

__all__ = ["Plugin", "PluginRegistry", "HookSystem", "PluginLoader"]
__version__ = "0.1.0"
