"""BosBase Python SDK public API."""

from .auth import AuthStore
from .client import BosBase
from .exceptions import ClientResponseError
from .types import (
    LangChaingoCompletionMessage,
    LangChaingoCompletionRequest,
    LangChaingoCompletionResponse,
    LangChaingoModelConfig,
    LangChaingoRAGFilters,
    LangChaingoRAGRequest,
    LangChaingoRAGResponse,
    LangChaingoSourceDocument,
    LangChaingoToolCall,
    LLMDocument,
    LLMDocumentUpdate,
    LLMQueryOptions,
    LLMQueryResult,
    VectorBatchInsertOptions,
    VectorBatchInsertResponse,
    VectorCollectionConfig,
    VectorCollectionInfo,
    VectorDocument,
    VectorInsertResponse,
    VectorSearchOptions,
    VectorSearchResponse,
    VectorSearchResult,
)

__all__ = [
    "AuthStore",
    "BosBase",
    "ClientResponseError",
    # vector helpers
    "VectorDocument",
    "VectorSearchOptions",
    "VectorSearchResponse",
    "VectorSearchResult",
    "VectorInsertResponse",
    "VectorBatchInsertOptions",
    "VectorBatchInsertResponse",
    "VectorCollectionConfig",
    "VectorCollectionInfo",
    # LangChaingo helpers
    "LangChaingoModelConfig",
    "LangChaingoCompletionMessage",
    "LangChaingoCompletionRequest",
    "LangChaingoCompletionResponse",
    "LangChaingoToolCall",
    "LangChaingoRAGFilters",
    "LangChaingoRAGRequest",
    "LangChaingoRAGResponse",
    "LangChaingoSourceDocument",
    # LLM helpers
    "LLMDocument",
    "LLMDocumentUpdate",
    "LLMQueryOptions",
    "LLMQueryResult",
]
