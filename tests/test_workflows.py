"""
Tests for memory and workflows.
"""
import pytest
import tempfile
import os
from omnidrive.memory.serena_client import MemoryManager
from omnidrive.workflows.graphs import (
    Workflow,
    WorkflowEngine,
    WorkflowStatus,
    create_smart_sync_workflow,
    create_backup_workflow
)


class TestMemoryManager:
    """Test memory management."""

    def test_write_and_read_memory(self):
        """Test writing and reading memories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(memory_dir=tmpdir)

            # Write memory
            result = manager.write_memory("test_key", {"data": "test_value"})
            assert result is True

            # Read memory
            value = manager.read_memory("test_key")
            assert value == {"data": "test_value"}

    def test_read_nonexistent_memory(self):
        """Test reading non-existent memory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(memory_dir=tmpdir)
            value = manager.read_memory("nonexistent")
            assert value is None

    def test_list_memories(self):
        """Test listing memories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(memory_dir=tmpdir)

            # Write multiple memories
            manager.write_memory("test1", {"data": "value1"})
            manager.write_memory("test2", {"data": "value2"})

            # List memories
            memories = manager.list_memories()
            assert len(memories) == 2

    def test_delete_memory(self):
        """Test deleting memory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(memory_dir=tmpdir)

            # Write memory
            manager.write_memory("to_delete", {"data": "value"})

            # Delete memory
            result = manager.delete_memory("to_delete")
            assert result is True

            # Verify deleted
            value = manager.read_memory("to_delete")
            assert value is None


class TestWorkflow:
    """Test workflow execution."""

    def test_workflow_creation(self):
        """Test creating a workflow."""
        workflow = Workflow(name="test", description="Test workflow")
        assert workflow.name == "test"
        assert workflow.description == "Test workflow"
        assert len(workflow.steps) == 0

    def test_workflow_add_steps(self):
        """Test adding steps to workflow."""
        workflow = Workflow(name="test")

        def step_1(context):
            context['step1'] = True

        def step_2(context):
            context['step2'] = True

        workflow.add_step(step_1).add_step(step_2)
        assert len(workflow.steps) == 2

    def test_workflow_execution(self):
        """Test workflow execution."""
        workflow = Workflow(name="test")

        def step_1(context):
            context['result'] = 'success'

        workflow.add_step(step_1)

        result = workflow.execute()
        assert result.status == WorkflowStatus.COMPLETED
        assert result.data == {'result': 'success'}

    def test_workflow_execution_failure(self):
        """Test workflow execution with failure."""
        workflow = Workflow(name="test")

        def failing_step(context):
            raise Exception("Step failed")

        workflow.add_step(failing_step)

        result = workflow.execute()
        assert result.status == WorkflowStatus.FAILED
        assert "Step failed" in result.message


class TestWorkflowEngine:
    """Test workflow engine."""

    def test_workflow_registration(self):
        """Test registering workflows."""
        engine = WorkflowEngine()
        workflow = Workflow(name="test", description="Test")

        engine.register_workflow(workflow)

        retrieved = engine.get_workflow("test")
        assert retrieved is not None
        assert retrieved.name == "test"

    def test_list_workflows(self):
        """Test listing workflows."""
        engine = WorkflowEngine()
        engine.register_workflow(Workflow(name="wf1", description="Workflow 1"))
        engine.register_workflow(Workflow(name="wf2", description="Workflow 2"))

        workflows = engine.list_workflows()
        assert len(workflows) == 2

    def test_execute_workflow(self):
        """Test executing workflow through engine."""
        engine = WorkflowEngine()

        workflow = Workflow(name="test", description="Test")

        def step(context):
            context['executed'] = True

        workflow.add_step(step)
        engine.register_workflow(workflow)

        result = engine.execute_workflow("test")
        assert result.status == WorkflowStatus.COMPLETED

    def test_execute_nonexistent_workflow(self):
        """Test executing non-existent workflow."""
        engine = WorkflowEngine()
        result = engine.execute_workflow("nonexistent")
        assert result.status == WorkflowStatus.FAILED


class TestPredefinedWorkflows:
    """Test predefined workflows."""

    def test_smart_sync_workflow(self):
        """Test smart sync workflow creation."""
        workflow = create_smart_sync_workflow()
        assert workflow.name == "smart-sync"
        assert len(workflow.steps) == 4

    def test_backup_workflow(self):
        """Test backup workflow creation."""
        workflow = create_backup_workflow()
        assert workflow.name == "backup-daily"
        assert len(workflow.steps) == 3
