from fastapi.testclient import TestClient
from app.api.v2.skincare_gpt.context.context_manager import SkincareGPTContextManager

def test_context_manager_methods():
    """Test context manager methods"""
    manager = SkincareGPTContextManager(limit=3)
    manager.get_context("test-1")
    manager.get_context("test-2")
    manager.get_context("test-3")
    assert len(manager.pool) == 3
    assert len(manager.ordered_keys) == 3
    assert manager.ordered_keys == ["test-1", "test-2", "test-3"]
    
    manager.get_context("test-4")
    assert len(manager.pool) == 3
    assert len(manager.ordered_keys) == 3
    assert manager.ordered_keys == ["test-2", "test-3", "test-4"]

    context = manager.get_context("test-3")
    assert context.session_id == "test-3"

    manager.remove_from_pool(context)
    assert len(manager.pool) == 2
    assert len(manager.ordered_keys) == 2
    assert manager.ordered_keys == ["test-2", "test-4"]