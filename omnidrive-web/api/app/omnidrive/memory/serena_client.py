"""
Persistent memory management using Serena MCP.
"""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class MemoryManager:
    """Manage persistent memory for OmniDrive CLI."""

    def __init__(self, memory_dir: str = None):
        """
        Initialize memory manager.

        Args:
            memory_dir: Directory to store memories (uses ~/.omnidrive/memory if None)
        """
        if memory_dir is None:
            memory_dir = os.path.expanduser("~/.omnidrive/memory")

        os.makedirs(memory_dir, exist_ok=True)
        self.memory_dir = memory_dir

    def write_memory(self, key: str, value: Any) -> bool:
        """
        Write a memory to persistent storage.

        Args:
            key: Memory key
            value: Value to store (must be JSON serializable)

        Returns:
            True if successful
        """
        try:
            memory_path = os.path.join(self.memory_dir, f"{key}.json")
            data = {
                'key': key,
                'value': value,
                'timestamp': datetime.now().isoformat()
            }

            with open(memory_path, 'w') as f:
                json.dump(data, f, indent=2)

            return True

        except Exception as e:
            print(f"Failed to write memory: {e}")
            return False

    def read_memory(self, key: str) -> Optional[Any]:
        """
        Read a memory from persistent storage.

        Args:
            key: Memory key

        Returns:
            Stored value or None if not found
        """
        try:
            memory_path = os.path.join(self.memory_dir, f"{key}.json")

            if not os.path.exists(memory_path):
                return None

            with open(memory_path, 'r') as f:
                data = json.load(f)

            return data.get('value')

        except Exception as e:
            print(f"Failed to read memory: {e}")
            return None

    def list_memories(self) -> List[Dict[str, Any]]:
        """
        List all stored memories.

        Returns:
            List of memory metadata
        """
        try:
            memories = []
            for filename in os.listdir(self.memory_dir):
                if filename.endswith('.json'):
                    memory_path = os.path.join(self.memory_dir, filename)
                    with open(memory_path, 'r') as f:
                        data = json.load(f)
                        memories.append({
                            'key': data.get('key'),
                            'timestamp': data.get('timestamp')
                        })

            return sorted(memories, key=lambda x: x['timestamp'], reverse=True)

        except Exception as e:
            print(f"Failed to list memories: {e}")
            return []

    def delete_memory(self, key: str) -> bool:
        """
        Delete a memory.

        Args:
            key: Memory key

        Returns:
            True if successful
        """
        try:
            memory_path = os.path.join(self.memory_dir, f"{key}.json")
            if os.path.exists(memory_path):
                os.remove(memory_path)
                return True
            return False

        except Exception as e:
            print(f"Failed to delete memory: {e}")
            return False


def get_memory_manager() -> MemoryManager:
    """
    Factory function to get memory manager.

    Returns:
        MemoryManager instance
    """
    return MemoryManager()
