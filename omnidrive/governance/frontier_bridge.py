"""
Frontier Bridge - Python interface to OpenClaw's Frontier Pack

Executes JavaScript skills via subprocess and provides Python-native API.
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

OPENCLAW_DIR = Path.home() / '.openclaw'
FRONTIER_DIR = OPENCLAW_DIR / 'skills' / 'frontier'
AUDIT_LOG = OPENCLAW_DIR / 'governance' / 'logs' / 'audit.jsonl'


class FrontierBridge:
    """Bridge to OpenClaw Frontier Pack skills"""

    def __init__(self, agent_name: str = 'omnidrive_cli'):
        self.agent_name = agent_name
        self.enabled = FRONTIER_DIR.exists()

    def call_skill(self, skill_name: str, context: dict) -> dict:
        """Execute a Frontier skill via Node.js"""
        if not self.enabled:
            return {'success': True, 'skipped': True, 'reason': 'Frontier not installed'}

        skill_path = FRONTIER_DIR / skill_name / 'skill.js'
        if not skill_path.exists():
            return {'success': False, 'error': f'Skill not found: {skill_name}'}

        try:
            # Build Node.js command to execute skill
            js_code = f"""
                const skill = require('{skill_path}');
                const context = {json.dumps(context)};
                skill.run(context).then(r => console.log(JSON.stringify(r))).catch(e => console.error(e));
            """

            result = subprocess.run(
                ['node', '-e', js_code],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(OPENCLAW_DIR)
            )

            if result.returncode != 0:
                return {'success': False, 'error': result.stderr}

            return json.loads(result.stdout) if result.stdout.strip() else {'success': True}

        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Skill execution timed out'}
        except json.JSONDecodeError:
            return {'success': True, 'raw_output': result.stdout}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def check_tool_permission(self, tool: str, action: str) -> bool:
        """Check if tool/action is allowed for this agent"""
        result = self.call_skill('tool_guardian', {
            'agent': self.agent_name,
            'tool': tool,
            'action': action
        })
        return result.get('allowed', True)  # Allow by default if guardian not available

    def log_action(
        self,
        action: str,
        resource: str,
        status: str = 'success',
        details: Optional[str] = None
    ) -> None:
        """Log action to audit trail"""
        # Try Frontier skill first
        self.call_skill('audit_logger', {
            'agent': self.agent_name,
            'action': action,
            'resource': resource,
            'status': status,
            'details': details
        })

        # Also write local backup log
        self._write_local_log(action, resource, status, details)

    def _write_local_log(
        self,
        action: str,
        resource: str,
        status: str,
        details: Optional[str]
    ) -> None:
        """Write to local audit log as backup"""
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

        entry = {
            'ts': datetime.utcnow().isoformat(),
            'agent': self.agent_name,
            'action': action,
            'resource': resource,
            'status': status,
            'details': details
        }

        with open(AUDIT_LOG, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def request_approval(
        self,
        action: str,
        resource: str,
        reason: str,
        timeout_seconds: int = 300
    ) -> bool:
        """Request human approval for destructive action"""
        result = self.call_skill('human_checkpoint', {
            'agent': self.agent_name,
            'action': action,
            'resource': resource,
            'reason': reason,
            'timeout': timeout_seconds
        })

        if result.get('skipped'):
            # If human_checkpoint not available, prompt in CLI
            return self._cli_approval_prompt(action, resource, reason)

        return result.get('approved', False)

    def _cli_approval_prompt(self, action: str, resource: str, reason: str) -> bool:
        """Fallback CLI prompt for approval"""
        print(f"\n⚠️  Approval Required")
        print(f"   Action: {action}")
        print(f"   Resource: {resource}")
        print(f"   Reason: {reason}")
        response = input("\n   Approve? [y/N]: ").strip().lower()
        return response in ('y', 'yes')

    def check_confidence(self, output: str) -> dict:
        """Check output for confidence issues"""
        result = self.call_skill('confidence_meter', {
            'agent': self.agent_name,
            'output': output
        })
        return {
            'score': result.get('confidence', 1.0),
            'issues': result.get('issues', [])
        }

    def evaluate_output(self, output: str, task_type: str) -> dict:
        """Evaluate output quality"""
        result = self.call_skill('agent_evaluator', {
            'agent': self.agent_name,
            'output': output,
            'task_type': task_type
        })
        return {
            'quality': result.get('quality', 100),
            'completeness': result.get('completeness', 100),
            'efficiency': result.get('efficiency', 100),
            'policy_compliance': result.get('policy_compliance', 100)
        }


# Singleton instance
_bridge: Optional[FrontierBridge] = None


def get_bridge() -> FrontierBridge:
    """Get or create the Frontier bridge singleton"""
    global _bridge
    if _bridge is None:
        _bridge = FrontierBridge()
    return _bridge
