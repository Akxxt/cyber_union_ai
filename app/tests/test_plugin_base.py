import pytest
from app.plugins.base import BasePlugin, PluginMeta, PluginExecutionException


class DummyPlugin(BasePlugin):
    META = {"plugin_id": "test", "name": "Test"}
    async def on_load(self): pass
    async def on_unload(self): pass
    async def on_enable(self): pass
    async def on_disable(self): pass
    async def execute(self, **kwargs): return "ok"


def test_plugin_meta():
    meta = PluginMeta(plugin_id="test", name="test")
    assert meta.plugin_id == "test"
    assert meta.permission_level == 1


@pytest.mark.asyncio
async def test_plugin_lifecycle():
    meta = PluginMeta(plugin_id="test", name="test")
    plugin = DummyPlugin(meta)
    assert not plugin.is_loaded
    await plugin.load()
    assert plugin.is_loaded
    await plugin.enable()
    assert plugin.is_enabled
    result = await plugin.execute()
    assert result == "ok"
    await plugin.disable()
    assert not plugin.is_enabled
    await plugin.unload()
    assert not plugin.is_loaded