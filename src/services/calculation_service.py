# src/services/calculation_service.py
from typing import Dict, Any, List, Optional
import time
import json
from pathlib import Path
import os

class CalculationService:
    """Enhanced ESG Calculation Service with integrated memory management"""
    
    def __init__(self, external_data_service=None, kg_service=None):
        self.external_data_service = external_data_service
        self.kg_service = kg_service
        self.supported_models = {
            "Grid Electricity Rate Model": {
                "description": "Percentage of energy consumed from grid electricity",
                "formula": "(grid_electricity / total_energy) * 100",
                "inputs": ["grid_electricity", "total_energy"],
                "output_unit": "percentage"
            },
            "Renewable Energy Rate Model": {
                "description": "Percentage of energy consumed from renewable sources",
                "formula": "(renewable_energy / total_energy) * 100", 
                "inputs": ["renewable_energy", "total_energy"],
                "output_unit": "percentage"
            },
            "High Stress Water Withdrawal Rate Model": {
                "description": "Percentage of water withdrawn in high stress regions",
                "formula": "(high_stress_water / total_water_withdrawn) * 100",
                "inputs": ["high_stress_water", "total_water_withdrawn"],
                "output_unit": "percentage"
            },
            "Hazardous Waste Recycling Rate Model": {
                "description": "Percentage of hazardous waste recycled",
                "formula": "(recycled_hazardous_waste / total_hazardous_waste) * 100",
                "inputs": ["recycled_hazardous_waste", "total_hazardous_waste"],
                "output_unit": "percentage"
            }
        }
        
        # Integrated memory management (from CalculationMemoryService)
        self.calculation_memory = {}
        self.session_memory = {}
        self.companies_cache = {}
        self.frameworks_cache = {}
        self.memory_file = "data/calculation_memory.json"
        self.memory = self._load_memory()
    
    # ==================== MEMORY MANAGEMENT METHODS ====================
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load calculation memory from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "sessions": {},
            "completed_calculations": {},
            "metrics_status": {}
        }
    
    def _save_memory(self):
        """Save calculation memory to file"""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def store_calculation(self, company_name: str, year: str, calculation_result: Dict[str, Any]):
        """Store calculation result in memory with correct signature"""
        try:
            memory_key = f"{company_name}:{year}"
            
            if memory_key not in self.calculation_memory:
                self.calculation_memory[memory_key] = {}
            
            # Extract metric name from calculation result
            metric_name = calculation_result.get('metric_name', 'unknown_metric')
            
            self.calculation_memory[memory_key][metric_name] = {
                'result': calculation_result,
                'timestamp': time.time(),
                'cached': True
            }
            
            print(f"💾 Stored calculation in memory: {metric_name} for {company_name} ({year})")
            
        except Exception as e:
            print(f"⚠️ Failed to store calculation in memory: {str(e)}")
    
    def get_calculation(self, company_name: str, year: str, metric_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve calculation result from memory"""
        try:
            memory_key = f"{company_name}:{year}"
            
            if memory_key in self.calculation_memory:
                if metric_name in self.calculation_memory[memory_key]:
                    cached_entry = self.calculation_memory[memory_key][metric_name]
                    
                    # Check if cache is still valid (24 hours)
                    if time.time() - cached_entry['timestamp'] < 86400:
                        print(f"🎯 Retrieved cached calculation: {metric_name}")
                        return cached_entry['result']
                    else:
                        # Remove expired cache
                        del self.calculation_memory[memory_key][metric_name]
                        print(f"⏰ Expired cache removed for: {metric_name}")
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error retrieving from cache: {str(e)}")
            return None
    
    def start_calculation_session(self, session_id: str, company_name: str, year: str, industry: str) -> str:
        """Start a new calculation session"""
        session_data = {
            "session_id": session_id,
            "company_name": company_name,
            "year": year,
            "industry": industry,
            "started_at": time.time(),
            "calculated_metrics": {},
            "status": "active"
        }
        
        self.memory["sessions"][session_id] = session_data
        self._save_memory()
        return session_id
    
    def record_calculation_result(self, session_id: str, metric_code: str, category: str, 
                                 calculation_result: Dict[str, Any]):
        """Record a completed calculation"""
        if session_id not in self.memory["sessions"]:
            return False
            
        session = self.memory["sessions"][session_id]
        
        # Store the calculation result
        metric_key = f"{metric_code}_{category}"
        session["calculated_metrics"][metric_key] = {
            "metric_code": metric_code,
            "category": category,
            "result": calculation_result,
            "calculated_at": time.time(),
            "status": "complete"
        }
        
        # Update global metrics status
        company_key = f"{session['company_name']}_{session['year']}"
        if company_key not in self.memory["metrics_status"]:
            self.memory["metrics_status"][company_key] = {}
            
        self.memory["metrics_status"][company_key][metric_code] = {
            "status": "complete",
            "category": category,
            "last_calculated": time.time(),
            "session_id": session_id
        }
        
        self._save_memory()
        return True
    
    def get_session_calculations(self, session_id: str) -> Dict[str, Any]:
        """Get all calculations for a session"""
        if session_id not in self.memory["sessions"]:
            return {"calculated_metrics": {}, "status": "not_found"}
            
        session = self.memory["sessions"][session_id]
        return {
            "session_id": session_id,
            "calculated_metrics": session["calculated_metrics"],
            "total_calculated": len(session["calculated_metrics"]),
            "status": session["status"],
            "company_info": {
                "company_name": session["company_name"],
                "year": session["year"],
                "industry": session["industry"]
            }
        }
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of calculation memory"""
        total_sessions = len(self.memory["sessions"])
        total_companies = len(set([
            f"{s['company_name']}_{s['year']}" 
            for s in self.memory["sessions"].values()
        ]))
        
        active_sessions = len([s for s in self.memory["sessions"].values() if s["status"] == "active"])
        
        return {
            "total_sessions": total_sessions,
            "total_companies": total_companies,
            "active_sessions": active_sessions,
            "cached_calculations": len(self.calculation_memory),
            "memory_size_mb": self._get_memory_size_mb()
        }
    
    def _get_memory_size_mb(self) -> float:
        """Estimate memory usage in MB"""
        import sys
        memory_size = sys.getsizeof(self.memory) + sys.getsizeof(self.calculation_memory)
        return memory_size / (1024 * 1024)

    # ==================== EXISTING CALCULATION METHODS ====================
    
    def _check_metric_data_availability(self, metric_name: str, cq4_result: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a metric has corresponding dataset variables in alignment data"""
        # This would ideally query the RDF store for alignment data
        # For now, we'll use a heuristic approach
        
        metric_code = cq4_result.get("metric_code", "")
        
        # Common dataset variable mappings based on your alignment data
        known_mappings = {
            "Total Energy Consumed": ["ENERGYUSETOTAL", "TOTALENERGYCONS"],
            "Gross Global Scope 1 Emissions": ["SCOPE1EMISSIONS", "CO2EMISSIONS"],
            "Perfluorinated Compounds Emissions": ["PFCEMISSIONS", "FLUORINATEDEMISSIONS"],
            "Total Water Withdrawn": ["WATERWITHDRAWALTOTAL", "TOTALWATERUSE"],
            "Total Water Consumed": ["WATERCONSUMPTIONTOTAL", "WATERUSE"],
            "Hazardous Waste Amount": ["HAZARDOUSWASTE", "WASTEGENERATED"],
            "Percentage Grid Electricity": ["ELECTRICITYPURCHASED", "GRIDELECTRICITY"],
            "Percentage Renewable Energy": ["TRANALYTICRENEWENERGYUSE", "RENEWABLEENERGY"]
        }
        
        dataset_variables = known_mappings.get(metric_name, [])
        has_variable = len(dataset_variables) > 0
        
        return {
            "metric_name": metric_name,
            "metric_code": metric_code,
            "has_dataset_variable": has_variable,
            "dataset_variables": dataset_variables,
            "availability_reason": "Found in known mappings" if has_variable else "No known dataset variable mapping"
        }
    
    def _check_model_input_availability(self, required_inputs: List[str], industry: str) -> Dict[str, Dict[str, Any]]:
        """Check availability of all model inputs"""
        availability = {}
        
        for input_var in required_inputs:
            # Check if this input can be resolved to a metric or direct dataset variable
            metric_name = self._resolve_input_metric_name(input_var, industry)
            
            if metric_name:
                # Input maps to a metric - check that metric's availability
                mock_cq4_result = {"metric_code": input_var}
                metric_availability = self._check_metric_data_availability(metric_name, mock_cq4_result)
                available = metric_availability["has_dataset_variable"]
            else:
                # Direct dataset variable - check if we have mapping
                external_mapping = self._get_external_mapping_for_input(input_var, "")
                available = external_mapping != input_var.upper()  # Has specific mapping
            
            availability[input_var] = {
                "available": available,
                "metric_name": metric_name,
                "resolution_method": "metric_based" if metric_name else "direct_dataset"
            }
        
        return availability
    
    def _resolve_input_metric_name(self, input_variable: str, industry: str) -> Optional[str]:
        """Map calculation input variable to actual metric name, avoiding circular dependencies"""
        
        # For cascading calculations, we should prefer direct dataset variable lookups 
        # over recursive metric resolution to avoid circular dependencies
        
        # Only resolve to metrics for inputs that are fundamentally different metrics
        # Most inputs should use direct external dataset lookups
        variable_to_metric_mapping = {
            # Only map to metrics when it's a different metric entirely
            "total_water_withdrawn": "Total Water Withdrawn",
            "total_water_consumed": "Total Water Consumed", 
            "total_hazardous_waste": "Hazardous Waste Amount",
            "hazardous_waste": "Hazardous Waste Amount",
            
            # All energy-related inputs should use direct external dataset lookups
            # to avoid circular dependencies
            "grid_electricity": None,    # ELECTRICITYPURCHASED
            "total_energy": None,        # ENERGYUSETOTAL  
            "renewable_energy": None,    # TRANALYTICRENEWENERGYUSE
            
            # Water stress inputs - use direct dataset lookups
            "high_stress_water": None,              # WATER_USE_PAI_M10
            "high_stress_consumption": None,        # WATER_USE_PAI_M10
            
            # Waste inputs - use direct dataset lookups  
            "recycled_waste": None,                 # ANALYTICWASTERECYCLINGRATIO
            
            # Banking inputs - use direct dataset lookups
            "personal_breaches": None,              # DATA_BREACHES_PERSONAL
            "total_breaches": None,                 # DATA_BREACHES_TOTAL
            "covered_exposure": None,               # FINANCED_EMISSIONS_COVERED
            "total_exposure": None                  # TOTAL_GROSS_EXPOSURE
        }
        
        return variable_to_metric_mapping.get(input_variable)
    
    def _get_external_mapping_for_input(self, input_var: str, model_name: str) -> str:
        """Get external dataset mapping for a model input variable"""
        # Use the supported models mapping if available
        if model_name in self.supported_models:
            external_mappings = self.supported_models[model_name].get("external_mappings", {})
            if input_var in external_mappings:
                return external_mappings[input_var]
        
        # Fallback to common mappings
        common_mappings = {
            "grid_electricity": "RENEWENERGYPURCHASED",  # Use available variable instead of ELECTRICITYPURCHASED
            "total_energy": "ENERGYUSETOTAL", 
            "renewable_energy": "RENEWENERGYPURCHASED",  # Fixed to use absolute energy values
            "total_water_withdrawn": "WATERWITHDRAWALTOTAL",
            "high_stress_water": "WATER_USE_PAI_M10",
            "total_water_consumed": "WATERWITHDRAWALTOTAL",  # Same as withdrawal in dataset
            "hazardous_waste": "HAZARDOUSWASTE",
            "recycled_waste": "ANALYTICWASTERECYCLINGRATIO",
            "total_hazardous_waste": "HAZARDOUSWASTE"
        }
        
        return common_mappings.get(input_var, input_var.upper())
    
    def _get_qualitative_value(self, company_name: str, year: str, metric_mapping: str) -> Any:
        """Get qualitative value from external dataset - real data only"""
        # This would need to be implemented with your external data service
        # For now, return clear indication that qualitative data needs real implementation
        return {
            "status": "not_implemented",
            "message": "Qualitative data access not yet implemented with real dataset",
            "metric_mapping": metric_mapping,
            "company": company_name,
            "year": year,
            "data_policy": "No demo/fake data provided"
        }
    
    def get_calculable_metrics(self, industry: str) -> Dict[str, Any]:
        """Get list of metrics that can actually be calculated based on data availability"""
        if not self.external_data_service:
            return {"error": "External data service not available"}
        
        # Get all metrics for the industry
        all_metrics = self.external_data_service.cq3_metrics_by_category(industry, "all_categories")
        calculable_metrics = []
        skipped_metrics = []
        
        for category_data in all_metrics.get("categories", []):
            for metric in category_data.get("metrics", []):
                metric_name = metric.get("metric_name")
                
                # Quick availability check
                cq4_result = self.kg_service.cq4_metric_calculation_method(industry, metric_name)
                calculation_method = cq4_result.get("measurement_method")
                
                if calculation_method == "direct_measurement":
                    data_availability = self._check_metric_data_availability(metric_name, cq4_result)
                    if data_availability["has_dataset_variable"]:
                        calculable_metrics.append({
                            "metric_name": metric_name,
                            "calculation_method": "direct_measurement",
                            "data_availability": "available"
                        })
                    else:
                        skipped_metrics.append({
                            "metric_name": metric_name,
                            "reason": "No dataset variable mapping",
                            "calculation_method": "direct_measurement"
                        })
                
                elif calculation_method == "calculation_model":
                    model_name = cq4_result.get("model_name")
                    if model_name and model_name != "n/a":
                        try:
                            cq5_result = self.kg_service.cq5_model_input_datapoints(industry, model_name, self)
                            required_inputs = cq5_result.get("required_inputs", [])
                            input_availability = self._check_model_input_availability(required_inputs, industry)
                            
                            all_available = all(input_availability[inp]["available"] for inp in input_availability)
                            
                            if all_available:
                                calculable_metrics.append({
                                    "metric_name": metric_name,
                                    "calculation_method": "calculation_model",
                                    "model_name": model_name,
                                    "data_availability": "available"
                                })
                            else:
                                unavailable = [inp for inp in input_availability if not input_availability[inp]["available"]]
                                skipped_metrics.append({
                                    "metric_name": metric_name,
                                    "reason": f"Missing inputs: {unavailable}",
                                    "calculation_method": "calculation_model",
                                    "model_name": model_name
                                })
                        except:
                            skipped_metrics.append({
                                "metric_name": metric_name,
                                "reason": "Model details not available",
                                "calculation_method": "calculation_model"
                            })
        
        return {
            "industry": industry,
            "calculable_metrics": calculable_metrics,
            "skipped_metrics": skipped_metrics,
            "summary": {
                "total_calculable": len(calculable_metrics),
                "total_skipped": len(skipped_metrics),
                "calculability_ratio": len(calculable_metrics) / (len(calculable_metrics) + len(skipped_metrics)) if (len(calculable_metrics) + len(skipped_metrics)) > 0 else 0
            }
        }
    
    def _get_demo_value_for_metric(self, metric_name: str) -> float:
        """Get demo value for a specific metric"""
        demo_values = {
            "Total Energy Consumed": 1250000.0,  # MWh
            "Gross Global Scope 1 Emissions": 125000.0,  # tCO2e
            "Perfluorinated Compounds Emissions": 2500.0,  # tCO2e
            "Total Water Withdrawn": 450000.0,  # m³
            "Total Water Consumed": 425000.0,  # m³
            "Hazardous Waste Amount": 1200.0,  # tonnes
            "Data Breaches Total": 12.0,  # number
            "Data Breaches Personal": 5.0,  # number
            "Total Gross Exposure": 120000000.0,  # USD millions
            "Financed Emissions Covered Exposure": 85000000.0  # USD millions
        }
        return demo_values.get(metric_name, 100.0)  # Default fallback
    
    def _calculate_by_formula(self, formula: str, inputs: Dict[str, float]) -> float:
        """Execute calculation based on formula string with enhanced parsing"""
        try:
            print(f"    🔧 Parsing formula: '{formula}' with inputs: {inputs}")
            
            # Handle percentage calculations: numerator / denominator * 100
            if "/" in formula and "*" in formula and "100" in formula:
                # Parse pattern: "var1 / var2 * 100"
                parts = formula.replace(" ", "").split("/")
                if len(parts) >= 2:
                    numerator_var = parts[0].strip()
                    denominator_and_multiplier = parts[1].strip()
                    
                    # Extract denominator (before the *)
                    if "*" in denominator_and_multiplier:
                        denominator_var = denominator_and_multiplier.split("*")[0].strip()
                        multiplier_str = denominator_and_multiplier.split("*")[1].strip()
                        multiplier = float(multiplier_str) if multiplier_str.replace(".", "").isdigit() else 100.0
                    else:
                        denominator_var = denominator_and_multiplier
                        multiplier = 1.0
                    
                    print(f"    📊 Extracted: numerator='{numerator_var}', denominator='{denominator_var}', multiplier={multiplier}")
                    
                    # Get values from inputs
                    numerator = inputs.get(numerator_var, 0.0)
                    denominator = inputs.get(denominator_var, 1.0)
                    
                    if denominator == 0:
                        print(f"    ⚠️ Division by zero avoided, returning 0")
                        return 0.0
                    
                    result = (numerator / denominator) * multiplier
                    print(f"    ✅ Calculation: ({numerator} / {denominator}) * {multiplier} = {result}")
                    return result
            
            # Handle simple arithmetic operations
            elif "+" in formula:
                return self._execute_simple_arithmetic(formula, inputs, "+")
            elif "-" in formula:
                return self._execute_simple_arithmetic(formula, inputs, "-")
            elif "*" in formula and "/" not in formula:
                return self._execute_simple_arithmetic(formula, inputs, "*")
            elif "/" in formula and "*" not in formula:
                return self._execute_simple_arithmetic(formula, inputs, "/")
            
            # If no pattern matches, try generic execution
            else:
                return self._execute_generic_formula(formula, inputs)
                
        except Exception as e:
            print(f"    ❌ Formula calculation error: {str(e)}")
            return 0.0
    
    def _execute_simple_arithmetic(self, formula: str, inputs: Dict[str, float], operator: str) -> float:
        """Execute simple arithmetic operations"""
        try:
            parts = formula.split(operator)
            if len(parts) == 2:
                left_var = parts[0].strip()
                right_var = parts[1].strip()
                
                left_val = inputs.get(left_var, 0.0)
                right_val = inputs.get(right_var, 0.0)
                
                if operator == "+":
                    return left_val + right_val
                elif operator == "-":
                    return left_val - right_val
                elif operator == "*":
                    return left_val * right_val
                elif operator == "/" and right_val != 0:
                    return left_val / right_val
            return 0.0
        except:
            return 0.0
    
    def _execute_generic_formula(self, formula: str, inputs: Dict[str, float]) -> float:
        """Generic formula executor using safe evaluation"""
        try:
            # Replace variable names with their values
            formula_with_values = formula
            for var_name, value in inputs.items():
                formula_with_values = formula_with_values.replace(var_name, str(value))
            
            print(f"    🔧 Generic formula evaluation: '{formula_with_values}'")
            
            # Safe evaluation of basic mathematical expressions
            # Only allow numbers, basic operators, and parentheses
            allowed_chars = set('0123456789.+-*/() ')
            if all(c in allowed_chars for c in formula_with_values):
                result = eval(formula_with_values)
                print(f"    ✅ Generic calculation result: {result}")
                return float(result)
            else:
                print(f"    ⚠️ Formula contains unsafe characters, returning 0")
                return 0.0
                
        except Exception as e:
            print(f"    ❌ Generic formula execution error: {str(e)}")
            return 0.0
    
    def get_model_complexity(self, model_name: str) -> Dict[str, Any]:
        """Get complexity metrics for calculation model"""
        if model_name not in self.supported_models:
            return {"complexity": "unknown"}
        
        model = self.supported_models[model_name]
        input_count = len(model["inputs"])
        
        return {
            "model_name": model_name,
            "input_count": input_count,
            "complexity": "simple" if input_count <= 2 else "complex",
            "estimated_execution_time": 0.1 + (input_count * 0.05)  # seconds
        }
    
    def get_all_calculated_metrics(self, company_name: str, year: str) -> Dict[str, Any]:
        """Get all calculated metrics for a company from memory"""
        return self.calculation_memory.get(f"{company_name}:{year}", {})
    
    def _get_demo_input_value(self, input_var: str) -> float:
        """Get demo values for calculation inputs"""
        demo_values = {
            "grid_electricity": 875000.0,  # MWh
            "total_energy": 1250000.0,     # MWh  
            "renewable_energy": 375000.0,  # MWh
            "total_water_withdrawn": 450000.0,  # m³
            "high_stress_water": 90000.0,  # m³
            "high_stress_consumption": 85000.0,  # m³
            "total_water_consumed": 425000.0,  # m³
            "hazardous_waste": 1200.0,     # tonnes
            "recycled_waste": 960.0,       # tonnes
            "total_hazardous_waste": 1200.0,  # tonnes
            "personal_breaches": 5.0,       # number
            "total_breaches": 12.0,         # number
            "covered_exposure": 85000000.0, # USD millions
            "total_exposure": 120000000.0   # USD millions
        }
        return demo_values.get(input_var, 1000.0)
    
    def _load_supported_models(self) -> Dict[str, Any]:
        """Load actual calculation models from the extraction data"""
        return {
            # Semiconductor models (from your actual data)
            "Grid Electricity Rate Model": {
                "description": "Percentage of energy consumed that was supplied from grid electricity calculated as purchased grid electricity consumption divided by total energy consumption",
                "formula": "grid_electricity / total_energy * 100",
                "inputs": ["grid_electricity", "total_energy"],
                "output_unit": "Percentage (%)",
                "external_mappings": {
                    "grid_electricity": "RENEWENERGYPURCHASED",  # Use available renewable purchased as proxy 
                    "total_energy": "ENERGYUSETOTAL"
                }
            },
            "Renewable Energy Rate Model": {
                "description": "Percentage of energy consumed that was renewable energy calculated as renewable energy consumption divided by total energy consumption", 
                "formula": "renewable_energy / total_energy * 100",
                "inputs": ["renewable_energy", "total_energy"],
                "output_unit": "Percentage (%)",
                "external_mappings": {
                    "renewable_energy": "RENEWENERGYPURCHASED",  # Fixed to use absolute energy values
                    "total_energy": "ENERGYUSETOTAL"
                }
            },
            "High Stress Water Withdrawal Rate Model": {
                "description": "Water withdrawn in locations with High or Extremely High Baseline Water Stress as a percentage of the total water withdrawn",
                "formula": "high_stress_water / total_water_withdrawn * 100",
                "inputs": ["high_stress_water", "total_water_withdrawn"],
                "output_unit": "Percentage (%)",
                "external_mappings": {
                    "high_stress_water": "WATER_USE_PAI_M10",
                    "total_water_withdrawn": "WATERWITHDRAWALTOTAL"
                }
            },
            "High Stress Water Consumption Rate Model": {
                "description": "Water consumed in locations with High or Extremely High Baseline Water Stress as a percentage of the total water consumed",
                "formula": "high_stress_consumption / total_water_consumed * 100", 
                "inputs": ["high_stress_consumption", "total_water_consumed"],
                "output_unit": "Percentage (%)",
                "external_mappings": {
                    "high_stress_consumption": "WATER_USE_PAI_M10",
                    "total_water_consumed": "WATERWITHDRAWALTOTAL"
                }
            },
            "Hazardous Waste Recycling Rate Model": {
                "description": "Percentage of hazardous waste recycled calculated as the weight of hazardous waste generated from manufacturing operations that was recycled, divided by the total weight of all hazardous waste generated",
                "formula": "recycled_waste / total_hazardous_waste * 100",
                "inputs": ["recycled_waste", "total_hazardous_waste"],
                "output_unit": "Percentage (%)",
                "external_mappings": {
                    "recycled_waste": "ANALYTICWASTERECYCLINGRATIO",
                    "total_hazardous_waste": "HAZARDOUSWASTE"
                }
            },
            # Banking models (from your actual data)
            "Personal Data Breach Rate": {
                "description": "Percentage of total data breaches that involve personal data",
                "formula": "personal_breaches / total_breaches * 100",
                "inputs": ["personal_breaches", "total_breaches"], 
                "output_unit": "Percentage (%)",
                "external_mappings": {
                    "personal_breaches": "DATA_BREACHES_PERSONAL",
                    "total_breaches": "DATA_BREACHES_TOTAL"
                }
            },
            "Financed Emissions Coverage Rate": {
                "description": "Percentage of total gross exposure included in financed emissions calculation",
                "formula": "covered_exposure / total_exposure * 100",
                "inputs": ["covered_exposure", "total_exposure"],
                "output_unit": "Percentage (%)",
                "external_mappings": {
                    "covered_exposure": "FINANCED_EMISSIONS_COVERED",
                    "total_exposure": "TOTAL_GROSS_EXPOSURE"
                }
            }
        }

    def calculate(self, metric_name: str, company_name: str, year: str, industry: str) -> Dict[str, Any]:
        """Calculate metric using enhanced RDF-based data access flow"""
        start_time = time.time()
        
        try:
            # Convert SASB codes to user-friendly names
            user_friendly_name = self._convert_to_user_friendly_name(metric_name, industry)
            if user_friendly_name != metric_name:
                print(f"🔄 Converting SASB code: '{metric_name}' -> '{user_friendly_name}'")
                metric_name = user_friendly_name
            
            print(f"🔄 Calculating {metric_name} for {company_name} ({year})")
            
            # Step 1: Use CQ4 to determine measurement method
            cq4_result = self.kg_service.cq4_metric_calculation_method(industry, metric_name)
            calculation_method = cq4_result.get("measurement_method")
            
            print(f"📊 CQ4 result for {metric_name}: method={calculation_method}")
            
            # Step 2: Route to appropriate calculation method
            if calculation_method == "direct_measurement":
                result = self._handle_direct_measurement_via_rdf(metric_name, company_name, year, industry, cq4_result, start_time)
            elif calculation_method == "calculation_model":
                result = self._handle_model_calculation_via_rdf(metric_name, company_name, year, industry, cq4_result, start_time)
            else:
                result = self._create_error_result(
                    metric_name, company_name, year,
                    {"unit": "n/a", "sasb_code": "n/a", "category": "Unknown"},
                    f"Unknown calculation method: {calculation_method}",
                    time.time() - start_time
                )
            
            # Store successful calculation in memory
            try:
                self.store_calculation(company_name, year, result)
                print(f"💾 Stored calculation in memory: {metric_name}")
            except Exception as memory_error:
                print(f"⚠️ Failed to store calculation in memory: {str(memory_error)}")
            
            return result
            
        except Exception as e:
            error_msg = f"Calculation service error: {str(e)}"
            print(f"❌ Error in calculate: {error_msg}")
            return self._create_error_result(
                metric_name, company_name, year,
                {"unit": "n/a", "sasb_code": "n/a", "category": "Unknown"},
                error_msg,
                time.time() - start_time
            )

    def _handle_direct_measurement_via_rdf(self, metric_name: str, company_name: str, year: str, industry: str, cq4_result: Dict, start_time: float) -> Dict[str, Any]:
        """
        Handle direct measurement using RDF alignment data to find DatasetVariable
        """
        try:
            # Get DatasetVariable mapping from RDF alignment data
            dataset_variable = self._get_dataset_variable_from_rdf(metric_name, industry)
            
            if not dataset_variable:
                return {
                    "metric_name": metric_name,
                    "company_name": company_name,
                    "year": year,
                    "value": None,
                    "display_value": f"❌ No DatasetVariable mapping found for {metric_name}",
                    "unit": cq4_result.get("unit", "n/a"),
                    "sasb_code": cq4_result.get("metric_code", "n/a"),
                    "category": "Environmental",
                    "data_source": "unavailable",
                    "calculation_method": "direct_measurement",
                    "reason": f"No DatasetVariable mapping found in RDF alignment data for {metric_name}",
                    "status": "failed_no_mapping",
                    "calculation_time": time.time() - start_time,
                    "authenticity_score": 0.0
                }
            
            print(f"🔗 RDF DatasetVariable mapping: {metric_name} -> {dataset_variable}")
            
            # Get value from external dataset using the dataset_variable from RDF mapping
            # This ensures we use the correct dataset variable mapping from RDF alignment
            value = self.external_data_service.get_metric_value(company_name, year, dataset_variable)
            
            if value is not None:
                # Real data found
                return {
                    "metric_name": metric_name,
                    "company_name": company_name,
                    "year": year,
                    "value": value,
                    "display_value": self._format_display_value(value, cq4_result.get("unit", "")),
                    "unit": cq4_result.get("unit", "n/a"),
                    "sasb_code": cq4_result.get("metric_code", "n/a"),
                    "category": "Environmental",
                    "data_source": "external_dataset",
                    "calculation_method": "direct_measurement",
                    "dataset_variable": dataset_variable,
                    "rdf_mapping": f"RDF alignment: {metric_name} -> {dataset_variable}",
                    "status": "success",
                    "calculation_time": time.time() - start_time,
                    "authenticity_score": 1.0
                }
            else:
                # CLEAR ERROR: Direct measurement - no external data available
                error_category = "DIRECT_MEASUREMENT_NO_DATA"
                detailed_reason = f"Direct measurement failed: No real data found for '{dataset_variable}' in external dataset for company '{company_name}' in year {year}"
                user_friendly_reason = f"No external data available for {metric_name}"
                
                return {
                    "metric_name": metric_name,
                    "company_name": company_name,
                    "year": year,
                    "value": None,
                    "display_value": f"❌ {user_friendly_reason}",
                    "unit": cq4_result.get("unit", "n/a"),
                    "sasb_code": cq4_result.get("metric_code", "n/a"),
                    "category": "Environmental",
                    "data_source": "external_dataset_unavailable",
                    "calculation_method": "direct_measurement",
                    "dataset_variable": dataset_variable,
                    "error_category": error_category,
                    "detailed_reason": detailed_reason,
                    "user_friendly_reason": user_friendly_reason,
                    "status": "failed_no_external_data",
                    "calculation_time": time.time() - start_time,
                    "authenticity_score": 0.0
                }
                
        except Exception as e:
            return self._create_error_result(
                metric_name, company_name, year,
                {"unit": cq4_result.get("unit", "n/a"), "sasb_code": cq4_result.get("metric_code", "n/a"), "category": "Environmental"},
                f"Direct measurement error: {str(e)}",
                time.time() - start_time
            )

    def _handle_model_calculation_via_rdf(self, metric_name: str, company_name: str, year: str, industry: str, cq4_result: Dict, start_time: float) -> Dict[str, Any]:
        """
        Handle model calculation using RDF model data to get equation and inputs
        """
        try:
            model_name = cq4_result.get("model_name", "")
            
            if not model_name or model_name == "n/a":
                # CLEAR ERROR: Calculated metric - no model defined
                error_category = "CALCULATED_METRIC_NO_MODEL"
                detailed_reason = f"Calculation failed: No model defined for metric '{metric_name}' in RDF knowledge graph"
                user_friendly_reason = f"No calculation model available for {metric_name}"
                
                return {
                    "metric_name": metric_name,
                    "company_name": company_name,
                    "year": year,
                    "value": None,
                    "display_value": f"❌ {user_friendly_reason}",
                    "unit": cq4_result.get("unit", "n/a"),
                    "sasb_code": cq4_result.get("metric_code", "n/a"),
                    "category": "Environmental",
                    "data_source": "rdf_knowledge_graph",
                    "calculation_method": "calculation_model",
                    "error_category": error_category,
                    "detailed_reason": detailed_reason,
                    "user_friendly_reason": user_friendly_reason,
                    "status": "failed_no_model_defined",
                    "calculation_time": time.time() - start_time,
                    "authenticity_score": 0.0
                }
            
            # Get model equation and inputs from RDF (CQ5)
            cq5_result = self.kg_service.cq5_model_input_datapoints(industry, model_name, self)
            model_equation = cq5_result.get("model_equation", "")
            required_inputs = cq5_result.get("required_inputs", [])
            
            print(f"🧮 RDF Model: {model_name}")
            print(f"📐 Equation: {model_equation}")
            print(f"📊 Required inputs: {required_inputs}")
            
            if not model_equation:
                # CLEAR ERROR: Calculated metric - no model equation
                error_category = "CALCULATED_METRIC_NO_EQUATION"
                detailed_reason = f"Calculation failed: Model '{model_name}' exists but no equation found in RDF knowledge graph"
                user_friendly_reason = f"Model equation missing for {metric_name}"
                
                return {
                    "metric_name": metric_name,
                    "company_name": company_name,
                    "year": year,
                    "value": None,
                    "display_value": f"❌ {user_friendly_reason}",
                    "unit": cq4_result.get("unit", "n/a"),
                    "sasb_code": cq4_result.get("metric_code", "n/a"),
                    "category": "Environmental",
                    "data_source": "rdf_knowledge_graph",
                    "calculation_method": "calculation_model",
                    "model_name": model_name,
                    "error_category": error_category,
                    "detailed_reason": detailed_reason,
                    "user_friendly_reason": user_friendly_reason,
                    "status": "failed_no_model_equation",
                    "calculation_time": time.time() - start_time,
                    "authenticity_score": 0.0
                }
            
            # Get input values from external dataset via RDF mappings
            input_values = {}
            missing_inputs = []
            available_inputs = []
            data_sources = {}
            input_details = {}
            
            for input_metric in required_inputs:
                # Get DatasetVariable mapping for each input
                dataset_variable = self._get_dataset_variable_from_rdf(input_metric, industry)
                
                if dataset_variable:
                    # Use the RDF-mapped dataset_variable directly instead of input_metric name
                    # to avoid internal mapping conflicts
                    value = self.external_data_service.get_metric_value(company_name, year, dataset_variable)
                    if value is not None:
                        input_key = input_metric.lower().replace(" ", "_")
                        input_values[input_key] = value
                        available_inputs.append(input_metric)
                        data_sources[input_metric] = {
                            "dataset_variable": dataset_variable,
                            "source": "external_dataset",
                            "value": value
                        }
                        input_details[input_metric] = {
                            "status": "available",
                            "value": value,
                            "dataset_variable": dataset_variable,
                            "source": "external_dataset"
                        }
                        print(f"✅ Input {input_metric}: {value} (from {dataset_variable})")
                    else:
                        missing_inputs.append(input_metric)
                        input_details[input_metric] = {
                            "status": "missing",
                            "dataset_variable": dataset_variable,
                            "reason": "No data available in external dataset"
                        }
                        print(f"❌ Input {input_metric}: No data available (mapped to {dataset_variable})")
                else:
                    missing_inputs.append(input_metric)
                    input_details[input_metric] = {
                        "status": "missing",
                        "reason": "No DatasetVariable mapping found in RDF alignment"
                    }
                    print(f"❌ Input {input_metric}: No DatasetVariable mapping found")
            
            if missing_inputs:
                # CLEAR ERROR: Calculated metric - missing input data
                error_category = "CALCULATED_METRIC_MISSING_INPUTS"
                detailed_reason = f"Calculation failed: Model '{model_name}' requires inputs {required_inputs}, but missing real data for: {missing_inputs}"
                user_friendly_reason = f"Missing input data for calculation: {', '.join(missing_inputs)}"
                
                return {
                    "metric_name": metric_name,
                    "company_name": company_name,
                    "year": year,
                    "value": None,
                    "display_value": f"❌ {user_friendly_reason}",
                    "unit": cq4_result.get("unit", "n/a"),
                    "sasb_code": cq4_result.get("metric_code", "n/a"),
                    "category": "Environmental",
                    "data_source": "external_dataset_incomplete",
                    "calculation_method": "calculation_model",
                    "model_name": model_name,
                    "model_equation": model_equation,
                    "required_inputs": required_inputs,
                    "missing_inputs": missing_inputs,
                    "available_inputs": available_inputs,
                    "input_details": input_details,
                    "data_sources": data_sources,
                    "error_category": error_category,
                    "detailed_reason": detailed_reason,
                    "user_friendly_reason": user_friendly_reason,
                    "status": "failed_missing_input_data",
                    "calculation_time": time.time() - start_time,
                    "authenticity_score": 0.0
                }
            
            # Execute calculation
            try:
                calculated_value = self._execute_model_equation(model_equation, input_values)
                
                return {
                    "metric_name": metric_name,
                    "company_name": company_name,
                    "year": year,
                    "value": calculated_value,
                    "display_value": self._format_display_value(calculated_value, cq4_result.get("unit", "")),
                    "unit": cq4_result.get("unit", "n/a"),
                    "sasb_code": cq4_result.get("metric_code", "n/a"),
                    "category": "Environmental",
                    "data_source": "calculated_from_real_data",
                    "calculation_method": "calculation_model",
                    "model_name": model_name,
                    "model_equation": model_equation,
                    "required_inputs": required_inputs,
                    "input_values": input_values,
                    "available_inputs": available_inputs,
                    "input_details": input_details,
                    "data_sources": data_sources,
                    "status": "success",
                    "calculation_time": time.time() - start_time,
                    "authenticity_score": 0.95
                }
                
            except Exception as calc_error:
                return {
                    "metric_name": metric_name,
                    "company_name": company_name,
                    "year": year,
                    "value": None,
                    "display_value": f"❌ Calculation failed: {str(calc_error)}",
                    "unit": cq4_result.get("unit", "n/a"),
                    "sasb_code": cq4_result.get("metric_code", "n/a"),
                    "category": "Environmental",
                    "data_source": "calculation_failed",
                    "calculation_method": "calculation_model",
                    "model_name": model_name,
                    "model_equation": model_equation,
                    "input_values": input_values,
                    "reason": f"Equation execution failed: {str(calc_error)}",
                    "status": "failed_equation_error",
                    "calculation_time": time.time() - start_time,
                    "authenticity_score": 0.0
                }
                
        except Exception as e:
            return self._create_error_result(
                metric_name, company_name, year,
                {"unit": cq4_result.get("unit", "n/a"), "sasb_code": cq4_result.get("metric_code", "n/a"), "category": "Environmental"},
                f"Model calculation error: {str(e)}",
                time.time() - start_time
            )

    def _get_dataset_variable_from_rdf(self, metric_name: str, industry: str) -> str:
        """
        Get DatasetVariable mapping from RDF knowledge graph using SPARQL queries
        """
        try:
            # First try direct metric name mapping
            sparql_query = f'''
            PREFIX esg: <http://example.org/esg#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?datasetVar WHERE {{
                ?metric rdfs:label "{metric_name}" .
                ?metric esg:obtainedFrom ?datasetVarEntity .
                ?datasetVarEntity rdfs:label ?datasetVar .
            }}
            '''
            
            # Execute SPARQL query
            result = self.kg_service.execute_sparql_query(sparql_query)
            
            if result.get('results') and len(result['results']) > 0:
                # Get the first dataset variable found
                dataset_var = str(result['results'][0].datasetVar)
                print(f"🔗 RDF DatasetVariable mapping: {metric_name} -> {dataset_var}")
                return dataset_var
            
            # If not found, try mapping equation variables to RDF input labels
            variable_to_label_mapping = {
                "renewable_energy": "Renewable Energy Consumption",
                "total_energy": "Total Energy Consumption", 
                "grid_electricity": "Grid Electricity Consumption",
                "recycled_hazardous_waste": "Recycled Hazardous Waste",
                "total_hazardous_waste": "Total Hazardous Waste Generated"
            }
            
            if metric_name in variable_to_label_mapping:
                rdf_label = variable_to_label_mapping[metric_name]
                alt_query = f'''
                PREFIX esg: <http://example.org/esg#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                
                SELECT ?datasetVar WHERE {{
                    ?input rdfs:label "{rdf_label}" .
                    ?input esg:obtainedFrom ?datasetVarEntity .
                    ?datasetVarEntity rdfs:label ?datasetVar .
                }}
                '''
                
                alt_result = self.kg_service.execute_sparql_query(alt_query)
                if alt_result.get('results') and len(alt_result['results']) > 0:
                    dataset_var = str(alt_result['results'][0].datasetVar)
                    print(f"🔗 RDF Variable-to-Label mapping: {metric_name} ({rdf_label}) -> {dataset_var}")
                    return dataset_var
            
            print(f"⚠️ No RDF DatasetVariable mapping found for: {metric_name}")
                
            # Try alternative query with partial match
            alt_query = f'''
            PREFIX esg: <http://example.org/esg#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?datasetVar WHERE {{
                ?metric rdfs:label ?metricLabel .
                ?metric esg:obtainedFrom ?datasetVarEntity .
                ?datasetVarEntity rdfs:label ?datasetVar .
                FILTER(CONTAINS(LCASE(?metricLabel), LCASE("{metric_name.split()[0]}")))
            }}
            '''
                
            alt_result = self.kg_service.execute_sparql_query(alt_query)
            if alt_result.get('results') and len(alt_result['results']) > 0:
                dataset_var = str(alt_result['results'][0].datasetVar)
                print(f"🔗 RDF Alternative DatasetVariable mapping: {metric_name} -> {dataset_var}")
                return dataset_var
                
            # Final fallback to external data service mapping
            fallback_var = self.external_data_service._map_sasb_to_external(metric_name.lower().replace(" ", "_"))
            print(f"🔄 Using fallback mapping: {metric_name} -> {fallback_var}")
            return fallback_var
            
        except Exception as e:
            print(f"⚠️ Error getting DatasetVariable from RDF: {e}")
            # Fallback to external data service mapping
            fallback_var = self.external_data_service._map_sasb_to_external(metric_name.lower().replace(" ", "_"))
            print(f"🔄 Using fallback mapping after error: {metric_name} -> {fallback_var}")
            return fallback_var

    def _execute_model_equation(self, equation: str, input_values: Dict[str, float]) -> float:
        """
        Execute model equation with input values
        """
        try:
            # Simple equation parser for basic arithmetic
            # Convert equation variables to actual values
            equation_to_eval = equation
            
            # Clean up the equation - replace special symbols
            equation_to_eval = equation_to_eval.replace('×', '*')  # Replace × with *
            equation_to_eval = equation_to_eval.replace('÷', '/')  # Replace ÷ with /
            
            for var_name, value in input_values.items():
                # Replace variable names in equation with actual values
                equation_to_eval = equation_to_eval.replace(var_name, str(value))
            
            # Handle common mathematical operations safely
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in equation_to_eval):
                # Find problematic characters
                problematic_chars = [c for c in equation_to_eval if c not in allowed_chars]
                raise ValueError(f"Unsafe characters in equation: {equation_to_eval}. Problematic: {problematic_chars}")
            
            print(f"🧮 Executing equation: {equation_to_eval}")
            
            # Evaluate the equation
            result = eval(equation_to_eval)
            return float(result)
            
        except Exception as e:
            raise Exception(f"Failed to execute equation '{equation}' with inputs {input_values}: {str(e)}")

    def _convert_to_user_friendly_name(self, metric_input: str, industry: str) -> str:
        """Convert SASB technical codes to user-friendly metric names"""
        try:
            # Load extraction data to get the mapping
            extraction_path = f"data/raw/extraction_{industry.replace('_', '-')}-standard_en-gb.pdf_1748577858.json"
            if not Path(extraction_path).exists():
                # Try alternative naming pattern
                extraction_path = f"data/raw/extraction_{industry.replace('_', '-')}-standard_en-gb.pdf_1748577792.json"
            
            if Path(extraction_path).exists():
                with open(extraction_path, 'r') as f:
                    extraction_data = json.load(f)
                
                # Check if input is a SASB code (like TC-SC-110a.1)
                if any(char in metric_input for char in ['-', '.']):
                    # Find metric by SASB code
                    for metric in extraction_data.get('metrics', []):
                        if metric.get('code') == metric_input:
                            user_friendly = metric.get('metric_name')
                            print(f"🔄 Converting SASB code: '{metric_input}' -> '{user_friendly}'")
                            return user_friendly
                
                # Check if input is already a user-friendly name
                for metric in extraction_data.get('metrics', []):
                    if metric.get('metric_name') == metric_input:
                        return metric_input  # Already user-friendly
            
            # If not found, return as-is but transformed if it looks like a SASB code
            if any(char in metric_input for char in ['-', '.']):
                print(f"🔄 No mapping found, using transformation: '{metric_input}' -> '{self._transform_sasb_code(metric_input)}'")
                return self._transform_sasb_code(metric_input)
            
            return metric_input
            
        except Exception as e:
            print(f"⚠️ Error converting metric name: {e}")
            return metric_input

    def _transform_sasb_code(self, sasb_code: str) -> str:
        """Transform SASB code to a more readable format as fallback"""
        # Simple transformation for codes like TC-SC-110a.1
        return sasb_code.replace('-', '').replace('.', '.').upper()

    def _format_display_value(self, value, unit: str) -> str:
        """Format value for user-friendly display"""
        if value is None:
            return "No data available"
        
        # Handle string values (like Yes/No) directly without numeric formatting
        if isinstance(value, str):
            return f"{value} {unit}".strip() if unit and unit != "n/a" else value
        
        # Handle numeric values
        try:
            numeric_value = float(value)
            # Format large numbers with commas
            if numeric_value >= 1000:
                formatted = f"{numeric_value:,.1f}"
            else:
                formatted = f"{numeric_value:.2f}"
            
            return f"{formatted} {unit}".strip()
        except (ValueError, TypeError):
            # If conversion to float fails, treat as string
            return f"{value} {unit}".strip() if unit and unit != "n/a" else str(value)

    def _create_error_result(self, metric_name: str, company_name: str, year: str, metadata: Dict, error_message: str, calculation_time: float) -> Dict[str, Any]:
        """
        Create standardized error result
        """
        return {
            "metric_name": metric_name,
            "company_name": company_name,
            "year": year,
            "value": None,
            "display_value": f"❌ Error: {error_message}",
            "unit": metadata.get("unit", "n/a"),
            "sasb_code": metadata.get("sasb_code", "n/a"),
            "category": metadata.get("category", "Unknown"),
            "data_source": "error",
            "calculation_method": "error",
            "reason": error_message,
            "status": "error",
            "calculation_time": calculation_time,
            "authenticity_score": 0.0
        }

    def get_all_calculated_metrics_for_company(self, company_name: str, year: str) -> Dict[str, Any]:
        """Get all calculated metrics for a company across all categories"""
        try:
            # Check calculation memory for this company
            memory_key = f"{company_name}:{year}"
            calculated_metrics = {}
            
            if memory_key in self.calculation_memory:
                for metric_name, cached_entry in self.calculation_memory[memory_key].items():
                    # Check if cache is still valid (24 hours)
                    if time.time() - cached_entry['timestamp'] < 86400:
                        calculated_metrics[metric_name] = {
                            "result": cached_entry['result'],
                            "calculated_at": cached_entry['timestamp'],
                            "status": "cached",
                            "category": cached_entry['result'].get('category', 'Unknown'),
                            "value": cached_entry['result'].get('value'),
                            "calculation_method": cached_entry['result'].get('calculation_method', 'unknown')
                        }
            
            return {
                "company_name": company_name,
                "year": year,
                "calculated_metrics": calculated_metrics,
                "total_calculated": len(calculated_metrics),
                "last_updated": max([m["calculated_at"] for m in calculated_metrics.values()]) if calculated_metrics else None
            }
            
        except Exception as e:
            print(f"⚠️ Error getting calculated metrics for {company_name}: {str(e)}")
            return {
                "company_name": company_name,
                "year": year,
                "calculated_metrics": {},
                "total_calculated": 0,
                "error": str(e)
            }