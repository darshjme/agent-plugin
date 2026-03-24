"""Base Plugin class for all agent plugins."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar


class Plugin(ABC):
    """Base class for all agent plugins.

    Subclasses must define the ``name`` class attribute. Optionally override
    ``version``, ``on_load``, and ``on_unload`` for custom lifecycle behaviour.

    Example::

        class MyPlugin(Plugin):
            name = "my-plugin"
            version = "1.0.0"

            def on_load(self, context: dict) -> None:
                print(f"Loaded with context: {context}")

            def on_unload(self) -> None:
                print("Unloaded")
    """

    #: Unique identifier for the plugin — MUST be set by every subclass.
    name: ClassVar[str]

    #: Semantic version string.
    version: str = "0.1.0"

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        # __abstractmethods__ is populated by ABCMeta *after* __init_subclass__,
        # so check the class dict directly for abstract members instead.
        is_abstract = any(
            getattr(v, "__isabstractmethod__", False)
            for v in cls.__dict__.values()
        )
        # Only enforce name on concrete (non-abstract) subclasses.
        if not is_abstract:
            if not hasattr(cls, "name") or not isinstance(cls.name, str) or not cls.name:
                raise TypeError(
                    f"Plugin subclass '{cls.__name__}' must define a non-empty "
                    "class attribute 'name: str'."
                )

    def __init__(self) -> None:
        self._active: bool = False

    @property
    def is_active(self) -> bool:
        """Return ``True`` if the plugin has been loaded and not yet unloaded."""
        return self._active

    def on_load(self, context: dict) -> None:  # noqa: D401
        """Called by the registry when the plugin is loaded.

        Override to perform initialisation (connect to services, read config …).
        """

    def on_unload(self) -> None:
        """Called by the registry when the plugin is unloaded.

        Override to perform teardown (close connections, flush caches …).
        """

    def __repr__(self) -> str:
        status = "active" if self._active else "inactive"
        return f"<Plugin name={self.name!r} version={self.version!r} status={status}>"
