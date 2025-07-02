# src/services/__init__.py
"""
ESG Knowledge Graph Services

Consolidated service architecture with 4 core services:
- DataRetrievalService: Unified data loading and external dataset access
- UnifiedKnowledgeGraphService: All knowledge graph operations and CQ1-CQ7  
- CalculationService: ESG calculations with integrated memory management
- ComprehensiveReportService: All ESG report generation capabilities

This consolidation eliminates:
- calculation_memory_service (merged into CalculationService)
- external_data_service (merged into DataRetrievalService)  
- report_service (merged into ComprehensiveReportService)
"""

from .data_retrieval_service import DataRetrievalService
from .unified_knowledge_graph_service import UnifiedKnowledgeGraphService
from .calculation_service import CalculationService
from .comprehensive_report_service import ComprehensiveReportService

__all__ = [
    'DataRetrievalService',
    'UnifiedKnowledgeGraphService', 
    'CalculationService',
    'ComprehensiveReportService'
]