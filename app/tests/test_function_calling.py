import pytest
from app.llm.function_calling import FunctionManager


def test_register_and_execute():
    fm = FunctionManager()

    def add(a: int, b: int) -> int:
        return a + b

    fm.register(add, name="add", description="加法")
    defs = fm.get_definitions()
    assert len(defs) == 1
    assert defs[0]["name"] == "add"

    call = fm.parse_call('{"name":"add","arguments":{"a":1,"b":2}}')
    assert call is not None
    result = fm.execute(call)
    assert result.result == 3