"""PluginRegistry — manages plugin lifecycle (register / load / unload)."""

from __future__ import annotations

from typing import Optional

from .plugin import Plugin


class PluginRegistry:
    """Central registry that tracks and drives plugin lifecycles.

    Usage::

        registry = PluginRegistry()
        registry.register(MyPlugin())
        registry.load("my-plugin", context={"api_key": "…"})
        print(registry.list_loaded())   # ["my-plugin"]
        registry.unload("my-plugin")
    """

    def __init__(self) -> None:
        # name → Plugin instance (registered, may or may not be active)
        self._plugins: dict[str, Plugin] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, plugin: Plugin) -> None:
        """Register *plugin* without loading it.

        Raises:
            TypeError: if *plugin* is not a :class:`Plugin` instance.
            ValueError: if a plugin with the same name is already registered.
        """
        if not isinstance(plugin, Plugin):
            raise TypeError(f"Expected a Plugin instance, got {type(plugin).__name__!r}.")
        if plugin.name in self._plugins:
            raise ValueError(
                f"A plugin named {plugin.name!r} is already registered. "
                "Unregister it first or use a different name."
            )
        self._plugins[plugin.name] = plugin

    def unregister(self, name: str) -> None:
        """Remove a plugin from the registry (unloading it first if active).

        Raises:
            KeyError: if no plugin with *name* is registered.
        """
        if name not in self._plugins:
            raise KeyError(f"No plugin named {name!r} is registered.")
        plugin = self._plugins[name]
        if plugin.is_active:
            self.unload(name)
        del self._plugins[name]

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def load(self, name: str, context: Optional[dict] = None) -> None:
        """Load the plugin identified by *name*, calling its ``on_load`` hook.

        Raises:
            KeyError:   if no plugin with *name* is registered.
            RuntimeError: if the plugin is already loaded.
        """
        plugin = self._get_or_raise(name)
        if plugin.is_active:
            raise RuntimeError(f"Plugin {name!r} is already loaded.")
        plugin.on_load(context or {})
        plugin._active = True  # noqa: SLF001

    def unload(self, name: str) -> None:
        """Unload the plugin identified by *name*, calling its ``on_unload`` hook.

        Raises:
            KeyError:   if no plugin with *name* is registered.
            RuntimeError: if the plugin is not currently loaded.
        """
        plugin = self._get_or_raise(name)
        if not plugin.is_active:
            raise RuntimeError(f"Plugin {name!r} is not loaded.")
        plugin.on_unload()
        plugin._active = False  # noqa: SLF001

    def load_all(self, context: Optional[dict] = None) -> None:
        """Load every registered plugin that is not already loaded."""
        for name, plugin in self._plugins.items():
            if not plugin.is_active:
                plugin.on_load(context or {})
                plugin._active = True  # noqa: SLF001

    def unload_all(self) -> None:
        """Unload every currently-active plugin."""
        for name, plugin in list(self._plugins.items()):
            if plugin.is_active:
                plugin.on_unload()
                plugin._active = False  # noqa: SLF001

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get(self, name: str) -> Optional[Plugin]:
        """Return the registered plugin with *name*, or ``None``."""
        return self._plugins.get(name)

    def list_registered(self) -> list[str]:
        """Return names of all registered plugins (loaded or not)."""
        return list(self._plugins.keys())

    def list_loaded(self) -> list[str]:
        """Return names of all currently-active (loaded) plugins."""
        return [n for n, p in self._plugins.items() if p.is_active]

    def __len__(self) -> int:
        return len(self._plugins)

    def __repr__(self) -> str:
        registered = len(self._plugins)
        loaded = len(self.list_loaded())
        return f"<PluginRegistry registered={registered} loaded={loaded}>"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_or_raise(self, name: str) -> Plugin:
        try:
            return self._plugins[name]
        except KeyError:
            raise KeyError(f"No plugin named {name!r} is registered.") from None
