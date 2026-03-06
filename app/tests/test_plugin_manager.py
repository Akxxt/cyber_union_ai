import pytest
from app.plugins.manager import PluginManager
from app.plugins.base import PluginMeta
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_manager_scan_load():
    manager = PluginManager()
    with patch.object(manager, '_load_plugin_from_module', AsyncMock()):
        await manager.scan_and_load()
        manager._load_plugin_from_module.assert_called()


@pytest.mark.asyncio
async def test_enable_disable():
    manager = PluginManager()
    mock_plugin = AsyncMock()
    mock_plugin.meta.plugin_id = "test"
    manager._plugins["test"] = mock_plugin
    await manager.enable_plugin("test")
    mock_plugin.enable.assert_awaited()
    await manager.disable_plugin("test")
    mock_plugin.disable.assert_awaited()