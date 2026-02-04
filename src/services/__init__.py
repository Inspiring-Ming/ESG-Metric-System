# src/services/__init__.py
"""
ESG Knowledge Graph Services

Clean service architecture with 4 core services:
- KnowledgeGraphService: Knowledge graph operations and CQ1-CQ7 (RDF/SPARQL)
- DataRetrievalService: External dataset access and company data retrieval
- CalculationService: ESG metric calculations with semantic flow (CQ4→CQ5→CQ6→CQ7)
- ReportService: Complete report generation (Word and PDF)
"""

from .knowledge_graph_service import KnowledgeGraphService
from .data_retrieval_service import DataRetrievalService
from .calculation_service import CalculationService
from .report_service import ReportService

__all__ = [
    'KnowledgeGraphService',
    'DataRetrievalService',
    'CalculationService',
    'ReportService'
]