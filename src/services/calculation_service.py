# src/services/calculation_service.py
from typing import Dict, Any, List, Optional
import time

# Import the consolidated dynamic model loader
from ..models import model_loader

class CalculationService:
    """Clean ESG Calculation Service following semantic architecture: CQ4→CQ5→CQ7→CQ6→Dynamic Loading"""
    
    def __init__(self, external_data_service=None, kg_service=None):
        self.external_data_service = external_data_service
        self.kg_service = kg_service
        self.model_loader = model_loader

    def calculate(self, metric_name: str, company_name: str, year: str, industry: str) -> Dict[str, Any]:
        """
        Calculate metric using clean semantic flow:
        CQ4 → (direct_measurement → CQ7) OR (calculation_model → CQ5 → CQ4/CQ7 for inputs → CQ6 → execute)
        """
        start_time = time.time()
        
        try:
            print(f"🔄 Calculating {metric_name} for {company_name} ({year})")
            
            # Convert metric name to knowledge graph format before CQ4
            converted_metric_name = self._convert_to_user_friendly_name(metric_name, industry)
            print(f"🔄 Converted metric name: '{metric_name}' → '{converted_metric_name}'")
            
            # Step 1: CQ4 - Get calculation method and model
            print(f"📊 Step 1: CQ4 - Getting calculation method for {converted_metric_name}")
            cq4_result = self.kg_service.cq4_metric_calculation_method(industry, converted_metric_name)
            calculation_method = cq4_result.get("measurement_method")
            
            if not calculation_method:
                return self._create_error_result(
                    metric_name, company_name, year, 
                    "Step 1 Failed: CQ4 did not return calculation method", 
                    start_time
                )
            
            print(f"✅ CQ4 result: method={calculation_method}")
            
            # Step 2: Route based on calculation method
            if calculation_method == "direct_measurement":
                return self._handle_direct_measurement(converted_metric_name, company_name, year, industry, cq4_result, start_time)
            elif calculation_method == "calculation_model":
                return self._handle_calculation_model(converted_metric_name, company_name, year, industry, cq4_result, start_time)
            else:
                return self._create_error_result(
                    converted_metric_name, company_name, year,
                    f"Step 1 Failed: Unknown calculation method '{calculation_method}' from CQ4",
                    start_time
                )
                
        except Exception as e:
            print(f"❌ Error in calculate: {str(e)}")
            # Use original metric name for user-facing error messages
            return self._create_error_result(
                metric_name, company_name, year,
                f"Calculation service error: {str(e)}",
                start_time
            )

    def _handle_direct_measurement(self, metric_name: str, company_name: str, year: str, industry: str, cq4_result: Dict, start_time: float) -> Dict[str, Any]:
        """Handle direct measurement: CQ7 → Get dataset variable → Return value"""
        try:
            # Step 2: CQ7 - Get dataset variable mapping
            print(f"📊 Step 2: CQ7 - Getting dataset variable for {metric_name}")
            cq7_result = self.kg_service.cq7_datapoint_original_source(industry, metric_name)
            
            if not cq7_result or not cq7_result.get("original_datasource"):
                return self._create_error_result(
                    metric_name, company_name, year,
                    f"Step 2 Failed: CQ7 did not return dataset variable mapping for {metric_name}",
                    start_time
                )
            
            dataset_variable = cq7_result.get("original_datasource", {}).get("dataset_variable")
            if not dataset_variable:
                return self._create_error_result(
                    metric_name, company_name, year,
                    f"Step 2 Failed: CQ7 returned empty dataset variable for {metric_name}",
                    start_time
                )
            
            print(f"✅ CQ7 result: {metric_name} → {dataset_variable}")
            
            # Step 3: Get value from dataset
            print(f"📊 Step 3: Getting value for {dataset_variable}")
            value = self.external_data_service.get_metric_value(company_name, year, dataset_variable)
            
            if value is None:
                return self._create_error_result(
                    metric_name, company_name, year,
                    f"Step 3 Failed: No data found for {dataset_variable} in {company_name} ({year})",
                    start_time
                )
            
            print(f"✅ Retrieved value: {value}")
            
            return {
                "metric_name": metric_name,
                "company_name": company_name,
                "year": year,
                "value": value,
                "display_value": f"{value:,.2f}" if isinstance(value, (int, float)) else str(value),
                "unit": cq4_result.get("unit", "n/a"),
                "sasb_code": cq4_result.get("metric_code", "n/a"),
                "calculation_method": "direct_measurement",
                "dataset_variable": dataset_variable,
                "status": "success",
                "calculation_time": time.time() - start_time
            }
                
        except Exception as e:
            print(f"❌ Error in direct measurement: {str(e)}")
            return self._create_error_result(
                metric_name, company_name, year,
                f"Direct measurement flow error: {str(e)}",
                start_time
            )

    def _handle_calculation_model(self, metric_name: str, company_name: str, year: str, industry: str, cq4_result: Dict, start_time: float) -> Dict[str, Any]:
        """Handle calculation model: CQ5 → CQ4/CQ7 for inputs → CQ6 → Execute"""
        try:
            model_name = cq4_result.get("model_name", "")
            
            if not model_name or model_name == "n/a":
                return self._create_error_result(
                    metric_name, company_name, year,
                    f"Step 1 Failed: CQ4 did not return valid model name for {metric_name}",
                    start_time
                )
            
            print(f"✅ CQ4 result: Using model {model_name}")
            
            # Step 2: CQ5 - Get required input metrics
            print(f"📊 Step 2: CQ5 - Getting required input metrics for {model_name}")
            cq5_result = self.kg_service.cq5_model_input_datapoints(industry, model_name, self)
            required_inputs = cq5_result.get("required_inputs", [])
            
            if not required_inputs:
                return self._create_error_result(
                    metric_name, company_name, year,
                    f"Step 2 Failed: CQ5 did not return required input metrics for {model_name}",
                    start_time
                )
            
            model_equation = cq5_result.get("model_equation", cq5_result.get("formula", ""))
            print(f"✅ CQ5 result: Required inputs = {required_inputs}")

            # Step 3: For each input metric, get its value using CQ4→CQ7
            print(f"📊 Step 3: Getting values for all input metrics")
            input_values = {}
            input_dataset_variables = {}  # Track dataset variables for each input metric

            for input_metric in required_inputs:
                print(f"  📊 Getting value for input: {input_metric}")

                # Sub-step 3a: CQ4 for input metric
                try:
                    input_cq4 = self.kg_service.cq4_metric_calculation_method(industry, input_metric)
                    input_method = input_cq4.get("measurement_method")

                    if input_method != "direct_measurement":
                        print(f"  ❌ Input {input_metric} is not direct measurement, skipping")
                        continue

                except Exception as e:
                    print(f"  ❌ CQ4 failed for input {input_metric}: {str(e)}")
                    continue

                # Sub-step 3b: CQ7 for input metric
                try:
                    input_cq7 = self.kg_service.cq7_datapoint_original_source(industry, input_metric)
                    dataset_variable = input_cq7.get("original_datasource", {}).get("dataset_variable")

                    if not dataset_variable:
                        print(f"  ❌ CQ7 failed for input {input_metric}: no dataset variable")
                        continue

                except Exception as e:
                    print(f"  ❌ CQ7 failed for input {input_metric}: {str(e)}")
                    continue

                # Track the dataset variable for this input metric
                input_dataset_variables[input_metric] = dataset_variable

                # Sub-step 3c: Get value from dataset
                try:
                    value = self.external_data_service.get_metric_value(company_name, year, dataset_variable)
                    if value is not None:
                        # Map input metric names to function parameter names
                        input_key = self._map_input_metric_to_parameter(input_metric)
                        input_values[input_key] = value
                        print(f"  ✅ {input_metric} = {value} (mapped to {input_key})")
                    else:
                        print(f"  ❌ No value found for {input_metric} in {dataset_variable}")

                except Exception as e:
                    print(f"  ❌ Data retrieval failed for {input_metric}: {str(e)}")
                    continue
            
            # Check if we have all required inputs  
            missing_inputs = [inp for inp in required_inputs if self._map_input_metric_to_parameter(inp) not in input_values]
            if missing_inputs:
                return self._create_error_result(
                    metric_name, company_name, year,
                    f"Step 3 Failed: Missing input values for: {missing_inputs}",
                    start_time
                )
            
            print(f"✅ All inputs collected: {input_values}")
            
            # Step 4: CQ6 - Get implementation details
            print(f"📊 Step 4: CQ6 - Getting implementation for {model_name}")
            cq6_result = self.kg_service.cq6_model_implementation(industry, model_name, self)
            implementation_details = cq6_result.get("implementation_details", {})
            file_path = implementation_details.get("file_path")
            function_name = implementation_details.get("function_name")
            
            if not file_path or not function_name:
                return self._create_error_result(
                    metric_name, company_name, year,
                    f"Step 4 Failed: CQ6 did not return implementation details for {model_name}",
                    start_time
                )
            
            print(f"✅ CQ6 result: {file_path}::{function_name}")
            
            # Step 5: Execute calculation using dynamic loading
            print(f"📊 Step 5: Executing calculation")
            try:
                result = self.model_loader.execute_implementation(file_path, function_name, input_values)
                print(f"✅ Calculation result: {result}")
                
                return {
                    "metric_name": metric_name,
                    "company_name": company_name,
                    "year": year,
                    "value": result,
                    "display_value": f"{result:,.4f}" if isinstance(result, (int, float)) else str(result),
                    "unit": cq4_result.get("unit", "n/a"),
                    "sasb_code": cq4_result.get("metric_code", "n/a"),
                    "calculation_method": "calculation_model",
                    "model_name": model_name,
                    "model_equation": model_equation,
                    "input_values": input_values,
                    "input_dataset_variables": input_dataset_variables,
                    "implementation": {"file_path": file_path, "function_name": function_name},
                    "status": "success",
                    "calculation_time": time.time() - start_time
                }
                
            except Exception as e:
                return self._create_error_result(
                    metric_name, company_name, year,
                    f"Step 5 Failed: Dynamic execution error: {str(e)}",
                    start_time
                )
            
        except Exception as e:
            print(f"❌ Error in model calculation: {str(e)}")
            return self._create_error_result(
                metric_name, company_name, year,
                f"Model calculation flow error: {str(e)}",
                start_time
            )
    
    def _create_error_result(self, metric_name: str, company_name: str, year: str, error_message: str, start_time: float) -> Dict[str, Any]:
        """Create standardized error result with clear step information"""
        return {
            "metric_name": metric_name,
            "company_name": company_name,
            "year": year,
            "value": None,
            "display_value": f"❌ {error_message}",
            "unit": "n/a",
            "sasb_code": "n/a",
            "calculation_method": "unknown",
            "status": "error",
            "error_message": error_message,
            "calculation_time": time.time() - start_time
        }
    
    # Minimal required methods for API compatibility
    def get_calculable_metrics(self, industry: str) -> Dict[str, Any]:
        """Get calculable metrics for industry"""
        try:
            metrics = self.kg_service.get_metrics_by_industry(industry)
            calculable = []
            skipped = []
            
            for metric in metrics:
                try:
                    cq4_result = self.kg_service.cq4_metric_calculation_method(industry, metric.get("metric_name"))
                    calculable.append({
                        "metric_name": metric.get("metric_name"),
                        "calculation_method": cq4_result.get("measurement_method")
                    })
                except:
                    skipped.append({"metric_name": metric.get("metric_name"), "reason": "CQ4 failed"})
            
            return {"calculable_metrics": calculable, "skipped_metrics": skipped}
            
        except Exception as e:
            return {"calculable_metrics": [], "skipped_metrics": [], "error": str(e)}
    
    def get_model_complexity(self, model_name: str) -> Dict[str, Any]:
        """Get model complexity from CQ5"""
        try:
            industry = "semiconductors"  # Default for complexity check
            cq5_result = self.kg_service.cq5_model_input_datapoints(industry, model_name, self)
            input_count = len(cq5_result.get("required_inputs", []))
            
            return {
                "model_name": model_name,
                "input_count": input_count,
                "complexity": "simple" if input_count <= 2 else "complex"
            }
        except:
            return {"model_name": model_name, "input_count": 0, "complexity": "unknown"}
    
    # ==================== API COMPATIBILITY METHODS ====================
    
    def _convert_to_user_friendly_name(self, metric_input: str, industry: str) -> str:
        """Convert SASB codes to user-friendly names matching knowledge graph format"""
        try:
            # GHG-related metrics
            if metric_input in ["TC-SC-110a.2", "ghgemissionintensity", "GHG Emission Intensity"]:
                return "GHGEmissionIntensity"
            elif metric_input in ["TC-SC-110a.1"]:
                return "GrossGlobalScope1Emissions"
            elif metric_input in ["TC-SC-110a.3"]:
                return "PerfluorinatedCompoundsEmissions"
            # Energy metrics - Fix the naming mismatch
            elif metric_input in ["Grid Electricity Rate", "grid_electricity_rate"]:
                return "PercentageGridElectricity"  # Match knowledge graph format
            elif metric_input in ["Renewable Energy Rate", "renewable_energy_rate"]:
                return "PercentageRenewableEnergy"  # Match knowledge graph format
            # Water metrics
            elif metric_input in ["High Stress Water Consumption Rate"]:
                return "PercentageWaterConsumedHighStress"
            elif metric_input in ["High Stress Water Withdrawal Rate"]:
                return "PercentageWaterWithdrawnHighStress"
            # Waste metrics
            elif metric_input in ["Hazardous Waste Recycling Rate"]:
                return "PercentageHazardousWasteRecycled"
            else:
                # Default: return as-is
                return metric_input
        except:
            return metric_input
    
    def _map_input_metric_to_parameter(self, input_metric: str) -> str:
        """Map input metric names from knowledge graph to function parameter names"""
        # Standard mapping for GHG Emission Intensity model
        mapping = {
            "Scope 1 Emission": "scope1_emissions",
            "Scope 2 Emission": "scope2_emissions",
            "GrossGlobalScope1Emissions": "scope1_emissions",  # Alternative name from RDF
            "Revenue": "revenue",
            # Add more mappings as needed for other models
            "Grid Electricity": "grid_electricity",
            "Total Energy": "total_energy",
            "Renewable Energy": "renewable_energy",
            "High Stress Water Consumed": "high_stress_water_consumed",
            "Total Water Consumed": "total_water_consumed",
            "High Stress Water Withdrawn": "high_stress_water_withdrawn",
            "Total Water Withdrawn": "total_water_withdrawn",
            "Hazardous Waste": "hazardous_waste",
            "Recycled Waste": "recycled_waste"
        }
        
        # Return mapped parameter name or fallback to default conversion
        return mapping.get(input_metric, input_metric.lower().replace(" ", "_"))
    
    @property 
    def memory_service(self):
        """Dummy memory service for API compatibility"""
        return DummyMemoryService()

class DummyMemoryService:
    """Dummy memory service to maintain API compatibility"""
    
    def get_all_calculated_metrics_for_company(self, company_name: str, year: str) -> Dict[str, Any]:
        """Return empty calculated metrics"""
        return {"calculated_metrics": {}}
    
    def store_calculation_result(self, *args, **kwargs):
        """No-op storage for compatibility"""
        pass