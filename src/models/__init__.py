"""
ESG Calculation Models Package

This package contains implementation files for ESG calculation models
as specified in the ESG Knowledge Graph RDF.

Available Models (aligned with RDF Knowledge Graph):
1. GHG Emission Intensity Model (ghg_emission_intensity_model.py)
2. Grid Electricity Rate Model (energy_rate_models.py)
3. Renewable Energy Rate Model (energy_rate_models.py)
4. Hazardous Waste Recycling Rate Model (waste_rate_models.py)
5. High Stress Water Consumption Rate Model (water_rate_models.py)
6. High Stress Water Withdrawal Rate Model (water_rate_models.py)
"""

import importlib
import inspect
from typing import Dict, Any, Callable, Optional

# Import all calculation functions from their respective modules
from .ghg_emission_intensity_model import (
    calculate_ghg_emission_intensity, 
    validate_inputs as validate_ghg_inputs, 
    get_model_metadata as get_ghg_metadata
)

from .energy_rate_models import (
    calculate_grid_electricity_rate,
    calculate_renewable_energy_rate
)

from .waste_rate_models import (
    calculate_hazardous_waste_recycling_rate
)

from .water_rate_models import (
    calculate_high_stress_water_consumption_rate,
    calculate_high_stress_water_withdrawal_rate
)

# ==================== DYNAMIC MODEL LOADER (Consolidated) ====================

class ModelLoader:
    """Dynamic loader for ESG calculation model implementations"""
    
    def __init__(self):
        self._loaded_modules = {}
        self._function_cache = {}
    
    def load_implementation(self, file_path: str, function_name: str) -> Optional[Callable]:
        """
        Dynamically load a model implementation function
        
        Args:
            file_path (str): Path to the Python file (e.g., "models/ghg_emission_intensity_model.py")
            function_name (str): Name of the function to load
            
        Returns:
            Callable: The loaded function, or None if loading failed
        """
        
        # Normalize the file path to module path
        if file_path.startswith("models/"):
            module_path = f"src.models.{file_path.replace('models/', '').replace('.py', '')}"
        else:
            module_path = file_path.replace('/', '.').replace('.py', '')
        
        # Check cache first
        cache_key = f"{module_path}.{function_name}"
        if cache_key in self._function_cache:
            return self._function_cache[cache_key]
        
        try:
            # Load or reload the module
            if module_path in self._loaded_modules:
                module = importlib.reload(self._loaded_modules[module_path])
            else:
                module = importlib.import_module(module_path)
                self._loaded_modules[module_path] = module
            
            # Get the function from the module
            if hasattr(module, function_name):
                function = getattr(module, function_name)
                
                # Cache the function
                self._function_cache[cache_key] = function
                
                return function
            else:
                raise AttributeError(f"Function '{function_name}' not found in module '{module_path}'")
                
        except ImportError as e:
            raise ImportError(f"Could not import module '{module_path}': {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error loading implementation: {str(e)}")
    
    def execute_implementation(self, file_path: str, function_name: str, inputs: Dict[str, Any]) -> Any:
        """
        Load and execute a model implementation with given inputs
        
        Args:
            file_path (str): Path to the Python file
            function_name (str): Name of the function to execute
            inputs (Dict[str, Any]): Input parameters for the function
            
        Returns:
            Any: The result of the function execution
        """
        
        # Load the implementation function
        function = self.load_implementation(file_path, function_name)
        
        if function is None:
            raise RuntimeError(f"Could not load function '{function_name}' from '{file_path}'")
        
        try:
            # Execute the function with the provided inputs
            result = function(**inputs)
            return result
            
        except TypeError as e:
            # Handle parameter mismatch errors
            raise TypeError(f"Parameter mismatch when calling '{function_name}': {str(e)}")
        except Exception as e:
            # Handle any other execution errors
            raise RuntimeError(f"Error executing '{function_name}': {str(e)}")
    
    def validate_implementation(self, file_path: str, function_name: str) -> Dict[str, Any]:
        """
        Validate that an implementation can be loaded and inspect its signature
        
        Args:
            file_path (str): Path to the Python file
            function_name (str): Name of the function to validate
            
        Returns:
            Dict[str, Any]: Validation results including signature info
        """
        
        try:
            function = self.load_implementation(file_path, function_name)
            
            if function is None:
                return {
                    "valid": False,
                    "error": "Function could not be loaded"
                }
            
            # Get function signature information
            sig = inspect.signature(function)
            
            parameters = []
            for param_name, param in sig.parameters.items():
                parameters.append({
                    "name": param_name,
                    "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                    "default": str(param.default) if param.default != inspect.Parameter.empty else None
                })
            
            return {
                "valid": True,
                "function_name": function_name,
                "file_path": file_path,
                "parameters": parameters,
                "return_annotation": str(sig.return_annotation) if sig.return_annotation != inspect.Signature.empty else "Any",
                "docstring": function.__doc__ or "No documentation available"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def clear_cache(self):
        """Clear the module and function cache"""
        self._loaded_modules.clear()
        self._function_cache.clear()


# Global instance for reuse (replaces the standalone model_loader.py)
model_loader = ModelLoader()

# Export all functions for external use
__all__ = [
    # GHG Emission Intensity Model
    'calculate_ghg_emission_intensity',
    'validate_ghg_inputs', 
    'get_ghg_metadata',
    
    # Energy Rate Models
    'calculate_grid_electricity_rate',
    'calculate_renewable_energy_rate',
    
    # Waste Rate Models
    'calculate_hazardous_waste_recycling_rate',
    
    # Water Rate Models
    'calculate_high_stress_water_consumption_rate',
    'calculate_high_stress_water_withdrawal_rate',
    
    # Dynamic Model Loader (consolidated)
    'model_loader',
    'ModelLoader'
]

# Model registry for mapping RDF model names to Python functions
MODEL_REGISTRY = {
    # RDF Model Name → Python Function
    "GHGEmissionIntensityModel": calculate_ghg_emission_intensity,
    "GridElectricityRateModel": calculate_grid_electricity_rate,
    "RenewableEnergyRateModel": calculate_renewable_energy_rate,
    "HazardousWasteRecyclingRateModel": calculate_hazardous_waste_recycling_rate,
    "HighStressWaterConsumptionRateModel": calculate_high_stress_water_consumption_rate,
    "HighStressWaterWithdrawalRateModel": calculate_high_stress_water_withdrawal_rate,
}

# File path mapping for dynamic loading (matches RDF hasFilePath)
FILE_PATH_REGISTRY = {
    "models/ghg_emission_intensity_model.py": "ghg_emission_intensity_model",
    "models/energy_rate_models.py": "energy_rate_models", 
    "models/waste_rate_models.py": "waste_rate_models",
    "models/water_rate_models.py": "water_rate_models",
}

def get_model_function(model_name: str):
    """Get Python function for a given RDF model name"""
    return MODEL_REGISTRY.get(model_name)

def get_all_available_models():
    """Get list of all available model names"""
    return list(MODEL_REGISTRY.keys())

def validate_rdf_alignment():
    """Validate that all RDF-defined models have corresponding Python implementations"""
    rdf_models = [
        "GHGEmissionIntensityModel",
        "GridElectricityRateModel", 
        "RenewableEnergyRateModel",
        "HazardousWasteRecyclingRateModel",
        "HighStressWaterConsumptionRateModel",
        "HighStressWaterWithdrawalRateModel"
    ]
    
    missing_models = []
    for model in rdf_models:
        if model not in MODEL_REGISTRY:
            missing_models.append(model)
    
    return {
        "total_rdf_models": len(rdf_models),
        "implemented_models": len(MODEL_REGISTRY),
        "missing_models": missing_models,
        "alignment_complete": len(missing_models) == 0
    } 