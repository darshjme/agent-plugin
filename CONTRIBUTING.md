# Contributing to agent-plugin

Thank you for considering a contribution! This guide will help you get started.

## Development Setup

```bash
git clone https://github.com/example/agent-plugin.git
cd agent-plugin
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
python -m pytest tests/ -v
```

All tests must pass before submitting a pull request.

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/).
- Type-annotate all public APIs.
- Write docstrings for every public class and function.
- Keep functions focused; prefer composition over inheritance.

## Pull Request Process

1. Fork the repo and create a branch: `git checkout -b feat/my-feature`.
2. Write tests for your change.
3. Ensure `pytest` passes locally.
4. Open a PR against `main` with a clear description of the change.
5. A maintainer will review within 48 hours.

## Commit Messages

Use the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
feat: add PluginGroup for batch operations
fix: handle missing name attribute gracefully
docs: update README with HookSystem example
```

## Reporting Bugs

Open a GitHub Issue with:
- Python version and OS.
- Minimal reproducible example.
- Expected vs. actual behaviour.

## Security Issues

Please **do not** open a public issue for security vulnerabilities. See [SECURITY.md](SECURITY.md) instead.

## Code of Conduct

All contributors must follow our [Code of Conduct](CODE_OF_CONDUCT.md).
