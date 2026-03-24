"""Tests for PluginRegistry."""

import pytest
from agent_plugin import Plugin, PluginRegistry


class Alpha(Plugin):
    name = "alpha"
    def __init__(self):
        super().__init__()
        self.load_calls = 0
        self.unload_calls = 0
    def on_load(self, context):
        self.load_calls += 1
        self.ctx = context
    def on_unload(self):
        self.unload_calls += 1


class Beta(Plugin):
    name = "beta"


class TestRegistration:
    def test_register_single(self):
        reg = PluginRegistry()
        reg.register(Alpha())
        assert "alpha" in reg.list_registered()

    def test_register_multiple(self):
        reg = PluginRegistry()
        reg.register(Alpha())
        reg.register(Beta())
        assert set(reg.list_registered()) == {"alpha", "beta"}

    def test_register_duplicate_raises(self):
        reg = PluginRegistry()
        reg.register(Alpha())
        with pytest.raises(ValueError, match="already registered"):
            reg.register(Alpha())

    def test_register_non_plugin_raises(self):
        reg = PluginRegistry()
        with pytest.raises(TypeError):
            reg.register("not-a-plugin")  # type: ignore

    def test_get_registered(self):
        reg = PluginRegistry()
        a = Alpha()
        reg.register(a)
        assert reg.get("alpha") is a

    def test_get_missing_returns_none(self):
        reg = PluginRegistry()
        assert reg.get("missing") is None

    def test_len(self):
        reg = PluginRegistry()
        reg.register(Alpha())
        reg.register(Beta())
        assert len(reg) == 2


class TestLoad:
    def test_load_calls_on_load(self):
        reg = PluginRegistry()
        a = Alpha()
        reg.register(a)
        reg.load("alpha", context={"x": 1})
        assert a.load_calls == 1
        assert a.ctx == {"x": 1}

    def test_load_sets_active(self):
        reg = PluginRegistry()
        a = Alpha()
        reg.register(a)
        reg.load("alpha")
        assert a.is_active is True

    def test_load_default_empty_context(self):
        reg = PluginRegistry()
        a = Alpha()
        reg.register(a)
        reg.load("alpha")
        assert a.ctx == {}

    def test_load_missing_plugin_raises(self):
        reg = PluginRegistry()
        with pytest.raises(KeyError):
            reg.load("nonexistent")

    def test_load_already_loaded_raises(self):
        reg = PluginRegistry()
        reg.register(Alpha())
        reg.load("alpha")
        with pytest.raises(RuntimeError, match="already loaded"):
            reg.load("alpha")

    def test_list_loaded(self):
        reg = PluginRegistry()
        reg.register(Alpha())
        reg.register(Beta())
        reg.load("alpha")
        assert reg.list_loaded() == ["alpha"]

    def test_load_all(self):
        reg = PluginRegistry()
        reg.register(Alpha())
        reg.register(Beta())
        reg.load_all()
        assert set(reg.list_loaded()) == {"alpha", "beta"}

    def test_load_all_skips_already_loaded(self):
        reg = PluginRegistry()
        a = Alpha()
        reg.register(a)
        reg.load("alpha")
        reg.load_all()          # alpha is already active
        assert a.load_calls == 1  # not called twice


class TestUnload:
    def test_unload_calls_on_unload(self):
        reg = PluginRegistry()
        a = Alpha()
        reg.register(a)
        reg.load("alpha")
        reg.unload("alpha")
        assert a.unload_calls == 1

    def test_unload_clears_active(self):
        reg = PluginRegistry()
        a = Alpha()
        reg.register(a)
        reg.load("alpha")
        reg.unload("alpha")
        assert a.is_active is False

    def test_unload_not_loaded_raises(self):
        reg = PluginRegistry()
        reg.register(Alpha())
        with pytest.raises(RuntimeError, match="not loaded"):
            reg.unload("alpha")

    def test_unload_missing_raises(self):
        reg = PluginRegistry()
        with pytest.raises(KeyError):
            reg.unload("ghost")

    def test_unload_all(self):
        reg = PluginRegistry()
        reg.register(Alpha())
        reg.register(Beta())
        reg.load_all()
        reg.unload_all()
        assert reg.list_loaded() == []

    def test_repr(self):
        reg = PluginRegistry()
        reg.register(Alpha())
        reg.load("alpha")
        r = repr(reg)
        assert "registered=1" in r
        assert "loaded=1" in r
