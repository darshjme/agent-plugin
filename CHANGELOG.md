# Changelog

All notable changes to **agent-plugin** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Nothing yet — contributions welcome!

---

## [0.1.0] — 2026-03-24

### Added
- `Plugin` — abstract base class with lifecycle hooks (`on_load` / `on_unload`) and `is_active` property.
- `PluginRegistry` — register, load, unload, and introspect plugins by name.
- `HookSystem` — register before/after hooks for any named function point; wrap callables with auto-hooks.
- `PluginLoader` — discover and dynamically import `Plugin` subclasses from a directory via `importlib`.
- Full pytest test suite (22+ tests across all four components).
- `README.md` with quick-start and extension examples.
- `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`.

[Unreleased]: https://github.com/example/agent-plugin/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/example/agent-plugin/releases/tag/v0.1.0
