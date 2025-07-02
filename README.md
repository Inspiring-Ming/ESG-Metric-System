# ESG Knowledge Graph System

A comprehensive knowledge graph-driven ESG reporting system with SASB framework support, designed for academic research and production deployment.

## 🌟 System Overview

This system transforms ESG (Environmental, Social, Governance) reporting through:
- **RDF Knowledge Graph**: Semantic modeling of SASB frameworks and corporate data
- **Interactive Web Interface**: User-friendly framework/metric selection and reporting
- **REST API**: 7 key endpoints for complete ESG workflow
- **Research-Grade Evaluation**: Performance benchmarks and analysis
- **Multi-Industry Support**: Semiconductors and Commercial Banks with extensible architecture

### Key Features
- ✅ **Real Data Integration**: 422,833+ ESG records from 40+ companies
- ✅ **SASB Framework Implementation**: Complete digital transformation of standards
- ✅ **CQ1-CQ7 Research Questions**: Full competency question implementation
- ✅ **Performance Benchmarks**: SPARQL query optimization and scalability analysis
- ✅ **Transparent Calculations**: Complete data lineage and transparency tracking
- ✅ **Production Ready**: Error handling, logging, and monitoring

## 🚀 Quick Start

### System Setup & Launch
```bash
# Clone and setup
git clone <repository>
cd esg-knowledge-graph-demo

# Install dependencies  
pip install -r requirements.txt

# Run comprehensive system demonstration
python run_comprehensive_system_demo.py
```

This will:
- Start the web interface at `http://localhost:8080` (auto port detection)
- Run all CQ1-CQ7 research questions
- Execute performance evaluation
- Generate research-grade visualizations
- Open browser to interactive interface

### Access Points
- **Web Interface**: `http://localhost:8080` (primary interface)
- **API Base URL**: `http://localhost:8080/api/v1`
- **System Health**: `http://localhost:8080/api/v1/system/health`

## 📁 Project Structure

```
esg-knowledge-graph-demo/
├── 📄 README.md                           # This file - comprehensive documentation
├── 🚀 run_comprehensive_system_demo.py    # Main entry point (recommended)
├── 📋 requirements.txt                    # Python dependencies
│
├── 🌐 web_interface/                      # Frontend interface
│   └── templates/
│       └── enhanced_demo.html             # Interactive web interface
│
├── 🔧 src/                                # Core system implementation  
│   ├── api/
│   │   └── esg_api.py                     # REST API with 35 endpoints (7 key workflow)
│   ├── services/
│   │   ├── data_retrieval_service.py      # Data loading and external dataset access
│   │   ├── unified_knowledge_graph_service.py  # RDF graph + CQ1-CQ7
│   │   ├── calculation_service.py         # ESG calculations with memory
│   │   └── comprehensive_report_service.py # Report generation
│   ├── evaluation/
│   │   └── performance_evaluator.py       # Comprehensive performance evaluation
│   └── utils/
│       └── port_manager.py                # Dynamic port management
│
├── 📊 data/                               # Data files and datasets
│   ├── raw/                              # SASB alignment files
│   ├── rdf/                              # RDF knowledge graph storage
│   └── External dataset/                 # Real ESG company data
│
├── 📈 evaluation_results/                 # Generated evaluation reports
│   ├── figures/                          # Performance visualizations
│   └── company_reports/                  # ESG company reports
└── 🔧 venv/                              # Python virtual environment
```

## 🎯 Core Components

### 1. Knowledge Graph Service (`UnifiedKnowledgeGraphService`)
**RDF Graph Construction + CQ1-CQ7 Implementation**
- Semantic modeling of SASB frameworks using RDF/OWL
- **613 RDF triples** with SASB framework relationships
- SPARQL query engine for knowledge retrieval
- Complete implementation of research competency questions:
  - **CQ1**: Which Reporting Framework applies to [industry]? (39.8ms avg)
  - **CQ2**: What Categories are included within [framework]? (21.6ms avg)
  - **CQ3**: Which Metrics are classified under [category]? (16.1ms avg)
  - **CQ4**: How is [metric] calculated or directly measured? (62.8ms avg)
  - **CQ5**: What Datapoints are required for [model]? (19.7ms avg)
  - **CQ6**: Which Implementation executes [model]? (implemented)
  - **CQ7**: What is the original Datasource for [datapoint]? (27.2ms avg)

### 2. REST API (`esg_api.py`)
**7 Key Workflow Endpoints - Performance Optimized**

```
API Endpoint Performance Visualization:

Industries API        ████▌ 5.3ms    ← Industry discovery
Companies API         ████████████████▌ 17.4ms  ← Company selection  
Frameworks API        ██████████▌ 11.1ms   ← Framework identification
Categories API        ████████████████▌ 17.2ms  ← Category mapping
Metrics API           ████████████▌ 13.3ms   ← Metric discovery
Calculate API         ████████████████████████████████████████████████████████████████▌ 130.7ms ← ESG calculations
Reports API           ███████████████▌ 16.5ms  ← Report generation

Scale: Each █ = ~2ms response time
```

**Complete ESG Workflow**: 211ms end-to-end

#### Core Workflow Endpoints
| **Endpoint** | **Method** | **Performance** | **Workflow Phase** |
|-------------|------------|----------------|-------------------|
| `/industries` | GET | 5.3ms | Discovery |
| `/industries/{industry}/companies` | GET | 17.4ms | Discovery |
| `/industries/{industry}/reporting-frameworks` | GET | 11.1ms | Discovery |
| `/reporting-frameworks/{framework}/categories` | GET | 17.2ms | Analysis |
| `/categories/{category}/metrics-detailed` | GET | 13.3ms | Analysis |
| `/calculate` | POST | 130.7ms | Computation |
| `/reports/generate` | POST | 16.5ms | Reporting |

### 3. Web Interface (`enhanced_demo.html`)
**Interactive user interface with professional UX**
- Step-by-step workflow: Framework → Industry → Category → Actions
- Real-time metric calculations with progress indicators
- Comprehensive report generation with download capabilities
- Performance monitoring dashboard
- Complete data lineage visualization
- Visual calculation status indicators (✅ for completed metrics)

### 4. Performance Evaluation System (`PerformanceEvaluator`)
**Research-focused performance analysis and benchmarking**

#### Actual Performance Metrics
- **CQ Query Performance**: 31.2ms average (7/7 implemented)
- **API Performance**: 30.2ms average (100% success rate)
- **Service Performance**: 35.5ms average (4/4 operational)
- **Calculate API**: 130.7ms (most complex operation)

#### Generated Visualizations
- **CQ Query Performance Chart**: All 7 competency questions performance
- **API Performance Chart**: 7 key endpoints with workflow phases  
- **Service Performance Chart**: 4 core services analysis
- **System Performance Analysis**: Complete overview chart

### 5. Service Architecture

#### Data Retrieval Service (`DataRetrievalService`)
- **External Dataset Access**: 422,833+ ESG records from 40+ companies
- **SASB Framework Loading**: Real framework data for semiconductors and commercial banks
- **Company Data Access**: Verified data for companies like "Powerchip Semiconductor Manufacturing Corp"
- **Performance**: 9.0ms average response time

#### Unified Knowledge Graph Service (`UnifiedKnowledgeGraphService`)
- **RDF Knowledge Graph**: 613 semantic triples
- **SPARQL Query Engine**: Custom queries for CQ1-CQ7 research questions  
- **Real Data Integration**: Live RDF queries for data consistency
- **Performance**: 8.2ms average response time

#### Calculation Service (`CalculationService`)
- **Integrated Memory Management**: Persistent storage of calculated metrics
- **Real Data Integration**: Access to external dataset values
- **Model Calculations**: Renewable Energy Rate Model, Grid Electricity Rate Model
- **Performance**: 101.7ms average (includes complex ESG calculations)

#### Comprehensive Report Service (`ComprehensiveReportService`)
- **Cross-Category Analysis**: Complete ESG metrics across all categories
- **Data Source Transparency**: Full traceability from raw data to final metrics
- **Visual Status Indicators**: ✅ Memory, 🧮 Calculated, 📊 Direct access
- **Performance**: 23.1ms average response time

## 🔬 Academic Research Support

### Competency Questions Implementation
All 7 research competency questions implemented with performance benchmarking:

```python
# Example: Execute all CQ questions for semiconductors industry
kg_service = UnifiedKnowledgeGraphService(data_service)

# CQ1: Framework identification (39.8ms average)
framework = kg_service.cq1_reporting_framework_by_industry("semiconductors")
# Returns: {"framework": "SASB Semiconductors Standard"}

# CQ2: Categories enumeration (21.6ms average)
categories = kg_service.cq2_categories_by_framework("semiconductors")
# Returns: 9 ESG categories with descriptions

# CQ3-CQ7: Continue with other research questions...
```

### Performance Benchmarks
Research-grade performance analysis with actual measured results:

```python
evaluator = PerformanceEvaluator(data_service, kg_service, calc_service)
results = evaluator.run_comprehensive_evaluation()

# Actual academic metrics generated:
# - CQ Query Performance: 31.2ms average (7/7 working)
# - API Performance: 30.2ms average (100% success)
# - Service Performance: 35.5ms average (4/4 operational)
# - Complete Workflow: 211ms end-to-end
```

### Research Data Quality
- **Real Data Only**: 422,833+ verified ESG records
- **No Synthetic Data**: Complete authentic dataset integration
- **Performance Transparency**: All timings from actual system operations
- **Success Rates**: 100% operational across all core components

## 📊 System Performance - Actual Results

### Latest Performance Evaluation Results
**Source**: `evaluation_results/system_performance_20250629_235036.json`

#### CQ Query Performance (7/7 Implemented)
- **CQ1**: 39.8ms - Reporting Framework by Industry
- **CQ2**: 21.6ms - Categories by Framework  
- **CQ3**: 16.1ms - Metrics by Category
- **CQ4**: 62.8ms - Metric Calculation Method
- **CQ5**: 19.7ms - Model Input Datapoints
- **CQ6**: Implemented - Model Implementation
- **CQ7**: 27.2ms - Datapoint Original Source

#### API Performance (100% Success)
- **Industries**: 5.3ms (fastest)
- **Companies**: 17.4ms
- **Frameworks**: 11.1ms
- **Categories**: 17.2ms
- **Metrics**: 13.3ms
- **Calculate**: 130.7ms (most complex)
- **Reports**: 16.5ms

#### Service Performance (4/4 Operational)
- **Data Retrieval**: 9.0ms average
- **Knowledge Graph**: 8.2ms average
- **Calculation**: 101.7ms average (with memory)
- **Report Generation**: 23.1ms average

### System Data Architecture
- **ESG Records**: 422,833+ real company records
- **Companies**: 40+ companies with multi-year data
- **RDF Triples**: 613 semantic relationships
- **Industries**: Semiconductors, Commercial Banks
- **Success Rate**: 100% across all components

## 🛠️ API Quick Reference

### Base URL: `http://localhost:8080/api/v1`

### Quick API Testing
```bash
# Start the system
python run_comprehensive_system_demo.py

# Test core workflow endpoints
curl http://localhost:8080/api/v1/industries
curl http://localhost:8080/api/v1/industries/semiconductors/companies
curl http://localhost:8080/api/v1/system/health
```

### Workflow Phases
1. **Discovery Phase** (33.8ms): Industries → Companies → Frameworks
2. **Analysis Phase** (30.5ms): Categories → Metrics
3. **Computation Phase** (130.7ms): ESG Calculations
4. **Reporting Phase** (16.5ms): Comprehensive Reports

**Total**: 211ms for complete ESG analysis workflow

## 🎉 System Status: EXCELLENT PERFORMANCE

### All Components Operational (100% Success)
- ✅ **API Layer**: 7 key endpoints, 30.2ms average
- ✅ **CQ Queries**: 7/7 implemented, 31.2ms average  
- ✅ **Services**: 4/4 operational, 35.5ms average
- ✅ **Data Authenticity**: 422,833+ verified real records
- ✅ **Research Ready**: Production-grade performance with realistic timings

### Key Production Features
- **Real Data Integration**: 422,833+ ESG records properly accessed
- **Cross-session Memory**: Maintaining calculated metrics across categories
- ✅ **Visual Status Indicators**: ✅ icons preventing duplicate calculations  
- ✅ **Comprehensive Reports**: Complete data source transparency
- ✅ **Performance Monitoring**: Real-time system health checks
- ✅ **Industry Workflow**: Enhanced user feedback and error handling

## 🚀 Getting Started Guide

### 1. System Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Launch System
```bash
# Single command startup
python run_comprehensive_system_demo.py
```

### 3. Access System
- **Web Interface**: `http://localhost:8080` (automatically opens)
- **API Access**: `http://localhost:8080/api/v1/*`
- **Health Check**: `http://localhost:8080/api/v1/system/health`

### 4. ESG Analysis Workflow
1. **Select Industry**: Choose semiconductors or commercial_banks
2. **Browse Categories**: Explore ESG categories (GHG Emissions, Energy, etc.)
3. **Calculate Metrics**: Real ESG calculations with 100% authentic data
4. **Generate Reports**: Comprehensive analysis with data lineage

### 5. Performance Evaluation
```bash
# Comprehensive system evaluation
# Results saved in evaluation_results/ with visualizations
python -c "
from src.evaluation.performance_evaluator import ComprehensivePerformanceEvaluator
from src.services.data_retrieval_service import DataRetrievalService
from src.services.unified_knowledge_graph_service import UnifiedKnowledgeGraphService  
from src.services.calculation_service import CalculationService

data_service = DataRetrievalService()
kg_service = UnifiedKnowledgeGraphService(data_service)
calc_service = CalculationService(data_service)
evaluator = ComprehensivePerformanceEvaluator(data_service, kg_service, calc_service)
evaluator.run_comprehensive_evaluation()
"
```

## 📈 Research & Production Ready

The ESG Knowledge Graph System provides:
- **Complete Transparency**: Full data lineage and source tracking
- **Real Performance**: All metrics from actual system operations (no synthetic data)
- **Academic Research**: 7 competency questions with performance benchmarks
- **Production Deployment**: 100% success rate, comprehensive error handling
- **Scalable Architecture**: Designed for expansion beyond current 2 industries

**System Version**: ESG Knowledge Graph v1.0  
**Latest Evaluation**: system_performance_20250629_235036.json  
**Performance Status**: Excellent - All Components Operational