# LangChaingo API - Python SDK

The LangChaingo service exposes completions and RAG workflows directly from BosBase.

## Completions

```python
from bosbase import (
    LangChaingoCompletionRequest,
    LangChaingoCompletionMessage,
    LangChaingoModelConfig,
)

req = LangChaingoCompletionRequest(
    model=LangChaingoModelConfig(provider="openai", model="gpt-4o-mini"),
    messages=[
        LangChaingoCompletionMessage(role="system", content="You are a release bot."),
        LangChaingoCompletionMessage(role="user", content="Summarize the changelog."),
    ],
    temperature=0.2,
)

resp = pb.langchaingo.completions(req)
print(resp.content)
```

The response includes optional tool/function call metadata if the provider returns it.

## RAG

```python
from bosbase import (
    LangChaingoRAGRequest,
    LangChaingoModelConfig,
    LangChaingoRAGFilters,
)

req = LangChaingoRAGRequest(
    collection="kb_articles",
    question="How do I reset my password?",
    top_k=5,
    score_threshold=0.6,
    filters=LangChaingoRAGFilters(where={"category": "auth"}),
    return_sources=True,
)

resp = pb.langchaingo.rag(req)
print(resp.answer)
for src in resp.sources or []:
    print(src.content, src.score)
```

## Tips

1. Configure provider credentials under *Settings → LangChaingo* before calling the API.
2. Embed documents via the Vector or LLM Document APIs to make them searchable by LangChaingo.
3. Always log prompt/response metadata when automating customer-facing workflows for traceability.
