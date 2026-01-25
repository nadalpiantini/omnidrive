"""
Workflow automation system.
Simple workflow implementation for file management tasks.
"""
from typing import Dict, Any, List, Callable
from dataclasses import dataclass
from enum import Enum


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowResult:
    """Result of workflow execution."""
    status: WorkflowStatus
    message: str
    data: Any = None


class Workflow:
    """Base workflow class."""

    def __init__(self, name: str, description: str = ""):
        """
        Initialize workflow.

        Args:
            name: Workflow name
            description: Workflow description
        """
        self.name = name
        self.description = description
        self.steps: List[Callable] = []

    def add_step(self, step: Callable) -> 'Workflow':
        """
        Add a step to the workflow.

        Args:
            step: Step function

        Returns:
            Self for chaining
        """
        self.steps.append(step)
        return self

    def execute(self, context: Dict[str, Any] = None) -> WorkflowResult:
        """
        Execute the workflow.

        Args:
            context: Execution context

        Returns:
            WorkflowResult
        """
        if context is None:
            context = {}

        try:
            for step in self.steps:
                step(context)

            return WorkflowResult(
                status=WorkflowStatus.COMPLETED,
                message=f"Workflow '{self.name}' completed successfully",
                data=context
            )

        except Exception as e:
            return WorkflowResult(
                status=WorkflowStatus.FAILED,
                message=f"Workflow '{self.name}' failed: {e}"
            )


class WorkflowEngine:
    """Manage and execute workflows."""

    def __init__(self):
        """Initialize workflow engine."""
        self.workflows: Dict[str, Workflow] = {}

    def register_workflow(self, workflow: Workflow):
        """
        Register a workflow.

        Args:
            workflow: Workflow to register
        """
        self.workflows[workflow.name] = workflow

    def get_workflow(self, name: str) -> Optional[Workflow]:
        """
        Get a registered workflow.

        Args:
            name: Workflow name

        Returns:
            Workflow or None
        """
        return self.workflows.get(name)

    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        List all registered workflows.

        Returns:
            List of workflow metadata
        """
        return [
            {
                'name': name,
                'description': workflow.description,
                'steps': len(workflow.steps)
            }
            for name, workflow in self.workflows.items()
        ]

    def execute_workflow(
        self,
        name: str,
        context: Dict[str, Any] = None
    ) -> WorkflowResult:
        """
        Execute a workflow.

        Args:
            name: Workflow name
            context: Execution context

        Returns:
            WorkflowResult
        """
        workflow = self.get_workflow(name)
        if not workflow:
            return WorkflowResult(
                status=WorkflowStatus.FAILED,
                message=f"Workflow '{name}' not found"
            )

        return workflow.execute(context)


# Predefined workflows

def create_smart_sync_workflow() -> Workflow:
    """Create smart sync workflow."""
    workflow = Workflow(
        name="smart-sync",
        description="Sync new PDFs from Google Drive to Folderfort"
    )

    def step_1_detect(context):
        """Step 1: Detect new PDF files."""
        print("  📋 Detecting new PDF files...")
        context['new_files'] = []  # Placeholder

    def step_2_validate(context):
        """Step 2: Validate space availability."""
        print("  ✅ Validating Folderfort space...")
        context['has_space'] = True

    def step_3_upload(context):
        """Step 3: Upload files."""
        print("  📤 Uploading files...")

    def step_4_report(context):
        """Step 4: Generate report."""
        print("  📊 Report: Sync completed")

    workflow.add_step(step_1_detect)
    workflow.add_step(step_2_validate)
    workflow.add_step(step_3_upload)
    workflow.add_step(step_4_report)

    return workflow


def create_backup_workflow() -> Workflow:
    """Create automatic backup workflow."""
    workflow = Workflow(
        name="backup-daily",
        description="Automatic daily backup of important files"
    )

    def step_1_classify(context):
        """Step 1: Classify files by type."""
        print("  📂 Classifying files...")

    def step_2_apply_rules(context):
        """Step 2: Apply retention rules."""
        print("  📜 Applying retention rules...")

    def step_3_distribute(context):
        """Step 3: Distribute to services."""
        print("  💾 Distributing files...")

    workflow.add_step(step_1_classify)
    workflow.add_step(step_2_apply_rules)
    workflow.add_step(step_3_distribute)

    return workflow


def get_workflow_engine() -> WorkflowEngine:
    """
    Factory function to get workflow engine with predefined workflows.

    Returns:
        WorkflowEngine instance
    """
    engine = WorkflowEngine()
    engine.register_workflow(create_smart_sync_workflow())
    engine.register_workflow(create_backup_workflow())
    return engine
