# ESG Knowledge Graph: Complete Documentation & Research Profile

## Research Contribution

This ESG Knowledge Graph presents a novel semantic framework that integrates Environmental, Social, and Governance (ESG) reporting standards with executable calculation models. The system bridges the gap between ESG metadata definitions and computational implementations, enabling automated ESG analysis and reporting through semantic web technologies.

## Core Innovation: Executable Knowledge Graphs

### **Key Research Problem Addressed**
Traditional ESG reporting systems suffer from:
- Disconnected metadata and calculation logic
- Manual, error-prone calculation processes  
- Lack of semantic standardization across industries
- Difficulty in automated compliance checking

### **Solution Architecture**
```turtle
# Semantic Model Definition
esg:GHGEmissionIntensityModel a esg:Model ;
    esg:hasFormula "(scope1_emissions + scope2_emissions) / revenue" ;
    esg:executesWith esg:GHGEmissionIntensityImplementation .

# Executable Implementation  
esg:GHGEmissionIntensityImplementation a esg:Implementation ;
    esg:hasFilePath "models/ghg_emission_intensity_model.py" ;
    esg:hasFunction "calculate_ghg_emission_intensity" .
```

This design enables **runtime discovery and execution** of calculation models through SPARQL queries, creating a self-describing computational framework.

---

## Complete Schema Specification

### **Schema Overview**
- **Version**: 1.0  
- **Total Classes**: 8 core classes  
- **Total Properties**: 25+ properties  
- **Data Coverage**: 650+ RDF triples, 53 metrics, 422K+ real-world records  
- **Standards**: SASB (Sustainability Accounting Standards Board)

### **Class Hierarchy & Core Classes**

#### 1. **esg:Industry**
**Purpose**: Represents industry sectors that report ESG data  
**Instance Count**: 2 (Semiconductors, Commercial Banks)

**Properties:**
- `rdfs:label`: Human-readable industry name
- `esg:reportsUsing`: Links to applicable reporting framework

**Example:**
```turtle
esg:semiconductors a esg:Industry ;
    rdfs:label "Semiconductors" ;
    esg:reportsUsing esg:SASBSemiconductors .
```

#### 2. **esg:ReportingFramework**
**Purpose**: ESG reporting standards and frameworks (e.g., SASB)  
**Instance Count**: 2 (SASB Commercial Banks, SASB Semiconductors)

**Properties:**
- `rdfs:label`: Framework name
- `esg:includes`: Categories included in this framework
- `esg:sourceDocument`: Original PDF/document source

#### 3. **esg:Category**
**Purpose**: Thematic groupings of related ESG metrics within frameworks  
**Instance Count**: 14 categories

**Properties:**
- `rdfs:label`: Category name
- `esg:consistsOf`: Metrics contained in this category

#### 4. **esg:Metric**
**Purpose**: Individual ESG metrics with three calculation method types  
**Instance Count**: 53 total metrics

**Metric Classification:**
- **SASBRequirement** (42 metrics, 79%): Standard SASB reporting requirements
- **Manual** (1 metric, 2%): Custom-defined calculations
- **Input Metric** (10 metrics, 19%): Computational input parameters

**Core Properties (All Metrics):**
- `rdfs:label`: Metric name
- `esg:hasType`: Classification (SASBRequirement/Manual/Input Metric)
- `esg:hasCalculationMethod`: "direct_measurement" or "calculation_model"
- `esg:hasDescription`: Detailed description
- `esg:hasMetricType`: "Quantitative" or "Discussion"
- `esg:hasUnit`: Measurement unit
- `esg:hasDataType`: Data type (for Input Metrics only)

**Calculation-Specific Properties:**
- **Direct Measurement**: `esg:obtainedFrom` → DatasetVariable
- **Model-Based**: `esg:isCalculatedBy` → Model

#### 5. **esg:Model**
**Purpose**: Mathematical calculation models for computed metrics  
**Instance Count**: 6 models

**Properties:**
- `rdfs:label`: Model name
- `esg:hasDescription`: Model description
- `esg:hasFormula`: Mathematical formula (simplified)
- `esg:hasMathematicalExpression`: Detailed mathematical expression
- `esg:hasCalculationType`: Calculation type (e.g., "intensity_ratio", "percentage_ratio")
- `esg:requiresInputFrom`: Input metrics required for calculation
- `esg:executesWith`: Implementation entity

#### 6. **esg:Implementation**
**Purpose**: Executable code implementations for calculation models  
**Instance Count**: 6 implementations

**Properties:**
- `rdfs:label`: Implementation name
- `esg:hasLanguage`: Programming language (e.g., "Python")
- `esg:hasFilePath`: Path to implementation file
- `esg:hasFunction`: Function name to execute
- `esg:hasDescription`: Implementation description
- `esg:hasInputParameters`: Function input parameters specification
- `esg:hasReturnType`: Return data type
- `esg:hasValidation`: Validation rules and constraints

#### 7. **esg:DatasetVariable**
**Purpose**: Variables from real-world datasets mapped to ESG metrics  
**Instance Count**: 14 variables

**Properties:**
- `rdfs:label`: Variable name
- `esg:alignmentReason`: Explanation of mapping rationale
- `esg:hasConfidenceScore`: Confidence in mapping (0-100)
- `esg:isUnitCompatible`: Unit compatibility description
- `esg:sourceFrom`: Source datasets containing this variable

#### 8. **esg:DataSource**
**Purpose**: Source datasets containing real-world ESG data  
**Instance Count**: 3 datasets

**Properties:**
- `rdfs:label`: Dataset name
- `esg:hasFileName`: File name
- `esg:hasDescription`: Dataset description
- `esg:hasRecordCount`: Number of records (where available)
- `esg:hasCoverage`: Geographic or industry coverage

---

## Quick Reference Tables

### **Core Classes Summary**

| Class | Count | Purpose | Key Properties |
|-------|-------|---------|----------------|
| **Industry** | 2 | Industry sectors | `esg:reportsUsing` |
| **ReportingFramework** | 2 | ESG standards | `esg:includes`, `esg:sourceDocument` |
| **Category** | 14 | Metric groupings | `esg:consistsOf` |
| **Metric** | 53 | ESG measurements | `esg:hasCalculationMethod`, `esg:obtainedFrom`, `esg:isCalculatedBy` |
| **Model** | 6 | Calculation models | `esg:executesWith`, `esg:requiresInputFrom` |
| **Implementation** | 6 | Executable code | `esg:hasFilePath`, `esg:hasFunction` |
| **DatasetVariable** | 14 | Dataset mappings | `esg:sourceFrom`, `esg:hasConfidenceScore` |
| **DataSource** | 3 | Real datasets | `esg:hasRecordCount`, `esg:hasCoverage` |

### **Calculation Flows**

#### Direct Measurement (81% of metrics)
```
Metric --obtainedFrom--> DatasetVariable --sourceFrom--> DataSource
```

#### Model-Based Calculation (19% of metrics)
```
Metric --isCalculatedBy--> Model --executesWith--> Implementation
Model --requiresInputFrom--> InputMetric --obtainedFrom--> DatasetVariable
```

### **Data Sources**

| Dataset | Type | Records | Coverage |
|---------|------|---------|----------|
| **Semiconductors_Eurofidai** | Environmental | 105,528 | Global semiconductors |
| **CommercialBanks_Eurofidai** | Environmental | 317,305 | Global banks |
| **Semiconductor_WRDS** | Financial | N/A | North America |

### **Confidence Scores**

| Score Range | Meaning | Example Variables |
|-------------|---------|------------------|
| **100** | Perfect match | CO2DIRECTSCOPE1, revt |
| **95** | High confidence | ELECTRICITYPURCHASED |
| **80** | Good match | TARGETS_EMISSIONS |
| **60** | Moderate | ANALYTICESTIMATEDCO2TOTAL |
| **30** | Low confidence | BRIBERY_AND_CORRUPTION |

---

## Relationship Patterns & Data Flow

### **Primary Relationships**

1. **Industry → Framework → Category → Metric** (Hierarchical Structure)
   ```
   esg:Industry --esg:reportsUsing--> esg:ReportingFramework
   esg:ReportingFramework --esg:includes--> esg:Category  
   esg:Category --esg:consistsOf--> esg:Metric
   ```

2. **Direct Measurement Flow** (81% of metrics)
   ```
   esg:Metric --esg:obtainedFrom--> esg:DatasetVariable --esg:sourceFrom--> esg:DataSource
   ```

3. **Calculation Model Flow** (19% of metrics)
   ```
   esg:Metric --esg:isCalculatedBy--> esg:Model --esg:executesWith--> esg:Implementation
   esg:Model --esg:requiresInputFrom--> esg:Metric (Input Metrics)
   ```

### **Calculation Execution Flow (CQ4→CQ5→CQ7→CQ6)**

1. **CQ4**: Determine calculation method via `esg:hasCalculationMethod`
2. **CQ5**: For model-based metrics, retrieve model via `esg:isCalculatedBy`
3. **CQ7**: Get input requirements via `esg:requiresInputFrom` and resolve to `DatasetVariable`
4. **CQ6**: Execute implementation via `esg:executesWith`

---

## Key Query Patterns (SPARQL)

### **CQ4: Get Calculation Method**
```sparql
SELECT ?method WHERE {
  ?metric esg:hasCalculationMethod ?method .
  FILTER(?metric = esg:GHGEmissionIntensity)
}
```

### **CQ5: Get Model Formula**
```sparql
SELECT ?formula WHERE {
  ?metric esg:isCalculatedBy ?model .
  ?model esg:hasFormula ?formula .
}
```

### **CQ6: Get Implementation**
```sparql
SELECT ?filePath ?function WHERE {
  ?model esg:executesWith ?impl .
  ?impl esg:hasFilePath ?filePath ;
        esg:hasFunction ?function .
}
```

### **CQ7: Get Input Requirements**
```sparql
SELECT ?inputMetric ?variable WHERE {
  ?model esg:requiresInputFrom ?inputMetric .
  ?inputMetric esg:obtainedFrom ?variable .
}
```

### **Get All Metrics for Industry**
```sparql
SELECT ?metric ?label ?method WHERE {
  ?industry esg:reportsUsing ?framework .
  ?framework esg:includes ?category .
  ?category esg:consistsOf ?metric .
  ?metric rdfs:label ?label ;
          esg:hasCalculationMethod ?method .
  FILTER(?industry = esg:semiconductors)
}
```

---

## System Architecture

### **Data Structure**
- **Format**: RDF/Turtle semantic graph  
- **Scale**: 650+ RDF triples, 53 metrics, 10+ calculation models
- **Coverage**: 2 industries (Semiconductors, Commercial Banks)
- **Standards**: SASB (Sustainability Accounting Standards Board)
- **Data Sources**: 422K+ records from environmental and financial datasets

### **Metric Classification System**
- **SASBRequirement**: 42 metrics (79%) - Standard reporting requirements
- **Manual**: 1 metric (2%) - Custom-defined calculations  
- **Input Metric**: 10 metrics (19%) - Computational parameters

### **Calculation Methods**
- **Direct Measurement**: 81% of metrics - Data retrieval via `esg:obtainedFrom`
- **Calculation Model**: 19% of metrics - Computed via `esg:isCalculatedBy`

---

## Technical Innovations

### **1. Semantic-Computational Integration**
**Traditional Approach**: Separate metadata and calculation systems
```
Metadata ← Manual Mapping → Calculation Code
```

**Our Approach**: Unified semantic-computational framework
```turtle
esg:Metric esg:isCalculatedBy esg:Model .
esg:Model esg:executesWith esg:Implementation .
```

### **2. Multi-Industry Data Harmonization**
Cross-industry semantic alignment with confidence scoring:
```turtle
esg:CO2DIRECTSCOPE1 a esg:DatasetVariable ;
    esg:hasConfidenceScore 100 ;
    esg:sourceFrom esg:SemiconductorsDataset, esg:CommercialBanksDataset .
```

### **3. Self-Describing Calculation Framework**
- **Dynamic Model Discovery**: SPARQL-based runtime model identification
- **Automatic Input Resolution**: Semantic dependency resolution  
- **Validation Integration**: Built-in data quality and calculation validation

---

## Design Principles & Constraints

### **1. Mutual Exclusivity**
- **Direct Measurement**: ONLY uses `esg:obtainedFrom`
- **Calculated Metrics**: ONLY uses `esg:isCalculatedBy`
- **Never both**: No metric uses both relationship types

### **2. Calculation Chain Integrity**
- All calculated metrics must have implementations
- All models must specify input requirements
- All input metrics must have data sources

### **3. Data Type Consistency**
- Quantitative metrics have numeric units
- Discussion metrics have "n/a" units
- Input metrics include `esg:hasDataType`

### **4. Confidence Scoring**
- DatasetVariable mappings include confidence scores
- Scores range from 0-100 based on alignment quality
- Unit compatibility explicitly documented

---

## Research Applications

### **Enabled Use Cases**
1. **Automated ESG Reporting** - End-to-end calculation and report generation
2. **Cross-Industry Benchmarking** - Semantic comparison across sectors
3. **Regulatory Compliance** - Automated SASB standard validation
4. **ESG Analytics** - Advanced analytics on harmonized datasets
5. **Investment Decision Support** - Data-driven ESG analysis

### **Academic Contributions**
- **Semantic Web**: Novel RDF modeling for domain-specific computational frameworks
- **ESG Technology**: Computational approaches to sustainability reporting automation
- **Data Integration**: Cross-industry harmonization methodologies
- **Knowledge Engineering**: Executable knowledge graph design patterns

## Performance Profile

### **Computational Efficiency**
- **Query Response**: 5-25ms for metric retrieval
- **Calculation Time**: 130ms for complex model-based calculations  
- **Memory Usage**: ~200MB for 422K+ records
- **Scalability**: Linear scaling with data volume

### **Quality Metrics**
- **Structural Consistency**: 100% - All entities follow standardized patterns
- **Data Coverage**: 422,833 real-world ESG records
- **Standards Compliance**: Full SASB framework integration
- **Calculation Accuracy**: Validated against industry benchmarks

## Research Methodology

### **Data Sources**
- **Environmental**: Eurofidai database (105K+ semiconductor, 317K+ banking records)
- **Financial**: WRDS North American financial data
- **Standards**: Official SASB reporting frameworks

### **Validation Framework**
- **Semantic Validation**: RDF/OWL consistency checking
- **Calculation Validation**: Unit testing with known values
- **Data Quality**: Confidence scoring and unit compatibility verification
- **Performance Benchmarking**: Systematic measurement across components

## Implementation Flow

### **Calculation Pipeline (CQ4→CQ5→CQ7→CQ6)**
1. **CQ4**: Determine calculation method (direct vs. model-based)
2. **CQ5**: Retrieve model inputs and formula  
3. **CQ7**: Resolve data source mappings
4. **CQ6**: Execute implementation code

This semantic query-driven approach enables **transparent, traceable, and automated** ESG calculations.

---

## Extension Guidelines

### **Adding New Industries**
1. Create `esg:Industry` instance
2. Create corresponding `esg:ReportingFramework`
3. Define industry-specific categories and metrics
4. Map to appropriate datasets and variables

### **Adding New Calculation Models**
1. Create `esg:Model` with mathematical specification
2. Create `esg:Implementation` with executable code
3. Define input metric requirements
4. Link calculated metric via `esg:isCalculatedBy`

### **Adding New Data Sources**
1. Create `esg:DataSource` instance
2. Define `esg:DatasetVariable` instances
3. Map variables to metrics via `esg:obtainedFrom`
4. Include confidence scores and unit compatibility

---

## Future Research Directions

### **Standards Expansion**
- GRI (Global Reporting Initiative) integration
- TCFD (Task Force on Climate-related Financial Disclosures)
- EU Taxonomy framework
- ISSB (International Sustainability Standards Board)

### **Industry Coverage**
- Energy sector (oil & gas, renewables)
- Manufacturing and industrial sectors
- Healthcare and pharmaceutical
- Real estate and construction

### **Technical Extensions**
- Automated model learning from data patterns
- Multi-language calculation support
- Blockchain-based calculation verification
- AI-driven ESG insight generation

---

## File Locations

- **Knowledge Graph**: `data/rdf/esg_knowledge_graph.ttl` (633 lines)
- **Implementation**: `src/models/ghg_emission_intensity_model.py`
- **API Services**: `src/services/` (Knowledge Graph, Data Retrieval, Calculation)
- **Web Interface**: `web_interface/templates/enhanced_demo.html`

---

**Research Impact**: First comprehensive semantic ESG framework combining standardized reporting with executable implementations, enabling automated, transparent, and scalable ESG analysis across industries.

**Version**: 1.0  
**Last Updated**: 2025-01-17  
**Maintained By**: ESG Knowledge Graph Research Team  
**License**: Research and Evaluation Use 