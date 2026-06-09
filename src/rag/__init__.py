from .build_kb import build_knowledge_base

__all__ = ["build_knowledge_base", "SlangRetriever"]


def __getattr__(name: str):
    if name == "SlangRetriever":
        from .retriever import SlangRetriever
        return SlangRetriever
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
