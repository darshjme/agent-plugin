"""HookSystem — before/after hooks for any named function point."""

from __future__ import annotations

import functools
from collections import defaultdict
from typing import Any, Callable, List


class HookSystem:
    """Lightweight before/after hook dispatcher.

    Hooks are callables registered against a *hook_name* string.  Before-hooks
    run (in registration order) before the wrapped function; after-hooks run
    after it, receiving the function's return value as their first argument.

    Example::

        hooks = HookSystem()

        hooks.register_before("llm.call", lambda *a, **kw: print("about to call LLM"))
        hooks.register_after("llm.call", lambda result, *a, **kw: print("LLM returned:", result))

        @hooks.wrap("llm.call")
        def call_llm(prompt: str) -> str:
            return f"response to '{prompt}'"

        call_llm("Hello!")
        # prints: about to call LLM
        # prints: LLM returned: response to 'Hello!'
    """

    def __init__(self) -> None:
        self._before: dict[str, List[Callable]] = defaultdict(list)
        self._after: dict[str, List[Callable]] = defaultdict(list)

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_before(self, hook_name: str, func: Callable) -> None:
        """Register *func* as a before-hook for *hook_name*.

        The hook is called with the same positional and keyword arguments that
        will be passed to the main function.
        """
        if not callable(func):
            raise TypeError(f"before-hook must be callable, got {type(func).__name__!r}.")
        self._before[hook_name].append(func)

    def register_after(self, hook_name: str, func: Callable) -> None:
        """Register *func* as an after-hook for *hook_name*.

        The hook is called with ``(result, *args, **kwargs)`` where *result* is
        the return value of the wrapped function.
        """
        if not callable(func):
            raise TypeError(f"after-hook must be callable, got {type(func).__name__!r}.")
        self._after[hook_name].append(func)

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def trigger(self, hook_name: str, *args: Any, **kwargs: Any) -> tuple[tuple, dict]:
        """Fire all before-hooks for *hook_name* and return ``(args, kwargs)``.

        The returned tuple can be forwarded directly to the main function::

            args, kwargs = hooks.trigger("my.hook", x, y=z)
            result = my_function(*args, **kwargs)
        """
        for hook in self._before[hook_name]:
            hook(*args, **kwargs)
        return args, kwargs

    def trigger_after(self, hook_name: str, result: Any, *args: Any, **kwargs: Any) -> Any:
        """Fire all after-hooks for *hook_name* with the function's *result*.

        Returns *result* unchanged so callers can chain easily.
        """
        for hook in self._after[hook_name]:
            hook(result, *args, **kwargs)
        return result

    def wrap(self, hook_name: str, func: Callable) -> Callable:
        """Return a new callable that auto-triggers before/after hooks.

        The wrapped function is fully transparent: it accepts the same
        arguments and returns the same value as *func*.
        """
        @functools.wraps(func)
        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            args, kwargs = self.trigger(hook_name, *args, **kwargs)
            result = func(*args, **kwargs)
            self.trigger_after(hook_name, result, *args, **kwargs)
            return result

        return _wrapper

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def list_hooks(self) -> dict[str, dict[str, int]]:
        """Return a summary of registered hooks keyed by name."""
        all_names = set(self._before) | set(self._after)
        return {
            name: {
                "before": len(self._before.get(name, [])),
                "after": len(self._after.get(name, [])),
            }
            for name in sorted(all_names)
        }

    def clear(self, hook_name: str | None = None) -> None:
        """Remove all hooks for *hook_name*, or all hooks if ``None``."""
        if hook_name is None:
            self._before.clear()
            self._after.clear()
        else:
            self._before.pop(hook_name, None)
            self._after.pop(hook_name, None)

    def __repr__(self) -> str:
        total = len(set(self._before) | set(self._after))
        return f"<HookSystem hook_points={total}>"
