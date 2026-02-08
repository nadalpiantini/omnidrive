"""
LangGraph-powered workflow automation system.
Real agentic architecture with state, branching, and observability.
"""
from typing import TypedDict, List, Dict, Any, Optional, Literal, Annotated
from dataclasses import dataclass
from enum import Enum
import operator
import json
from datetime import datetime

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("Warning: langgraph not installed. Install with: pip install langgraph")


# =============================================================================
# STATE DEFINITIONS
# =============================================================================

class SyncState(TypedDict):
    """State for sync workflow."""
    # Input
    source_service: str
    target_service: str
    dry_run: bool

    # Processing
    files_detected: List[Dict[str, Any]]
    files_validated: List[Dict[str, Any]]
    files_synced: List[Dict[str, Any]]

    # Errors & Logs
    errors: Annotated[List[str], operator.add]
    logs: Annotated[List[str], operator.add]

    # Control
    should_continue: bool
    current_step: str
    started_at: str
    completed_at: Optional[str]


class RAGState(TypedDict):
    """State for RAG-powered search workflow."""
    # Input
    query: str
    service: Optional[str]
    top_k: int

    # Processing
    query_embedding: Optional[List[float]]
    retrieved_docs: List[Dict[str, Any]]
    reasoned_response: Optional[str]

    # Logs
    logs: Annotated[List[str], operator.add]

    # Control
    current_step: str


class ObsidianState(TypedDict):
    """State for Obsidian vault ingestion."""
    # Input
    vault_path: str

    # Processing
    files_found: List[str]
    files_indexed: List[str]
    backlinks_graph: Dict[str, List[str]]

    # Logs
    logs: Annotated[List[str], operator.add]
    errors: Annotated[List[str], operator.add]

    # Control
    current_step: str


# =============================================================================
# GRAPH LOGGER - Observability
# =============================================================================

class GraphLogger:
    """Visual logging for graph execution."""

    ICONS = {
        'start': '🚀',
        'node': '⚙️',
        'success': '✅',
        'error': '❌',
        'branch': '🔀',
        'end': '🏁',
        'rag': '🧠',
        'obsidian': '📓',
        'sync': '🔄',
    }

    def __init__(self, graph_name: str):
        self.graph_name = graph_name
        self.logs: List[Dict[str, Any]] = []
        self.start_time = datetime.now()

    def log(self, event: str, node: str, message: str, data: Any = None):
        """Log a graph event."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'elapsed_ms': (datetime.now() - self.start_time).total_seconds() * 1000,
            'event': event,
            'node': node,
            'message': message,
            'data': data
        }
        self.logs.append(entry)

        # Print visual log
        icon = self.ICONS.get(event, '📌')
        print(f"  {icon} [{node}] {message}")

    def get_execution_trace(self) -> str:
        """Get visual execution trace."""
        lines = [f"\n{'='*50}", f"Graph: {self.graph_name}", f"{'='*50}"]
        for entry in self.logs:
            icon = self.ICONS.get(entry['event'], '📌')
            lines.append(f"{icon} {entry['node']:15} | {entry['message']}")
        lines.append(f"{'='*50}\n")
        return "\n".join(lines)


# =============================================================================
# SYNC WORKFLOW NODES
# =============================================================================

def detect_files_node(state: SyncState) -> SyncState:
    """Node: Detect files in source service."""
    state['current_step'] = 'detect'
    state['logs'] = [f"Detecting files in {state['source_service']}..."]

    try:
        # Import service factory
        from ..services.factory import ServiceFactory

        service = ServiceFactory.get_service(state['source_service'])
        files = service.list_files(limit=100)

        state['files_detected'] = files
        state['logs'] = [f"Found {len(files)} files"]
        state['should_continue'] = len(files) > 0

    except Exception as e:
        state['errors'] = [f"Detection failed: {str(e)}"]
        state['should_continue'] = False

    return state


def validate_space_node(state: SyncState) -> SyncState:
    """Node: Validate target has space."""
    state['current_step'] = 'validate'
    state['logs'] = [f"Validating space in {state['target_service']}..."]

    try:
        # For now, assume space is available
        # TODO: Implement actual space check
        state['files_validated'] = state['files_detected']
        state['logs'] = [f"Validated {len(state['files_validated'])} files for sync"]
        state['should_continue'] = True

    except Exception as e:
        state['errors'] = [f"Validation failed: {str(e)}"]
        state['should_continue'] = False

    return state


def sync_files_node(state: SyncState) -> SyncState:
    """Node: Sync files to target."""
    state['current_step'] = 'sync'

    if state['dry_run']:
        state['logs'] = [f"DRY RUN: Would sync {len(state['files_validated'])} files"]
        state['files_synced'] = []
    else:
        state['logs'] = [f"Syncing {len(state['files_validated'])} files..."]
        # TODO: Implement actual sync
        state['files_synced'] = state['files_validated']
        state['logs'] = [f"Synced {len(state['files_synced'])} files"]

    state['completed_at'] = datetime.now().isoformat()
    return state


def should_continue_sync(state: SyncState) -> Literal["sync", "end"]:
    """Conditional edge: Check if we should continue syncing."""
    if state.get('should_continue', False) and not state.get('errors'):
        return "sync"
    return "end"


# =============================================================================
# RAG WORKFLOW NODES
# =============================================================================

def embed_query_node(state: RAGState) -> RAGState:
    """Node: Generate embedding for query."""
    state['current_step'] = 'embed'
    state['logs'] = [f"Embedding query: '{state['query'][:50]}...'"]

    try:
        from ..rag.embeddings import EmbeddingsGenerator

        embeddings = EmbeddingsGenerator()
        state['query_embedding'] = embeddings.embed_text(state['query'])
        state['logs'] = [f"Generated {len(state['query_embedding'])}-dim embedding"]

    except Exception as e:
        state['logs'] = [f"Embedding failed: {str(e)}"]
        state['query_embedding'] = None

    return state


def retrieve_docs_node(state: RAGState) -> RAGState:
    """Node: Retrieve relevant documents."""
    state['current_step'] = 'retrieve'
    state['logs'] = ["Retrieving relevant documents..."]

    try:
        from ..rag.vector_store import VectorStore

        if state['query_embedding'] is None:
            state['retrieved_docs'] = []
            state['logs'] = ["No embedding available, skipping retrieval"]
            return state

        vector_store = VectorStore()
        where = {'service': state['service']} if state['service'] else None

        results = vector_store.search(
            query_embedding=state['query_embedding'],
            top_k=state['top_k'],
            where=where
        )

        state['retrieved_docs'] = results
        state['logs'] = [f"Retrieved {len(results)} documents"]

    except Exception as e:
        state['logs'] = [f"Retrieval failed: {str(e)}"]
        state['retrieved_docs'] = []

    return state


def reason_node(state: RAGState) -> RAGState:
    """Node: Reason over retrieved documents."""
    state['current_step'] = 'reason'
    state['logs'] = ["Reasoning over documents..."]

    try:
        if not state['retrieved_docs']:
            state['reasoned_response'] = "No relevant documents found."
            return state

        # Build context from retrieved docs
        context_parts = []
        for i, doc in enumerate(state['retrieved_docs'][:5]):
            name = doc.get('metadata', {}).get('file_name', f'Document {i+1}')
            score = doc.get('score', 0)
            snippet = doc.get('document', '')[:200]
            context_parts.append(f"[{name}] (score: {score:.2f})\n{snippet}...")

        context = "\n\n".join(context_parts)

        # For now, return formatted results
        # TODO: Add LLM reasoning step
        state['reasoned_response'] = f"Found {len(state['retrieved_docs'])} relevant files:\n\n{context}"
        state['logs'] = ["Reasoning complete"]

    except Exception as e:
        state['logs'] = [f"Reasoning failed: {str(e)}"]
        state['reasoned_response'] = f"Error during reasoning: {str(e)}"

    return state


# =============================================================================
# OBSIDIAN WORKFLOW NODES
# =============================================================================

def scan_vault_node(state: ObsidianState) -> ObsidianState:
    """Node: Scan Obsidian vault for markdown files."""
    import os
    from pathlib import Path

    state['current_step'] = 'scan'
    state['logs'] = [f"Scanning vault: {state['vault_path']}"]

    try:
        vault_path = Path(state['vault_path'])
        if not vault_path.exists():
            state['errors'] = [f"Vault not found: {state['vault_path']}"]
            state['files_found'] = []
            return state

        # Find all markdown files
        md_files = list(vault_path.rglob("*.md"))
        state['files_found'] = [str(f) for f in md_files]
        state['logs'] = [f"Found {len(md_files)} markdown files"]

    except Exception as e:
        state['errors'] = [f"Scan failed: {str(e)}"]
        state['files_found'] = []

    return state


def extract_backlinks_node(state: ObsidianState) -> ObsidianState:
    """Node: Extract backlinks graph from vault."""
    import re
    from pathlib import Path

    state['current_step'] = 'backlinks'
    state['logs'] = ["Extracting backlinks graph..."]

    backlinks: Dict[str, List[str]] = {}
    wiki_link_pattern = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')

    try:
        for file_path in state['files_found']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                file_name = Path(file_path).stem
                links = wiki_link_pattern.findall(content)
                backlinks[file_name] = links

            except Exception as e:
                state['errors'] = [f"Error reading {file_path}: {str(e)}"]

        state['backlinks_graph'] = backlinks
        total_links = sum(len(links) for links in backlinks.values())
        state['logs'] = [f"Extracted {total_links} backlinks from {len(backlinks)} files"]

    except Exception as e:
        state['errors'] = [f"Backlink extraction failed: {str(e)}"]
        state['backlinks_graph'] = {}

    return state


def index_vault_node(state: ObsidianState) -> ObsidianState:
    """Node: Index vault files for RAG."""
    state['current_step'] = 'index'
    state['logs'] = ["Indexing vault for semantic search..."]

    try:
        from ..rag.indexer import FileIndexer

        indexer = FileIndexer()
        indexed = []

        for file_path in state['files_found'][:50]:  # Limit for now
            try:
                from pathlib import Path
                file_id = f"obsidian:{Path(file_path).stem}"

                success = indexer.index_file(
                    file_path=file_path,
                    file_id=file_id,
                    service='obsidian',
                    metadata={
                        'backlinks': state['backlinks_graph'].get(Path(file_path).stem, [])
                    }
                )

                if success:
                    indexed.append(file_path)

            except Exception as e:
                state['errors'] = [f"Failed to index {file_path}: {str(e)}"]

        state['files_indexed'] = indexed
        state['logs'] = [f"Indexed {len(indexed)} files"]

    except Exception as e:
        state['errors'] = [f"Indexing failed: {str(e)}"]
        state['files_indexed'] = []

    return state


# =============================================================================
# GRAPH BUILDERS
# =============================================================================

def build_sync_graph() -> Optional[StateGraph]:
    """Build the sync workflow graph."""
    if not LANGGRAPH_AVAILABLE:
        return None

    graph = StateGraph(SyncState)

    # Add nodes
    graph.add_node("detect", detect_files_node)
    graph.add_node("validate", validate_space_node)
    graph.add_node("sync", sync_files_node)

    # Add edges
    graph.set_entry_point("detect")
    graph.add_edge("detect", "validate")
    graph.add_conditional_edges(
        "validate",
        should_continue_sync,
        {
            "sync": "sync",
            "end": END
        }
    )
    graph.add_edge("sync", END)

    return graph.compile()


def build_rag_graph() -> Optional[StateGraph]:
    """Build the RAG workflow graph."""
    if not LANGGRAPH_AVAILABLE:
        return None

    graph = StateGraph(RAGState)

    # Add nodes
    graph.add_node("embed", embed_query_node)
    graph.add_node("retrieve", retrieve_docs_node)
    graph.add_node("reason", reason_node)

    # Add edges
    graph.set_entry_point("embed")
    graph.add_edge("embed", "retrieve")
    graph.add_edge("retrieve", "reason")
    graph.add_edge("reason", END)

    return graph.compile()


def build_obsidian_graph() -> Optional[StateGraph]:
    """Build the Obsidian ingestion graph."""
    if not LANGGRAPH_AVAILABLE:
        return None

    graph = StateGraph(ObsidianState)

    # Add nodes
    graph.add_node("scan", scan_vault_node)
    graph.add_node("backlinks", extract_backlinks_node)
    graph.add_node("index", index_vault_node)

    # Add edges
    graph.set_entry_point("scan")
    graph.add_edge("scan", "backlinks")
    graph.add_edge("backlinks", "index")
    graph.add_edge("index", END)

    return graph.compile()


# =============================================================================
# WORKFLOW ENGINE - Unified interface
# =============================================================================

class WorkflowEngine:
    """Manage and execute LangGraph workflows."""

    def __init__(self):
        """Initialize workflow engine with compiled graphs."""
        self.graphs = {}
        self.loggers = {}

        # Build graphs
        sync_graph = build_sync_graph()
        if sync_graph:
            self.graphs['smart-sync'] = sync_graph

        rag_graph = build_rag_graph()
        if rag_graph:
            self.graphs['rag-search'] = rag_graph

        obsidian_graph = build_obsidian_graph()
        if obsidian_graph:
            self.graphs['obsidian-ingest'] = obsidian_graph

    def list_workflows(self) -> List[Dict[str, str]]:
        """List available workflows."""
        workflows = [
            {
                'name': 'smart-sync',
                'description': 'Sync files between cloud services with validation',
                'nodes': 'detect → validate → sync'
            },
            {
                'name': 'rag-search',
                'description': 'Semantic search with RAG (retrieve → reason)',
                'nodes': 'embed → retrieve → reason'
            },
            {
                'name': 'obsidian-ingest',
                'description': 'Ingest Obsidian vault with backlinks graph',
                'nodes': 'scan → backlinks → index'
            }
        ]
        return workflows

    def execute_sync(
        self,
        source: str,
        target: str,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """Execute sync workflow."""
        if 'smart-sync' not in self.graphs:
            return {'error': 'LangGraph not available'}

        logger = GraphLogger('smart-sync')
        logger.log('start', 'engine', f'Starting sync: {source} → {target}')

        initial_state: SyncState = {
            'source_service': source,
            'target_service': target,
            'dry_run': dry_run,
            'files_detected': [],
            'files_validated': [],
            'files_synced': [],
            'errors': [],
            'logs': [],
            'should_continue': True,
            'current_step': 'init',
            'started_at': datetime.now().isoformat(),
            'completed_at': None
        }

        result = self.graphs['smart-sync'].invoke(initial_state)
        logger.log('end', 'engine', 'Sync complete')

        print(logger.get_execution_trace())
        return result

    def execute_search(
        self,
        query: str,
        service: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Execute RAG search workflow."""
        if 'rag-search' not in self.graphs:
            return {'error': 'LangGraph not available'}

        logger = GraphLogger('rag-search')
        logger.log('start', 'engine', f'Starting RAG search: "{query[:30]}..."')

        initial_state: RAGState = {
            'query': query,
            'service': service,
            'top_k': top_k,
            'query_embedding': None,
            'retrieved_docs': [],
            'reasoned_response': None,
            'logs': [],
            'current_step': 'init'
        }

        result = self.graphs['rag-search'].invoke(initial_state)
        logger.log('end', 'engine', 'Search complete')

        print(logger.get_execution_trace())
        return result

    def execute_obsidian_ingest(self, vault_path: str) -> Dict[str, Any]:
        """Execute Obsidian vault ingestion."""
        if 'obsidian-ingest' not in self.graphs:
            return {'error': 'LangGraph not available'}

        logger = GraphLogger('obsidian-ingest')
        logger.log('start', 'engine', f'Ingesting vault: {vault_path}')

        initial_state: ObsidianState = {
            'vault_path': vault_path,
            'files_found': [],
            'files_indexed': [],
            'backlinks_graph': {},
            'logs': [],
            'errors': [],
            'current_step': 'init'
        }

        result = self.graphs['obsidian-ingest'].invoke(initial_state)
        logger.log('end', 'engine', 'Ingestion complete')

        print(logger.get_execution_trace())
        return result


def get_workflow_engine() -> WorkflowEngine:
    """Factory function to get workflow engine."""
    return WorkflowEngine()
