"""
Governance Decorators

Python decorators for integrating Frontier Pack governance with OmniDrive CLI.
"""

import functools
from typing import Callable, Any, Optional, List
from .frontier_bridge import get_bridge


def audit_log(action: Optional[str] = None, resource_arg: Optional[str] = None):
    """
    Decorator to log function calls to the audit trail.

    Args:
        action: Override action name (defaults to function name)
        resource_arg: Name of argument to use as resource identifier

    Example:
        @audit_log(action='file_upload', resource_arg='file_path')
        def upload_file(file_path: str, service: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bridge = get_bridge()

            # Determine action name
            action_name = action or func.__name__

            # Determine resource from args
            resource = 'unknown'
            if resource_arg:
                # Try to get from kwargs first
                if resource_arg in kwargs:
                    resource = str(kwargs[resource_arg])
                else:
                    # Try to get from positional args
                    try:
                        arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
                        if resource_arg in arg_names:
                            idx = arg_names.index(resource_arg)
                            if idx < len(args):
                                resource = str(args[idx])
                    except Exception:
                        pass

            try:
                result = func(*args, **kwargs)
                bridge.log_action(action_name, resource, 'success')
                return result
            except Exception as e:
                bridge.log_action(action_name, resource, 'failure', str(e))
                raise

        return wrapper
    return decorator


def require_approval(
    reason: str,
    action: Optional[str] = None,
    resource_arg: Optional[str] = None,
    timeout: int = 300
):
    """
    Decorator to require human approval before executing.

    Args:
        reason: Why approval is needed
        action: Override action name (defaults to function name)
        resource_arg: Name of argument to use as resource identifier
        timeout: Approval timeout in seconds

    Example:
        @require_approval(
            reason='Permanently deletes file',
            action='file_delete',
            resource_arg='file_id'
        )
        def delete_file(file_id: str, permanent: bool = False):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bridge = get_bridge()

            action_name = action or func.__name__

            # Determine resource
            resource = 'unknown'
            if resource_arg and resource_arg in kwargs:
                resource = str(kwargs[resource_arg])

            # Request approval
            approved = bridge.request_approval(
                action_name,
                resource,
                reason,
                timeout
            )

            if not approved:
                bridge.log_action(action_name, resource, 'blocked', 'Approval denied')
                raise PermissionError(f"Action '{action_name}' was not approved")

            # Log approval and execute
            bridge.log_action(action_name, resource, 'approved')
            return func(*args, **kwargs)

        return wrapper
    return decorator


def check_confidence(threshold: float = 0.7, fail_on_low: bool = False):
    """
    Decorator to check output confidence and flag potential issues.

    Args:
        threshold: Minimum confidence score (0-1)
        fail_on_low: Whether to raise exception on low confidence

    Example:
        @check_confidence(threshold=0.8)
        def generate_summary(content: str) -> str:
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Only check string outputs
            if isinstance(result, str):
                bridge = get_bridge()
                confidence = bridge.check_confidence(result)

                if confidence['score'] < threshold:
                    if confidence['issues']:
                        print(f"⚠️  Low confidence ({confidence['score']:.0%}): {', '.join(confidence['issues'])}")

                    if fail_on_low:
                        raise ValueError(f"Output confidence {confidence['score']:.0%} below threshold {threshold:.0%}")

            return result

        return wrapper
    return decorator


def check_permission(tool: str, action: str):
    """
    Decorator to check tool permission before executing.

    Args:
        tool: Tool/service name
        action: Action being performed

    Example:
        @check_permission(tool='google_drive', action='write')
        def upload_to_google(file_path: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bridge = get_bridge()

            if not bridge.check_tool_permission(tool, action):
                bridge.log_action(
                    func.__name__,
                    f"{tool}:{action}",
                    'blocked',
                    'Tool permission denied'
                )
                raise PermissionError(f"Permission denied for {tool}:{action}")

            return func(*args, **kwargs)

        return wrapper
    return decorator
