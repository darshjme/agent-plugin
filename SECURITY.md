# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Yes     |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub Issues.**

Instead, send an email to **security@example.com** with:

- A description of the vulnerability.
- Steps to reproduce (minimal PoC is ideal).
- Potential impact assessment.
- Suggested fix if you have one.

You will receive an acknowledgement within **48 hours** and a full response within **7 business days**.

## Disclosure Policy

We follow [Responsible Disclosure](https://en.wikipedia.org/wiki/Responsible_disclosure):

1. Reporter submits the issue privately.
2. Maintainers confirm and work on a fix.
3. A patch release is published.
4. A public CVE and changelog entry are created.
5. Credit is given to the reporter (unless they prefer to remain anonymous).

## Security Considerations for Plugin Authors

`agent-plugin` uses `importlib` to dynamically load Python files. This means:

- **Only load plugins from trusted sources.** Arbitrary code execution is possible.
- Validate plugin files before loading them in production.
- Consider sandboxing (e.g. `RestrictedPython`, containers) for untrusted plugins.
- The `PluginLoader` performs a heuristic text scan, not a sandbox execution, during discovery.
