"""Tests for HookSystem."""

import pytest
from agent_plugin import HookSystem


class TestHookRegistration:
    def test_register_before(self):
        hs = HookSystem()
        hs.register_before("evt", lambda: None)
        assert hs.list_hooks()["evt"]["before"] == 1

    def test_register_after(self):
        hs = HookSystem()
        hs.register_after("evt", lambda r: None)
        assert hs.list_hooks()["evt"]["after"] == 1

    def test_register_non_callable_before_raises(self):
        hs = HookSystem()
        with pytest.raises(TypeError):
            hs.register_before("evt", "not-callable")  # type: ignore

    def test_register_non_callable_after_raises(self):
        hs = HookSystem()
        with pytest.raises(TypeError):
            hs.register_after("evt", 42)  # type: ignore

    def test_multiple_before_hooks(self):
        hs = HookSystem()
        hs.register_before("evt", lambda: None)
        hs.register_before("evt", lambda: None)
        assert hs.list_hooks()["evt"]["before"] == 2

    def test_multiple_after_hooks(self):
        hs = HookSystem()
        hs.register_after("evt", lambda r: None)
        hs.register_after("evt", lambda r: None)
        assert hs.list_hooks()["evt"]["after"] == 2


class TestTrigger:
    def test_trigger_fires_before_hooks(self):
        hs = HookSystem()
        calls = []
        hs.register_before("evt", lambda x: calls.append(x))
        hs.trigger("evt", "hello")
        assert calls == ["hello"]

    def test_trigger_returns_args_kwargs(self):
        hs = HookSystem()
        args, kwargs = hs.trigger("evt", 1, 2, key="val")
        assert args == (1, 2)
        assert kwargs == {"key": "val"}

    def test_trigger_no_hooks_is_noop(self):
        hs = HookSystem()
        args, kwargs = hs.trigger("unknown", 99)
        assert args == (99,)

    def test_trigger_order(self):
        hs = HookSystem()
        order = []
        hs.register_before("evt", lambda: order.append(1))
        hs.register_before("evt", lambda: order.append(2))
        hs.trigger("evt")
        assert order == [1, 2]

    def test_trigger_after_fires_after_hooks(self):
        hs = HookSystem()
        captured = []
        hs.register_after("evt", lambda result: captured.append(result))
        hs.trigger_after("evt", "my-result")
        assert captured == ["my-result"]

    def test_trigger_after_returns_result(self):
        hs = HookSystem()
        ret = hs.trigger_after("evt", 42)
        assert ret == 42


class TestWrap:
    def test_wrap_returns_callable(self):
        hs = HookSystem()
        wrapped = hs.wrap("fn", lambda x: x * 2)
        assert callable(wrapped)

    def test_wrap_preserves_return_value(self):
        hs = HookSystem()
        wrapped = hs.wrap("fn", lambda x: x + 1)
        assert wrapped(5) == 6

    def test_wrap_fires_before_hooks(self):
        hs = HookSystem()
        calls = []
        hs.register_before("fn", lambda x: calls.append(("before", x)))
        wrapped = hs.wrap("fn", lambda x: x)
        wrapped("arg")
        assert ("before", "arg") in calls

    def test_wrap_fires_after_hooks(self):
        hs = HookSystem()
        calls = []
        hs.register_after("fn", lambda result, x: calls.append(("after", result)))
        wrapped = hs.wrap("fn", lambda x: x.upper())
        wrapped("hello")
        assert ("after", "HELLO") in calls

    def test_wrap_preserves_name(self):
        hs = HookSystem()
        def my_func(x): return x
        wrapped = hs.wrap("fn", my_func)
        assert wrapped.__name__ == "my_func"

    def test_wrap_keyword_args(self):
        hs = HookSystem()
        wrapped = hs.wrap("fn", lambda a, b=10: a + b)
        assert wrapped(5, b=3) == 8


class TestClearAndInspect:
    def test_clear_specific_hook(self):
        hs = HookSystem()
        hs.register_before("evt", lambda: None)
        hs.clear("evt")
        assert "evt" not in hs.list_hooks()

    def test_clear_all_hooks(self):
        hs = HookSystem()
        hs.register_before("a", lambda: None)
        hs.register_after("b", lambda r: None)
        hs.clear()
        assert hs.list_hooks() == {}

    def test_repr(self):
        hs = HookSystem()
        hs.register_before("a", lambda: None)
        assert "hook_points=1" in repr(hs)
