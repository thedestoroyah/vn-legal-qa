"""Tầng gọi API: client HTTP bất đồng bộ và schema phản hồi."""
from src.ui.web.api.client import ApiClientError, LegalQAApiClient, parse_chunk_id
from src.ui.web.api.schemas import ArticleResponse, AskResponse, CitationItem, HealthResponse, TraceStep

__all__ = ["ApiClientError", "LegalQAApiClient", "parse_chunk_id", "ArticleResponse", "AskResponse",
           "CitationItem", "HealthResponse", "TraceStep"]

