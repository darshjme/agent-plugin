"""Tests for PluginLoader."""

import os
import textwrap
import pytest
from pathlib import Path
from agent_plugin import PluginLoader


@pytest.fixture()
def plugin_dir(tmp_path):
    """A temp directory with two valid plugin files and one non-plugin file."""
    # Valid plugin 1
    (tmp_path / "weather_plugin.py").write_text(textwrap.dedent("""\
        from agent_plugin import Plugin

        class WeatherPlugin(Plugin):
            name = "weather"
            version = "1.2.0"

            def on_load(self, context):
                self.context = context
    """))
    # Valid plugin 2
    (tmp_path / "translate_plugin.py").write_text(textwrap.dedent("""\
        from agent_plugin import Plugin

        class TranslatePlugin(Plugin):
            name = "translate"
    """))
    # Non-plugin python file (no Plugin subclass)
    (tmp_path / "utils.py").write_text("def helper(): return 42\n")
    # Private file (should be skipped)
    (tmp_path / "__init__.py").write_text("")
    return tmp_path


class TestPluginLoaderInit:
    def test_init_valid_dir(self, plugin_dir):
        loader = PluginLoader(str(plugin_dir))
        assert loader.plugin_dir == plugin_dir

    def test_init_missing_dir_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            PluginLoader(str(tmp_path / "does_not_exist"))

    def test_repr(self, plugin_dir):
        loader = PluginLoader(str(plugin_dir))
        assert "PluginLoader" in repr(loader)


class TestDiscover:
    def test_discover_finds_plugin_files(self, plugin_dir):
        loader = PluginLoader(str(plugin_dir))
        found = loader.discover()
        names = [Path(f).name for f in found]
        assert "weather_plugin.py" in names
        assert "translate_plugin.py" in names

    def test_discover_excludes_non_plugin_files(self, plugin_dir):
        loader = PluginLoader(str(plugin_dir))
        found = loader.discover()
        names = [Path(f).name for f in found]
        assert "utils.py" not in names

    def test_discover_excludes_private_files(self, plugin_dir):
        loader = PluginLoader(str(plugin_dir))
        found = loader.discover()
        names = [Path(f).name for f in found]
        assert "__init__.py" not in names

    def test_discover_empty_dir(self, tmp_path):
        loader = PluginLoader(str(tmp_path))
        assert loader.discover() == []

    def test_discover_returns_absolute_paths(self, plugin_dir):
        loader = PluginLoader(str(plugin_dir))
        found = loader.discover()
        for path in found:
            assert os.path.isabs(path)


class TestLoadFromFile:
    def test_load_from_file_returns_plugin(self, plugin_dir):
        loader = PluginLoader(str(plugin_dir))
        plugin = loader.load_from_file(str(plugin_dir / "weather_plugin.py"))
        from agent_plugin import Plugin
        assert isinstance(plugin, Plugin)

    def test_load_from_file_correct_name(self, plugin_dir):
        loader = PluginLoader(str(plugin_dir))
        plugin = loader.load_from_file(str(plugin_dir / "weather_plugin.py"))
        assert plugin.name == "weather"

    def test_load_from_file_correct_version(self, plugin_dir):
        loader = PluginLoader(str(plugin_dir))
        plugin = loader.load_from_file(str(plugin_dir / "weather_plugin.py"))
        assert plugin.version == "1.2.0"

    def test_load_from_file_missing_raises(self, plugin_dir):
        loader = PluginLoader(str(plugin_dir))
        with pytest.raises(FileNotFoundError):
            loader.load_from_file(str(plugin_dir / "ghost.py"))

    def test_load_from_file_no_plugin_class_raises(self, plugin_dir):
        loader = PluginLoader(str(plugin_dir))
        with pytest.raises(ValueError, match="No concrete Plugin subclass"):
            loader.load_from_file(str(plugin_dir / "utils.py"))

    def test_load_from_file_plugin_not_active(self, plugin_dir):
        """Loader returns uninitialised (not-yet-loaded) plugin."""
        loader = PluginLoader(str(plugin_dir))
        plugin = loader.load_from_file(str(plugin_dir / "weather_plugin.py"))
        assert plugin.is_active is False
