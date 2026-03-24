"""Tests for the Plugin base class."""

import pytest
from agent_plugin import Plugin


# ---------------------------------------------------------------------------
# Concrete plugin fixtures
# ---------------------------------------------------------------------------

class SimplePlugin(Plugin):
    name = "simple"

    def __init__(self):
        super().__init__()
        self.loaded_context = None
        self.unloaded = False

    def on_load(self, context: dict) -> None:
        self.loaded_context = context

    def on_unload(self) -> None:
        self.unloaded = True


class VersionedPlugin(Plugin):
    name = "versioned"
    version = "2.3.4"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPluginInstantiation:
    def test_simple_plugin_instantiates(self):
        p = SimplePlugin()
        assert p is not None

    def test_name_attribute(self):
        p = SimplePlugin()
        assert p.name == "simple"

    def test_default_version(self):
        p = SimplePlugin()
        assert p.version == "0.1.0"

    def test_custom_version(self):
        p = VersionedPlugin()
        assert p.version == "2.3.4"

    def test_is_active_starts_false(self):
        p = SimplePlugin()
        assert p.is_active is False

    def test_repr_inactive(self):
        p = SimplePlugin()
        r = repr(p)
        assert "simple" in r
        assert "inactive" in r


class TestPluginLifecycle:
    def test_on_load_called_with_context(self):
        p = SimplePlugin()
        ctx = {"key": "value"}
        p.on_load(ctx)
        assert p.loaded_context == ctx

    def test_on_unload_called(self):
        p = SimplePlugin()
        p.on_unload()
        assert p.unloaded is True

    def test_is_active_toggled_manually(self):
        """Registry toggles _active; test direct toggle here."""
        p = SimplePlugin()
        p._active = True
        assert p.is_active is True
        p._active = False
        assert p.is_active is False

    def test_repr_active(self):
        p = SimplePlugin()
        p._active = True
        assert "active" in repr(p)


class TestPluginEnforcement:
    def test_missing_name_raises_typeerror(self):
        with pytest.raises(TypeError, match="name"):
            class BadPlugin(Plugin):
                pass  # no name attribute

    def test_empty_name_raises_typeerror(self):
        with pytest.raises(TypeError):
            class EmptyNamePlugin(Plugin):
                name = ""

    def test_abstract_base_allowed_without_name(self):
        """An abstract intermediate class need not set name."""
        from abc import abstractmethod

        class AbstractMiddle(Plugin):
            @abstractmethod
            def do_something(self): ...

        # No error — it's still abstract

    def test_on_load_default_noop(self):
        """Default on_load does nothing (no exception)."""
        p = VersionedPlugin()
        p.on_load({})  # should not raise

    def test_on_unload_default_noop(self):
        p = VersionedPlugin()
        p.on_unload()  # should not raise
