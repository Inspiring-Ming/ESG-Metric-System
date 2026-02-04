# ESG Knowledge Graph System

An ontology-driven ESG (Environmental, Social, and Governance) reporting system built on SASB standards. The system uses an RDF knowledge graph to map reporting frameworks, categories, metrics, and calculation models, then retrieves real company data from external datasets to compute ESG metrics and generate structured reports.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Competency Questions (CQ1–CQ7)](#competency-questions-cq1cq7)
- [Adding New Industries](#adding-new-industries)
- [Configuration](#configuration)

---

## Overview

### What it does

1. **Knowledge Graph** — An RDF/Turtle ontology encodes SASB reporting frameworks, ESG categories, metrics, calculation models, and data source mappings (525 triples).
2. **Data Retrieval** — Loads real ESG company data from CSV datasets (422K+ records across 40+ companies in semiconductors and commercial banking).
3. **Metric Calculation** — Resolves how each metric should be computed (direct measurement vs. calculation model) and executes the computation using the appropriate data.
4. **Report Generation** — Produces formatted PDF and Word reports with cover page, table of contents, executive summary, metrics tables, data lineage, and methodology sections.

### Supported Industries

| Industry | SASB Standard | Categories | Dataset Records |
|----------|--------------|------------|-----------------|
| Semiconductors | TC-SC | 8 categories | 105K+ records |
| Commercial Banks | FN-CB | 6 categories | 317K+ records |

### Tech Stack

- **Backend:** Python 3.9+, Flask, RDFLib, Pandas
- **Frontend:** HTML/CSS/JavaScript (single-page app served by Flask)
- **Reports:** ReportLab (PDF), python-docx (Word)
- **Data:** RDF/Turtle (ontology), CSV (company data)

---

## Getting Started

### Prerequisites

- Python 3.9 or later
- pip

### Installation

```bash
git clone https://github.com/Inspiring-Ming/ESG-Metric-System.git
cd ESG-Metric-System

pip install -r requirements.txt
```

### Running

```bash
python run_comprehensive_system_demo.py
```

The system starts on port 5000 (auto-increments if occupied). Open `http://localhost:5000/` in a browser to access the web interface.

### Quick API Test

```bash
curl http://localhost:5000/api/KGservice/industries
curl http://localhost:5000/api/DRservice/industries/semiconductors/companies
curl http://localhost:5000/api/v1/system/health
```

---

## Project Structure

```
ESG-Metric-System/
├── run_comprehensive_system_demo.py       # Entry point
├── requirements.txt
│
├── src/
│   ├── api/
│   │   └── esg_api.py                     # Flask API gateway (20+ endpoints)
│   ├── services/
│   │   ├── knowledge_graph_service.py     # RDF/SPARQL, CQ1–CQ7
│   │   ├── data_retrieval_service.py      # CSV data access
│   │   ├── calculation_service.py         # ESG metric calculations
│   │   └── report_service.py             # PDF and Word report generation
│   ├── models/                            # Calculation model definitions
│   └── utils/
│       └── port_manager.py               # Port detection and process management
│
├── data/
│   ├── rdf/
│   │   └── esg_knowledge_graph.ttl       # RDF knowledge graph (525 triples)
│   └── External dataset/                 # Company ESG data (CSV)
│
├── web_interface/
│   └── templates/
│       └── enhanced_demo.html            # Web UI
│
└── generated_reports/                    # Output directory for PDF/Word reports
```

---

## Architecture

```
Browser (enhanced_demo.html)
    │
    │  HTTP/JSON
    ▼
API Gateway (esg_api.py)
    │
    ├── /api/KGservice/*  →  KnowledgeGraphService   →  RDF/Turtle file
    ├── /api/DRservice/*  →  DataRetrievalService     →  CSV datasets
    ├── /api/CSservice/*  →  CalculationService       →  (uses KG + Data services)
    └── /api/RSservice/*  →  ReportService            →  generated_reports/
```

### Services

| Service | File | Role |
|---------|------|------|
| **Knowledge Graph** | `knowledge_graph_service.py` | Loads the RDF ontology, answers CQ1–CQ7 via SPARQL, resolves framework/category/metric/model relationships |
| **Data Retrieval** | `data_retrieval_service.py` | Reads CSV datasets, looks up companies/years, retrieves variable values for metric computation |
| **Calculation** | `calculation_service.py` | Orchestrates the CQ4→CQ5→CQ6→CQ7 flow to determine how a metric is measured and compute its value |
| **Report** | `report_service.py` | Generates PDF and Word documents from calculation results |

### Frontend Flow

1. Select **Company** → industry auto-detected from dataset
2. Select **Year** → available reporting frameworks load from knowledge graph (CQ1)
3. Select **Reporting Framework** → categories load (CQ2)
4. Select **Category** → metrics load with measurement methods (CQ3–CQ5)
5. Click metrics to add to calculation table → compute values (CQ6–CQ7)
6. Download PDF or Word report

---

## API Reference

All endpoints return JSON. The API is organized by service prefix.

### Knowledge Graph Service (`/api/KGservice`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/industries` | List available industries |
| GET | `/industries/{industry}/frameworks` | Get reporting frameworks for an industry (CQ1) |
| GET | `/frameworks/{framework}/categories` | Get categories within a framework (CQ2) |
| GET | `/categories/{category}/metrics` | Get metrics in a category (CQ3) |
| GET | `/metrics/{metric}/models` | Get calculation models for a metric (CQ4–CQ5) |

### Data Retrieval Service (`/api/DRservice`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/industries/{industry}/companies` | List companies in an industry |
| GET | `/companies/{company}/years` | Get available years for a company |
| GET | `/companies/{company}/industry` | Get industry for a company |
| GET | `/companies/all` | Get all companies grouped by industry |
| GET | `/data-availability/{company}/{year}` | Check data availability |

### Calculation Service (`/api/CSservice`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/calculate` | Calculate ESG metrics for a company/year |

**Request body:**
```json
{
  "company_name": "NVIDIA",
  "year": 2020,
  "industry": "semiconductors",
  "metrics": ["TC-SC-130a.1", "TC-SC-140a.1"]
}
```

### Report Service (`/api/RSservice`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/reports/generate-pdf` | Generate a PDF report |
| POST | `/reports/generate-word` | Generate a Word report |
| GET | `/reports/download/{filename}` | Download a generated report |

### Legacy Endpoints

All endpoints are also available under `/api/v1/*` for backward compatibility.

---

## Competency Questions (CQ1–CQ7)

The knowledge graph is designed around seven competency questions that define the information retrieval and computation workflow:

| CQ | Question | Service Method |
|----|----------|---------------|
| CQ1 | Which reporting framework applies to a given industry? | `cq1_reporting_framework_by_industry(industry)` |
| CQ2 | What categories are included in the framework? | `cq2_categories_by_framework(industry)` |
| CQ3 | Which metrics belong to a given category? | `cq3_metrics_by_category(industry, category)` |
| CQ4 | How is a metric calculated (direct measurement or model)? | `cq4_metric_calculation_method(industry, metric)` |
| CQ5 | What input data points does a calculation model require? | `cq5_model_input_datapoints(industry, metric)` |
| CQ6 | What is the model equation/implementation? | `cq6_model_implementation(industry, metric)` |
| CQ7 | Where does each data point originate (dataset variable mapping)? | `cq7_datapoint_source(industry, metric)` |

### Programmatic Usage

```python
from src.services.knowledge_graph_service import KnowledgeGraphService
from src.services.data_retrieval_service import DataRetrievalService

data_service = DataRetrievalService()
kg_service = KnowledgeGraphService(data_service)

# CQ1: Get reporting framework
framework = kg_service.cq1_reporting_framework_by_industry("semiconductors")

# CQ2: Get categories
categories = kg_service.cq2_categories_by_framework("semiconductors")

# CQ3: Get metrics for a category
metrics = kg_service.cq3_metrics_by_category("semiconductors", "Energy Management in Manufacturing")
```

---

## Adding New Industries

1. **Define RDF triples** in `data/rdf/esg_knowledge_graph.ttl`:

```turtle
esg:automotive a esg:Industry ;
    rdfs:label "Automotive" ;
    esg:reportsUsing esg:SASBAutomotive .

esg:SASBAutomotive a esg:ReportingFramework ;
    rdfs:label "SASB Automotive" ;
    esg:includes esg:AutoGHGEmissions ;
    esg:sourceDocument "automotive-standard_en-gb.pdf" .
```

2. **Add CSV data** to `data/External dataset/`

3. **Update `DataRetrievalService`** to load the new dataset

4. **Test** by running the system:
```bash
python run_comprehensive_system_demo.py
```

---

## Configuration

### Port Management

The system auto-detects available ports starting from 5000. To specify a port:

```bash
python run_comprehensive_system_demo.py --port 8080
```

`port_manager.py` handles detecting port conflicts and cleaning up stale processes.

### File Paths

All services resolve file paths relative to the project root using `Path(__file__).resolve()`, so the system works regardless of the working directory.

---

## License

See [LICENSE](LICENSE) for details.
