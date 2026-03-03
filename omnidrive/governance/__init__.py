"""
OmniDrive Governance Module

Integrates with OpenClaw's Frontier Pack for enterprise governance:
- tool_guardian: Access control for operations
- audit_logger: Immutable action logging
- human_checkpoint: Approval queue for destructive actions
- confidence_meter: Error detection and hallucination prevention
- agent_evaluator: Output quality scoring
"""

from .decorators import audit_log, require_approval, check_confidence
from .frontier_bridge import FrontierBridge

__all__ = [
    'audit_log',
    'require_approval',
    'check_confidence',
    'FrontierBridge',
]
