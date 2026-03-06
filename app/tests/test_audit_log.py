import pytest
from app.audit.audit_full_link import audit_manager


@pytest.mark.asyncio
async def test_audit_log_write_and_read():
    task_id = "audit_test"
    await audit_manager.log_operation(task_id, "tester", "create", {"input": "test"})
    await audit_manager.log_execution(task_id, "node1", "agent1", "success", {"output": "ok"})
    await audit_manager.log_compliance(task_id, "rule1", "content", "high", "blocked")

    logs = await audit_manager.get_task_logs(task_id)
    assert len(logs) == 3
    types = [log["type"] for log in logs]
    assert "operation" in types
    assert "execution" in types
    assert "compliance" in types