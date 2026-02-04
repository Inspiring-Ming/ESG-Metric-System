"""
Data Retrieval Service for Ontometric System

Consolidates data loading and retrieval functionality for framework data,
alignment data, and company ESG datasets. Supports calculation service
with data value access.
"""

import json
import os
import time
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional

class DataRetrievalService:
    """Service for retrieving and managing ESG data from various sources"""
    
    def __init__(self, data_dir: str = "data/raw"):
        """Initialize data retrieval service with external dataset access"""
        # Get project root directory (2 levels up from this file)
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent

        # Use absolute paths from project root
        self.data_dir = project_root / data_dir if not Path(data_dir).is_absolute() else Path(data_dir)
        self.csv_sample = None
        self._validate_data_directory()

        # External dataset configuration - LAZY LOADING for performance
        self.external_dataset_path = project_root / "data/External dataset/Raw data with industry.csv"
        self.external_df = None
        self.industry_datasets = {}
        self._datasets_loaded = False
        
        # Initialize demo companies for fallback
        self.demo_companies = {
            "semiconductors": {
                "STMicroelectronics NV": "Advanced semiconductor manufacturer with comprehensive ESG data",
                "ON Semiconductor Corp": "Global semiconductor solutions provider"
            },
            "commercial_banks": {
                "Banco Santander SA": "Major European commercial bank with extensive ESG metrics", 
                "Taishin Financial Holding Co Ltd": "Taiwan-based financial services company"
            }
        }
        
        print("⚡ DataRetrievalService initialized with lazy loading (datasets load on first access)")
        
        # Enhanced error categories are provided by the error_categories property method
        
    def _validate_data_directory(self):
        """Ensure required data files exist"""
        required_files = [
            "extraction_semiconductors-standard_en-gb.pdf_1748577858.json",
            "extraction_commercial-banks-standard_en-gb.pdf_1748577792.json",
            "matching_semiconductors.json", 
            "matching_commercial-banks.json"
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.data_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            actual_files = [f.name for f in self.data_dir.iterdir() if f.is_file()]
            raise FileNotFoundError(
                f"Missing required data files: {missing_files}\n"
                f"Files found in {self.data_dir}: {actual_files}"
            )
    
    def get_available_industries(self) -> List[str]:
        """Get list of industries with available data"""
        return ["semiconductors", "commercial_banks"]
    
    def load_framework_data(self, industry: str) -> Dict[str, Any]:
        """Load framework data for specific industry"""
        filename_mapping = {
            "semiconductors": "extraction_semiconductors-standard_en-gb.pdf_1748577858.json",
            "commercial_banks": "extraction_commercial-banks-standard_en-gb.pdf_1748577792.json"
        }
        
        if industry not in filename_mapping:
            raise ValueError(f"Industry {industry} not supported. Available: {list(filename_mapping.keys())}")
        
        file_path = self.data_dir / filename_mapping[industry]
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_matching_data(self, industry: str) -> Dict[str, Any]:
        """Load data matching information for specific industry (new structure)"""
        filename_mapping = {
            "semiconductors": "matching_semiconductors.json",
            "commercial_banks": "matching_commercial-banks.json"
        }
        
        if industry not in filename_mapping:
            raise ValueError(f"Industry {industry} not supported")
        
        file_path = self.data_dir / filename_mapping[industry]
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_alignment_data(self, industry: str) -> Dict[str, Any]:
        """Load data alignment information for specific industry (compatibility method)"""
        # Load new matching data and convert to old format for compatibility
        matching_data = self.load_matching_data(industry)
        
        # Convert to old alignment format for backward compatibility
        direct_metrics = matching_data.get("direct_regulatory_metrics", [])
        input_metrics = matching_data.get("input_metrics", [])
        
        # Calculate summary statistics
        total_direct = len(direct_metrics)
        total_input = len(input_metrics)
        total_matches = len([m for m in direct_metrics if m["eurofidai_variable"] != "No Match"])
        total_matches += len([m for m in input_metrics if m["eurofidai_variable"] != "No Match"])
        
        # Calculate average confidence from successful matches
        successful_matches = [m for m in direct_metrics + input_metrics if m["eurofidai_variable"] != "No Match"]
        avg_confidence = sum(m["confidence_score"] for m in successful_matches) / len(successful_matches) if successful_matches else 0
        high_confidence_count = len([m for m in successful_matches if m["confidence_score"] >= 70])
        
        return {
            "coverage_rate": (total_matches / (total_direct + total_input)) * 100 if (total_direct + total_input) > 0 else 0,
            "average_confidence": avg_confidence,
            "high_confidence_count": high_confidence_count,
            "total_alignments": total_matches,
            "matching_summary": matching_data.get("matching_summary", {})
        }
    
    def get_metrics_by_industry(self, industry: str) -> List[Dict[str, Any]]:
        """Get all metrics for specific industry"""
        framework_data = self.load_framework_data(industry)
        return framework_data.get("metrics", [])
    
    def get_calculation_models_by_industry(self, industry: str) -> List[Dict[str, Any]]:
        """Get metrics that have calculation models"""
        metrics = self.get_metrics_by_industry(industry)
        return [m for m in metrics if m.get("model_name") != "n/a" and m.get("model_name")]
    
    def get_industry_summary(self, industry: str) -> Dict[str, Any]:
        """Get summary statistics for industry"""
        framework_data = self.load_framework_data(industry)
        alignment_data = self.load_alignment_data(industry)
        
        return {
            "industry": industry,
            "framework": framework_data.get("framework"),
            "total_metrics": framework_data.get("total_metrics", 0),
            "metrics_with_models": framework_data.get("metrics_with_models", 0),
            "quantitative_metrics": framework_data.get("quantitative_metrics", 0),
            "discussion_metrics": framework_data.get("discussion_metrics", 0),
            "categories": framework_data.get("categories", []),
            "coverage_rate": alignment_data.get("coverage_rate", 0),
            "average_confidence": alignment_data.get("average_confidence", 0),
            "high_confidence_count": alignment_data.get("high_confidence_count", 0)
        }
    
    def load_company_esg_dataset(self, sample_size: int = 1000) -> Optional[pd.DataFrame]:
        """Load company ESG CSV dataset for calculation support"""
        
        csv_path = self.data_dir.parent / "External dataset" / "Raw data with industry.csv"
        
        if not csv_path.exists():
            print(f"Warning: CSV file not found: {csv_path}")
            return None
        
        try:
            self.csv_sample = pd.read_csv(csv_path, nrows=sample_size)
            return self.csv_sample
            
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return None
    
    def get_company_data_by_industry(self, target_industry: str) -> List[str]:
        """Get company names for target industry from CSV dataset"""
        
        if self.csv_sample is None:
            self.load_company_esg_dataset()
        
        if self.csv_sample is None:
            return []
        
        # Find industry and company columns
        industry_col = self._find_column_by_keywords(['industry', 'sector'])
        company_col = self._find_column_by_keywords(['company', 'firm', 'name'])
        
        if not industry_col or not company_col:
            return []
        
        # Filter companies by industry
        if target_industry == "semiconductors":
            industry_keywords = ["semiconductor", "chip", "electronic", "hardware"]
        elif target_industry == "commercial_banks":
            industry_keywords = ["bank", "financial", "finance"]
        else:
            return []
        
        companies = []
        for _, row in self.csv_sample.iterrows():
            industry_value = str(row[industry_col]).lower()
            if any(keyword in industry_value for keyword in industry_keywords):
                companies.append(row[company_col])
        
        return list(set(companies))[:10]  # Return unique companies, limit to 10
    
    def get_company_metric_data(self, company_name: str, metric_keywords: List[str]) -> Dict[str, Any]:
        """Get metric data for specific company to support calculations"""
        
        if self.csv_sample is None:
            self.load_company_esg_dataset()
        
        if self.csv_sample is None:
            return {}
        
        company_col = self._find_column_by_keywords(['company', 'firm', 'name'])
        if not company_col:
            return {}
        
        # Find company rows
        company_rows = self.csv_sample[
            self.csv_sample[company_col].str.contains(company_name, case=False, na=False)
        ]
        
        if company_rows.empty:
            return {}
        
        # Extract relevant metric data
        metric_data = {}
        for keyword in metric_keywords:
            matching_cols = [col for col in self.csv_sample.columns if keyword.lower() in col.lower()]
            for col in matching_cols:
                if not company_rows[col].isna().all():
                    metric_data[col] = company_rows[col].iloc[0]
        
        return metric_data
    
    def get_calculation_input_data(self, model_name: str, company_name: Optional[str] = None) -> Dict[str, float]:
        """Get input data for calculation models from various sources"""
        
        # Default realistic inputs for calculation models
        default_inputs = {
            "Grid Electricity Rate Model": {"grid_electricity": 750, "total_energy": 1000},
            "Renewable Energy Rate Model": {"renewable_energy": 250, "total_energy": 1000},
            "High Stress Water Withdrawal Rate Model": {"high_stress_water": 30, "total_water_withdrawn": 100},
            "High Stress Water Consumption Rate Model": {"high_stress_consumption": 20, "total_water_consumed": 80},
            "Hazardous Waste Recycling Rate Model": {"recycled_waste": 45, "total_hazardous_waste": 60},
            "Personal Data Breach Rate": {"personal_breaches": 3, "total_breaches": 5},
            "Financed Emissions Coverage Rate": {"covered_exposure": 850000, "total_exposure": 1000000},
            "Financed Emissions Coverage Percentage": {"covered_exposure": 850000, "total_exposure": 1000000}
        }
        
        # Try to get company-specific data if available
        if company_name and self.csv_sample is not None:
            company_data = self.get_company_metric_data(company_name, self._get_model_keywords(model_name))
            if company_data:
                return self._convert_to_calculation_inputs(company_data, model_name)
        
        # Return default inputs
        return default_inputs.get(model_name, {"input1": 100, "input2": 200})
    
    def _find_column_by_keywords(self, keywords: List[str]) -> Optional[str]:
        """Find column that matches any of the keywords"""
        if self.csv_sample is None:
            return None
        
        for col in self.csv_sample.columns:
            if any(keyword.lower() in col.lower() for keyword in keywords):
                return col
        return None
    
    def _get_model_keywords(self, model_name: str) -> List[str]:
        """Get relevant keywords for finding data for specific calculation models"""
        keyword_mappings = {
            "Grid Electricity Rate Model": ["electricity", "energy", "power"],
            "Renewable Energy Rate Model": ["renewable", "energy", "solar", "wind"],
            "High Stress Water Withdrawal Rate Model": ["water", "withdrawal", "consumption"],
            "High Stress Water Consumption Rate Model": ["water", "consumption", "usage"],
            "Hazardous Waste Recycling Rate Model": ["waste", "recycling", "hazardous"],
            "Personal Data Breach Rate": ["data", "breach", "security", "privacy"],
            "Financed Emissions Coverage Rate": ["emissions", "finance", "carbon", "scope"],
            "Financed Emissions Coverage Percentage": ["emissions", "finance", "carbon", "scope"]
        }
        
        return keyword_mappings.get(model_name, ["metric", "value"])
    
    def _convert_to_calculation_inputs(self, company_data: Dict, model_name: str) -> Dict[str, float]:
        """Convert company data to calculation inputs format"""
        
        # Simple conversion logic - in production this would be more sophisticated
        inputs = {}
        
        for key, value in company_data.items():
            try:
                if pd.notna(value) and str(value).replace('.', '').replace('-', '').isdigit():
                    inputs[key.lower().replace(' ', '_')] = float(value)
            except:
                continue
        
        return inputs if inputs else {"input1": 100, "input2": 200}
    
    def get_data_sources_summary(self) -> Dict[str, Any]:
        """Get summary of available data sources"""
        
        industries = self.get_available_industries()
        
        summary = {
            "framework_data_sources": len(industries),
            "alignment_data_sources": len(industries),
            "supported_industries": industries,
            "csv_dataset_loaded": self.csv_sample is not None,
            "csv_dataset_size": len(self.csv_sample) if self.csv_sample is not None else 0
        }
        
        return summary 

    # ==================== EXTERNAL DATASET ACCESS ====================
    # Integrated External Data Service functionality for real ESG dataset access
    
    def _ensure_datasets_loaded(self):
        """Ensure datasets are loaded (lazy loading for performance)"""
        if self._datasets_loaded:
            return
        
        print("⚡ Loading datasets on first access...")
        self._load_external_dataset()
        self._datasets_loaded = True
    
    def _ensure_datasets_loaded(self):
        """Ensure datasets are loaded (lazy loading for performance)"""
        if self._datasets_loaded:
            return
        
        print("⚡ Loading datasets on first access...")
        self._load_external_dataset()
        self._datasets_loaded = True
    
    def _load_external_dataset(self):
        """Load the external ESG dataset and initialize configurations"""
        # Initialize demo companies and metric mappings
        self.demo_companies = {
            "semiconductors": {
                "STMicroelectronics NV": "Advanced semiconductor manufacturer with comprehensive ESG data",
                "ON Semiconductor Corp": "Global semiconductor solutions provider"
            },
            "commercial_banks": {
                "Banco Santander SA": "Major European commercial bank with extensive ESG metrics", 
                "Taishin Financial Holding Co Ltd": "Taiwan-based financial services company"
            }
        }
        
        self.metric_mappings = {
            # Greenhouse Gas Emissions
            "CO2DIRECTSCOPE1": "gross_global_scope_1_emissions",
            "CO2INDIRECTSCOPE2": "scope_2_emissions", 
            "CO2INDIRECTSCOPE3": "scope_3_emissions",
            
            # Energy Management
            "ENERGYUSETOTAL": "total_energy_consumed",
            "ELECTRICITYPURCHASED": "percentage_grid_electricity",
            "RENEWENERGYPURCHASED": "percentage_renewable_energy",
            
            # Water Management
            "WATERWITHDRAWALTOTAL": "total_water_withdrawn",
            "WATER_USE_PAI_M10": "percentage_water_high_stress",
            
            # Waste Management
            "WASTETOTAL": "total_waste_generated",
            "HAZARDOUSWASTE": "hazardous_waste_generated",
            "ANALYTICWASTERECYCLINGRATIO": "waste_recycling_rate",
            
            # Workforce Health & Safety
            "EMPLOYEEFATALITIES": "employee_fatalities",
            "TIRTOTAL": "employee_safety_incidents",
            
            # Diversity & Inclusion
            "WOMENEMPLOYEES": "gender_diversity_workforce",
            "TURNOVEREMPLOYEES": "employee_turnover_rate"
        }
        
        # Load industry-specific datasets
        self.industry_datasets = {}
        industry_files = {
            "semiconductors": "data/External dataset/Semiconductors_Eurofidai_EnvironmentData.csv",
            "commercial_banks": "data/External dataset/Commercial_Banks_Eurofidai_EnvironmentData.csv"
        }
        
        try:
            print("📊 Loading industry-specific external datasets...")
            start_time = time.time()
            
            for industry, file_path in industry_files.items():
                if Path(file_path).exists():
                    print(f"📊 Loading {industry} dataset from {file_path}")
                    
                    try:
                        # Load full dataset to ensure all companies are available
                        print(f"📊 Loading full dataset...")
                        self.industry_datasets[industry] = pd.read_csv(
                            file_path,
                            low_memory=False
                        )
                        
                        print(f"✅ {industry} dataset loaded: {len(self.industry_datasets[industry]):,} records")
                    except Exception as e:
                        print(f"❌ Error loading {industry} dataset: {str(e)}")
                        self.industry_datasets[industry] = pd.DataFrame()
                else:
                    print(f"⚠️ Industry dataset not found: {file_path}")
                    self.industry_datasets[industry] = pd.DataFrame()
            
            # Fallback to general dataset if industry-specific files not available
            general_path = Path("data/External dataset/Raw data with industry.csv")
            if not self.industry_datasets and general_path.exists():
                print("📊 Loading general external dataset as fallback...")
                self.external_df = pd.read_csv(general_path, low_memory=False)
                print(f"✅ General dataset loaded: {len(self.external_df):,} records")
            else:
                self.external_df = pd.DataFrame()  # Empty fallback
            
            load_time = time.time() - start_time
            print(f"✅ All external datasets loaded in {load_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Error loading external datasets: {str(e)}")
            self.industry_datasets = {}
            self.external_df = pd.DataFrame()  # Empty fallback
    
    def get_companies_by_industry(self, industry: str) -> List[str]:
        """Get the 20 companies with most records for specific industry using industry-specific datasets"""
        self._ensure_datasets_loaded()  # Lazy loading
        print(f"📊 Looking for companies in industry: {industry}")
        
        # First try to use industry-specific dataset
        if hasattr(self, 'industry_datasets') and industry in self.industry_datasets:
            dataset = self.industry_datasets[industry]
            print(f"📊 Dataset found for {industry}: {len(dataset)} rows")
            if not dataset.empty:
                print(f"📊 Using industry-specific dataset for {industry}")
                try:
                    # Debug: Check columns
                    print(f"📊 Dataset columns: {list(dataset.columns)}")
                    
                    # Get companies with record counts
                    company_counts = dataset['company_name'].dropna().value_counts()
                    print(f"📊 Raw companies count: {len(company_counts)}")
                    
                    # Filter out invalid entries and get top 20 companies by record count
                    valid_companies = []
                    for company_name, count in company_counts.items():
                        if str(company_name) != 'nan' and str(company_name).strip():
                            valid_companies.append((company_name, count))
                    
                    # Sort by record count (descending) and take top 20
                    top_companies = sorted(valid_companies, key=lambda x: x[1], reverse=True)[:20]
                    companies = [company for company, count in top_companies]
                    
                    print(f"📊 Filtered companies count: {len(companies)}")
                    print(f"📊 First 5 companies: {companies[:5]}")
                    print(f"📊 Top company record counts: {[(c, count) for c, count in top_companies[:5]]}")
                    
                    print(f"📊 Found {len(companies)} companies with most records in {industry} dataset")
                    return companies
                    
                except Exception as e:
                    print(f"⚠️ Error reading industry-specific dataset: {str(e)}")
                    import traceback
                    traceback.print_exc()
        else:
            print(f"📊 No industry-specific dataset found for {industry}")
            if hasattr(self, 'industry_datasets'):
                print(f"📊 Available datasets: {list(self.industry_datasets.keys())}")
        
        # No real data available - return error instead of demo companies
        print(f"❌ No real data available for {industry}")
        return self._create_error_response(
            "NO_REAL_DATA_AVAILABLE",
            f"No real companies found for industry '{industry}'",
            {
                "industry": industry,
                "data_policy": "No demo/fake data provided",
                "available_industries": list(self.industry_datasets.keys()) if hasattr(self, 'industry_datasets') else [],
                "suggestion": "Check available industries or verify dataset loading"
            }
        )
    
    def get_available_years(self, company_name: str) -> List[str]:
        """Get available years for company using industry-specific datasets"""
        print(f"📊 Getting years for company: {company_name}")
        
        # First try to find the company in industry-specific datasets
        if hasattr(self, 'industry_datasets'):
            for industry, dataset in self.industry_datasets.items():
                if not dataset.empty:
                    # Check if company exists in this industry dataset
                    company_rows = dataset[
                        dataset['company_name'].str.contains(company_name, case=False, na=False, regex=False)
                    ]
                    
                    if not company_rows.empty:
                        print(f"📊 Found {company_name} in {industry} dataset")
                        
                        # Extract years from data
                        years = []
                        if 'metric_year' in company_rows.columns:
                            # Convert years to string and clean them
                            year_values = company_rows['metric_year'].dropna().unique()
                            years = []
                            for year in year_values:
                                try:
                                    # Handle different year formats
                                    if pd.isna(year):
                                        continue
                                    year_str = str(year)
                                    if '-' in year_str:
                                        # Extract year from date format like "2023-12-31"
                                        year_str = year_str.split('-')[0]
                                    years.append(year_str)
                                except:
                                    continue
                            
                            years = sorted(list(set(years)))  # Remove duplicates and sort
                        
                        if not years:
                            # Default to common reporting years if no valid years found
                            years = ["2023", "2022", "2021"]
                        
                        print(f"📊 Found {len(years)} years for {company_name}: {years}")
                        return years
        
        # Fallback to general dataset if industry-specific not found
        if self.external_df is not None and not self.external_df.empty:
            print(f"📊 Falling back to general dataset for {company_name}")
            try:
                # Enhanced fuzzy company matching
                company_matches = self._fuzzy_match_company(company_name)
                
                if not company_matches:
                    print(f"⚠️ Company '{company_name}' not found in general dataset")
                    return ["2023", "2022", "2021"]  # Default years
                
                if len(company_matches) > 1:
                    print(f"⚠️ Multiple companies found: {company_matches[:3]}")
                    # Use the first match
                    matched_company = company_matches[0]
                else:
                    matched_company = company_matches[0]
                
                # Get years for the matched company
                company_rows = self.external_df[
                    self.external_df['company_name'].str.contains(matched_company, case=False, na=False)
                ]
                
                if company_rows.empty:
                    print(f"⚠️ No data found for company '{matched_company}'")
                    return ["2023", "2022", "2021"]  # Default years
                
                # Extract years from data
                years = []
                if 'metric_year' in company_rows.columns:
                    years = sorted(company_rows['metric_year'].dropna().unique().astype(str).tolist())
                else:
                    # Default to common reporting years
                    years = ["2023", "2022", "2021"]
                
                return years
                
            except Exception as e:
                print(f"❌ Error in general dataset search: {str(e)}")
        
        # Final fallback
        print(f"📊 Using default years for {company_name}")
        return ["2023", "2022", "2021"]

    def get_metric_value(self, company_name: str, year: str, metric_name: str) -> Optional[float]:
        """Get metric value for a specific company and year from external dataset"""
        print(f"📊 Getting metric value: {metric_name} for {company_name} ({year})")

        # Ensure datasets are loaded (lazy loading)
        self._ensure_datasets_loaded()

        try:
            # Check if metric_name is already a dataset variable (uppercase, specific patterns)
            # If it looks like a dataset variable, use it directly
            is_dataset_variable = (
                metric_name.isupper() and 
                any(prefix in metric_name for prefix in ['ENERGY', 'RENEW', 'CO2', 'WATER', 'WASTE', 'TARGET'])
            )
            
            if is_dataset_variable:
                # Use directly as dataset variable without mapping
                external_variable = metric_name
                print(f"📊 Using as direct dataset variable: {external_variable}")
            else:
                # Apply mapping for metric names
                external_variable = self._map_sasb_to_external(metric_name)
                print(f"📊 Mapped {metric_name} -> {external_variable}")

            # Find the company in industry-specific datasets
            company_dataset = None
            matched_company = None
            industry_used = None
            
            if hasattr(self, 'industry_datasets'):
                for industry, dataset in self.industry_datasets.items():
                    if not dataset.empty:
                        # Look for exact match first
                        exact_matches = dataset[dataset['company_name'] == company_name]
                        if not exact_matches.empty:
                            company_dataset = dataset
                            matched_company = company_name
                            industry_used = industry
                            break
                        
                        # Try fuzzy matching
                        fuzzy_matches = dataset[
                            dataset['company_name'].str.contains(company_name, case=False, na=False, regex=False)
                        ]
                        if not fuzzy_matches.empty:
                            company_dataset = dataset
                            matched_company = fuzzy_matches['company_name'].iloc[0]
                            industry_used = industry
                            break
            
            # Fallback to general dataset if not found in industry datasets
            if company_dataset is None and hasattr(self, 'external_df') and self.external_df is not None:
                print(f"📊 Falling back to general dataset for {company_name}")
                company_dataset = self.external_df
                # Enhanced fuzzy company matching
                company_matches = self._fuzzy_match_company(company_name)
                if company_matches:
                    matched_company = company_matches[0]
                else:
                    print(f"❌ Company not found: {company_name}")
                    return None
            
            if company_dataset is None or matched_company is None:
                print(f"❌ No dataset found for company: {company_name}")
                return None
            
            print(f"📊 Found {matched_company} in {industry_used or 'general'} dataset")
            
            # Get company data
            if industry_used:
                # Use exact match for industry datasets
                company_rows = company_dataset[company_dataset['company_name'] == matched_company]
            else:
                # Use fuzzy match for general dataset
                company_rows = company_dataset[
                    company_dataset['company_name'].str.contains(matched_company, case=False, na=False)
                ]
            
            if company_rows.empty:
                print(f"❌ No data rows found for: {matched_company}")
                return None
            
            # Filter by year if available (handle both '2023' and '2023-12-31' formats)
            if 'metric_year' in company_rows.columns:
                # Try exact match first
                year_filtered = company_rows[company_rows['metric_year'].astype(str) == str(year)]
                
                # If no exact match, try partial match for date formats like '2023-12-31'
                if year_filtered.empty:
                    year_filtered = company_rows[company_rows['metric_year'].astype(str).str.startswith(str(year))]
                
                if not year_filtered.empty:
                    company_rows = year_filtered
                    print(f"✅ Using {year} data for {matched_company}")
                else:
                    print(f"⚠️ Year {year} not available for {matched_company}, using latest data")
            
            # Use the external_variable that was determined earlier
            if not external_variable:
                print(f"❌ Cannot determine dataset variable for metric '{metric_name}'")
                return None
            
            print(f"📊 Looking for dataset variable: {external_variable}")
            
            # For industry datasets, look in the metric_name column for direct matches
            if industry_used:
                # Check if this is a direct match in metric_name column
                metric_rows = company_rows[company_rows['metric_name'] == external_variable]
                if not metric_rows.empty and 'metric_value' in metric_rows.columns:
                    value = metric_rows['metric_value'].iloc[0]
                    if not pd.isna(value):
                        print(f"✅ Found direct metric value: {value}")
                        
                        # Check metric unit to determine proper value interpretation
                        metric_unit = metric_rows['metric_unit'].iloc[0] if 'metric_unit' in metric_rows.columns else None
                        print(f"📊 Metric unit: {metric_unit}")
                        
                        # Handle Yes/No metrics
                        if metric_unit and str(metric_unit).lower() in ['yes/no', 'boolean']:
                            try:
                                numeric_value = float(value)
                                if numeric_value == 1.0:
                                    return "Yes"
                                elif numeric_value == 0.0:
                                    return "No"
                                else:
                                    return f"Unknown ({numeric_value})"
                            except (ValueError, TypeError):
                                return str(value)
                        
                        # Handle percentage metrics
                        elif metric_unit and '%' in str(metric_unit).lower():
                            try:
                                return float(value)
                            except (ValueError, TypeError):
                                print(f"⚠️ Non-numeric percentage value: {value}")
                                return None
                        
                        # Handle numeric metrics
                        else:
                            try:
                                return float(value)
                            except (ValueError, TypeError):
                                print(f"⚠️ Non-numeric value found: {value}")
                                return None

            # Fallback: Find matching columns (for general dataset)
            matching_columns = [col for col in company_rows.columns 
                              if external_variable.lower() in col.lower()]
            
            if not matching_columns:
                print(f"❌ No matching columns found for: {external_variable}")
                print(f"📊 Available columns: {list(company_rows.columns)}")
                return None
            
            # Get value from the best matching column
            best_column = matching_columns[0]
            value = company_rows[best_column].iloc[0]
            
            if pd.isna(value):
                print(f"❌ No real data found for: {external_variable} ({matched_company}, {year})")
                return None
            
            # Convert to float if possible
            try:
                return float(value)
            except (ValueError, TypeError):
                print(f"⚠️ Non-numeric value found: {value}")
                return None
                
        except Exception as e:
            print(f"❌ Error retrieving metric value: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def _map_sasb_to_external(self, sasb_metric: str) -> str:
        """Map SASB metric names to external dataset variables"""
        
        # Clean metric name for comparison
        clean_metric = sasb_metric.lower().replace(' ', '_').replace('-', '_')
        
        # Direct mappings
        direct_mappings = {
            "total_energy_consumed": "ENERGYUSETOTAL",
            "energy_consumed": "ENERGYUSETOTAL", 
            "percentage_grid_electricity": "ELECTRICITYPURCHASED",
            "grid_electricity": "ELECTRICITYPURCHASED",
            "percentage_renewable_energy": "RENEWENERGYPURCHASED",
            "renewable_energy": "RENEWENERGYPURCHASED",
            "gross_global_scope_1_emissions": "CO2DIRECTSCOPE1",
            "scope_1_emissions": "CO2DIRECTSCOPE1",
            "scope1_emission": "CO2DIRECTSCOPE1",  # Added for GHG calculation
            "scope_1_emissions_strategy": "TARGETS_EMISSIONS",  # Yes/No metric
            "scope_2_emissions": "CO2INDIRECTSCOPE2", 
            "scope2_emission": "CO2INDIRECTSCOPE2",  # Added for GHG calculation
            "scope_3_emissions": "CO2INDIRECTSCOPE3",
            "revenue": "revt",  # Added for GHG calculation - maps to financial dataset
            "total_water_withdrawn": "WATERWITHDRAWALTOTAL",
            "water_withdrawn": "WATERWITHDRAWALTOTAL",
            "total_waste_generated": "WASTETOTAL",
            "waste_generated": "WASTETOTAL",
            "hazardous_waste": "HAZARDOUSWASTE",
            "employee_fatalities": "EMPLOYEEFATALITIES",
            "safety_incidents": "TIRTOTAL",
            # GHG Emission Intensity related metrics
            "ghg_emission_intensity": "calculated",  # This is a calculated metric
            "ghgemissionintensity": "calculated"  # Alternative naming
        }
        
        # Check direct mappings first
        if clean_metric in direct_mappings:
            return direct_mappings[clean_metric]
        
        # Keyword-based fallback mappings
        keyword_mappings = {
            "energy": "ENERGYUSETOTAL",
            "electricity": "ELECTRICITYPURCHASED", 
            "renewable": "RENEWENERGYPURCHASED",
            "emissions": "CO2DIRECTSCOPE1",
            "carbon": "CO2DIRECTSCOPE1",
            "water": "WATERWITHDRAWALTOTAL",
            "waste": "WASTETOTAL",
            "fatalities": "EMPLOYEEFATALITIES",
            "safety": "TIRTOTAL"
        }
        
        for keyword, mapping in keyword_mappings.items():
            if keyword in clean_metric:
                return mapping
        
        # Default fallback
        return "ENERGYUSETOTAL"

    def _get_demo_metric_value(self, metric_name: str) -> float:
        """Get realistic demo values for metrics"""
        demo_values = {
            "Total Energy Consumed": 2847000.0,  # MWh - realistic for large company
            "Percentage Grid Electricity": 85.2,  # Percentage
            "Percentage Renewable Energy": 23.8,  # Percentage
            "Gross Global Scope 1 Emissions": 145000.0,  # tCO2e
            "Scope 2 Emissions": 89000.0,  # tCO2e  
            "Scope 3 Emissions": 1250000.0,  # tCO2e
            "Total Water Withdrawn": 850000.0,  # cubic meters
            "Total Waste Generated": 45000.0,  # metric tons
            "Hazardous Waste": 1200.0,  # metric tons
            "Employee Fatalities": 0.0,  # count
            "Safety Incidents": 15.0,  # count
        }
        
        # Find closest match by keywords
        metric_lower = metric_name.lower()
        for key, value in demo_values.items():
            if any(word in metric_lower for word in key.lower().split()):
                return value
        
        # Default value
        return 1000.0

    def get_calculation_inputs(self, company_name: str, year: str, required_metrics: List[str]) -> Dict[str, float]:
        """Get input data for calculation models from external dataset"""
        inputs = {}
        
        for metric in required_metrics:
            value = self.get_metric_value(company_name, year, metric)
            if value is not None:
                inputs[metric.lower().replace(' ', '_')] = value
        
        return inputs

    # ==================== ADDITIONAL API SUPPORT METHODS ====================
    
    def get_available_companies(self, industry: str = None) -> Dict[str, Any]:
        """Get available companies for selection, optionally filtered by industry - REAL DATA ONLY"""
        self._ensure_datasets_loaded()  # Lazy loading
        if self.external_df is None or len(self.external_df) == 0:
            return {"error": "External dataset not loaded", "available_companies": {}, "total_companies": 0}
        
        try:
            companies_by_industry = {}
            all_companies = set()
            
            if hasattr(self, 'industry_datasets'):
                # Use industry-specific datasets
                for industry_name, dataset in self.industry_datasets.items():
                    if not dataset.empty and 'company_name' in dataset.columns:
                        industry_companies = dataset['company_name'].unique().tolist()
                        companies_by_industry[industry_name] = {
                            "companies": industry_companies[:20],  # Limit to 20 for performance
                            "total_count": len(industry_companies),
                            "dataset_size": len(dataset)
                        }
                        all_companies.update(industry_companies)
            
            # Filter by specific industry if requested
            if industry and industry in companies_by_industry:
                return companies_by_industry[industry]
            elif industry:
                return {"error": f"Industry {industry} not found", "available_companies": [], "total_companies": 0}
            
            return {
                "companies_by_industry": companies_by_industry,
                "all_companies": list(all_companies)[:50],  # Limit for API response
                "total_companies": len(all_companies),
                "industries_available": list(companies_by_industry.keys()),
                "data_policy": "Real company data only - no synthetic entries"
            }
            
        except Exception as e:
            return self._create_error_response(
                "EXTERNAL_DATASET_ACCESS_FAILED",
                f"Error accessing company data: {str(e)}",
                {"industry_filter": industry}
            )

    def check_data_availability(self, company_name: str, year: str, metrics: List[str]) -> Dict[str, Any]:
        """Check data availability for specific company, year, and metrics"""
        try:
            available_metrics = []
            unavailable_metrics = []
            
            for metric in metrics:
                # Try to get the metric value
                value = self.get_metric_value(company_name, year, metric)
                
                if value is not None:
                    available_metrics.append({
                        "metric_name": metric,
                        "value": value,
                        "status": "available"
                    })
                else:
                    unavailable_metrics.append({
                        "metric_name": metric,
                        "status": "unavailable",
                        "reason": "No data found in external dataset"
                    })
            
            coverage_rate = len(available_metrics) / len(metrics) if metrics else 0
            
            return {
                "status": "checked",
                "company_name": company_name,
                "year": year,
                "total_metrics_checked": len(metrics),
                "available_metrics": available_metrics,
                "unavailable_metrics": unavailable_metrics,
                "coverage_rate": coverage_rate,
                "coverage_percentage": f"{coverage_rate * 100:.1f}%",
                "suggestion": "Good data coverage" if coverage_rate > 0.7 else "Limited data available"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error checking data availability: {str(e)}",
                "company_name": company_name,
                "year": year
            }

    def get_available_years(self, company_name: str) -> List[str]:
        """Get available years for a specific company"""
        try:
            years = set()
            
            # Check industry-specific datasets
            if hasattr(self, 'industry_datasets'):
                for industry, dataset in self.industry_datasets.items():
                    if not dataset.empty and 'company_name' in dataset.columns:
                        company_rows = dataset[dataset['company_name'] == company_name]
                        if not company_rows.empty and 'metric_year' in dataset.columns:
                            company_years = company_rows['metric_year'].dropna().unique()
                            for year in company_years:
                                # Extract year from date strings like "2023-12-31"
                                year_str = str(year)
                                if '-' in year_str:
                                    year_str = year_str.split('-')[0]
                                years.add(year_str)
            
            # Fallback years if none found
            if not years:
                years = {"2023", "2022", "2021"}
                
            return sorted(list(years), reverse=True)
            
        except Exception as e:
            print(f"⚠️ Error getting years for {company_name}: {e}")
            return ["2023", "2022", "2021"]

    def get_company_industry(self, company_name: str) -> str:
        """Get the industry for a specific company"""
        try:
            if hasattr(self, 'industry_datasets'):
                for industry, dataset in self.industry_datasets.items():
                    if not dataset.empty and 'company_name' in dataset.columns:
                        if company_name in dataset['company_name'].values:
                            return industry
            
            # Fallback determination based on company name patterns
            company_lower = company_name.lower()
            if any(keyword in company_lower for keyword in ['bank', 'financial', 'credit']):
                return "commercial_banks"
            elif any(keyword in company_lower for keyword in ['semiconductor', 'micro', 'tech', 'electronics']):
                return "semiconductors"
            else:
                return "semiconductors"  # Default fallback
                
        except Exception as e:
            print(f"⚠️ Error determining industry for {company_name}: {e}")
            return "semiconductors"



    def get_calculation_inputs(self, company_name: str, year: str, required_metrics: List[str]) -> Dict[str, float]:
        """Get input data for calculation models from external dataset"""
        inputs = {}
        
        for metric in required_metrics:
            value = self.get_metric_value(company_name, year, metric)
            if value is not None:
                inputs[metric.lower().replace(' ', '_')] = value
        
        return inputs

    def get_all_companies(self) -> Dict[str, List[str]]:
        """Get all companies organized by industry"""
        self._ensure_datasets_loaded()

        companies_by_industry = {}

        if hasattr(self, 'industry_datasets'):
            for industry, dataset in self.industry_datasets.items():
                if not dataset.empty and 'company_name' in dataset.columns:
                    # Get unique companies, sorted by record count
                    company_counts = dataset['company_name'].dropna().value_counts()
                    companies = [comp for comp in company_counts.index if str(comp).strip()]
                    companies_by_industry[industry] = companies[:20]  # Top 20 companies

        return companies_by_industry

    def get_company_industry(self, company_name: str) -> Optional[str]:
        """Get the industry for a given company name"""
        self._ensure_datasets_loaded()

        if not hasattr(self, 'industry_datasets'):
            return None

        # Search for company in each industry dataset
        for industry, dataset in self.industry_datasets.items():
            if not dataset.empty and 'company_name' in dataset.columns:
                # Check if company exists in this industry
                company_exists = dataset['company_name'].str.contains(
                    company_name, case=False, na=False, regex=False
                ).any()

                if company_exists:
                    print(f"📊 Found {company_name} in {industry}")
                    return industry

        print(f"⚠️ Company {company_name} not found in any industry dataset")
        return None

    @property
    def error_categories(self) -> Dict[str, Dict[str, str]]:
        """Error categories for standardized error responses"""
        return {
            "EXTERNAL_DATASET_ACCESS_FAILED": {
                "user_message": "Unable to access external dataset",
                "suggestion": "Please try again or contact support"
            },
            "DATASET_VARIABLE_MAPPING_FAILED": {
                "user_message": "Cannot map metric to dataset variable", 
                "suggestion": "Check metric name and try again"
            },
            "COMPANY_NOT_FOUND": {
                "user_message": "Company not found in dataset",
                "suggestion": "Check company name spelling"
            },
            "DATA_NOT_AVAILABLE": {
                "user_message": "Data not available for requested parameters",
                "suggestion": "Try different company or year"
            }
        }

    def _create_error_response(self, error_category: str, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create standardized error response with user-friendly messages"""
        error_info = self.error_categories.get(error_category, {
            "user_message": "Unknown error occurred",
            "suggestion": "Please try again or contact support"
        })
        
        return {
            "error": True,
            "error_category": error_category,
            "user_message": error_info["user_message"],
            "suggestion": error_info["suggestion"],
            "technical_message": message,
            "context": context,
            "timestamp": time.time()
        }