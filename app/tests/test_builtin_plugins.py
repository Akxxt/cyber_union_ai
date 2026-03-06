import pytest
import tempfile
from pathlib import Path
from app.plugins.builtin.file_operation_plugin import FileOperationPlugin
from app.plugins.builtin.http_request_plugin import HttpRequestPlugin
from app.plugins.builtin.data_calculate_plugin import DataCalculatePlugin
from app.plugins.builtin.db_query_plugin import DbQueryPlugin
from app.plugins.builtin.content_audit_plugin import ContentAuditPlugin
from app.plugins.base import PluginMeta


@pytest.mark.asyncio
async def test_file_plugin():
    meta = PluginMeta(plugin_id="file_test", name="file")
    plugin = FileOperationPlugin(meta)
    with tempfile.TemporaryDirectory() as tmpdir:
        plugin.work_dir = Path(tmpdir)
        result = await plugin.execute(action="write", path="test.txt", content="hello")
        assert result["success"] is True
        result = await plugin.execute(action="read", path="test.txt")
        assert result["data"] == "hello"
        result = await plugin.execute(action="list", path=".")
        assert "test.txt" in result["data"]


@pytest.mark.asyncio
async def test_calc_plugin():
    meta = PluginMeta(plugin_id="calc", name="calc")
    plugin = DataCalculatePlugin(meta)
    result = await plugin.execute(operation="calc", expression="1+2")
    assert result["result"] == 3
    result = await plugin.execute(operation="sum", numbers=[1,2,3])
    assert result["result"] == 6
    with pytest.raises(Exception):
        await plugin.execute(operation="calc", expression="__import__('os').system('ls')")


@pytest.mark.asyncio
async def test_http_plugin(monkeypatch):
    meta = PluginMeta(plugin_id="http", name="http")
    plugin = HttpRequestPlugin(meta)
    with pytest.raises(Exception) as exc:
        await plugin.execute(method="GET", url="http://evil.com")
    assert "不在白名单内" in str(exc.value)