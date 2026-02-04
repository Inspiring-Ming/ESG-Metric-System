"""
Energy Rate Models Implementation

This module implements energy percentage calculation models
as specified in the ESG Knowledge Graph RDF.

Models:
- Grid Electricity Rate Model
- Renewable Energy Rate Model
"""

def calculate_grid_electricity_rate(grid_electricity, total_energy):
    """
    Calculate Grid Electricity Rate
    
    Args:
        grid_electricity (float): Energy consumed from grid electricity in GJ
        total_energy (float): Total energy consumed in GJ
        
    Returns:
        float: Grid electricity percentage (0-100)
        None: If total_energy is <= 0 or inputs are invalid
        
    Raises:
        ValueError: If any input is negative
        TypeError: If inputs are not numeric
    """
    
    # Type validation
    try:
        grid_electricity = float(grid_electricity)
        total_energy = float(total_energy)
    except (TypeError, ValueError):
        raise TypeError("All inputs must be numeric values")
    
    # Value validation
    if grid_electricity < 0:
        raise ValueError("Grid electricity cannot be negative")
    if total_energy < 0:
        raise ValueError("Total energy cannot be negative")
    
    # Handle zero total energy case
    if total_energy == 0:
        return None
    
    # Calculate percentage
    percentage = (grid_electricity / total_energy) * 100
    
    # Ensure percentage doesn't exceed 100%
    return min(percentage, 100.0)


def calculate_renewable_energy_rate(renewable_energy, total_energy):
    """
    Calculate Renewable Energy Rate
    
    Args:
        renewable_energy (float): Energy consumed from renewable sources in GJ
        total_energy (float): Total energy consumed in GJ
        
    Returns:
        float: Renewable energy percentage (0-100)
        None: If total_energy is <= 0 or inputs are invalid
        
    Raises:
        ValueError: If any input is negative
        TypeError: If inputs are not numeric
    """
    
    # Type validation
    try:
        renewable_energy = float(renewable_energy)
        total_energy = float(total_energy)
    except (TypeError, ValueError):
        raise TypeError("All inputs must be numeric values")
    
    # Value validation
    if renewable_energy < 0:
        raise ValueError("Renewable energy cannot be negative")
    if total_energy < 0:
        raise ValueError("Total energy cannot be negative")
    
    # Handle zero total energy case
    if total_energy == 0:
        return None
    
    # Calculate percentage
    percentage = (renewable_energy / total_energy) * 100
    
    # Ensure percentage doesn't exceed 100%
    return min(percentage, 100.0)


# Model metadata for validation
MODELS = {
    "Grid Electricity Rate Model": {
        "function": calculate_grid_electricity_rate,
        "inputs": ["grid_electricity", "total_energy"],
        "formula": "(grid_electricity / total_energy) * 100",
        "unit": "percentage"
    },
    "Renewable Energy Rate Model": {
        "function": calculate_renewable_energy_rate,
        "inputs": ["renewable_energy", "total_energy"],
        "formula": "(renewable_energy / total_energy) * 100",
        "unit": "percentage"
    }
} 