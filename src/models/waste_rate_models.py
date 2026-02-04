"""
Waste Rate Models Implementation

This module implements waste percentage calculation models
as specified in the ESG Knowledge Graph RDF.

Models:
- Hazardous Waste Recycling Rate Model
"""

def calculate_hazardous_waste_recycling_rate(recycled_hazardous_waste, total_hazardous_waste):
    """
    Calculate Hazardous Waste Recycling Rate
    
    Args:
        recycled_hazardous_waste (float): Amount of hazardous waste recycled in metric tonnes
        total_hazardous_waste (float): Total amount of hazardous waste generated in metric tonnes
        
    Returns:
        float: Hazardous waste recycling percentage (0-100)
        None: If total_hazardous_waste is <= 0 or inputs are invalid
        
    Raises:
        ValueError: If any input is negative
        TypeError: If inputs are not numeric
    """
    
    # Type validation
    try:
        recycled_hazardous_waste = float(recycled_hazardous_waste)
        total_hazardous_waste = float(total_hazardous_waste)
    except (TypeError, ValueError):
        raise TypeError("All inputs must be numeric values")
    
    # Value validation
    if recycled_hazardous_waste < 0:
        raise ValueError("Recycled hazardous waste cannot be negative")
    if total_hazardous_waste < 0:
        raise ValueError("Total hazardous waste cannot be negative")
    
    # Handle zero total waste case
    if total_hazardous_waste == 0:
        return None
    
    # Calculate percentage
    percentage = (recycled_hazardous_waste / total_hazardous_waste) * 100
    
    # Ensure percentage doesn't exceed 100%
    return min(percentage, 100.0)


# Model metadata for validation
MODELS = {
    "Hazardous Waste Recycling Rate Model": {
        "function": calculate_hazardous_waste_recycling_rate,
        "inputs": ["recycled_hazardous_waste", "total_hazardous_waste"],
        "formula": "(recycled_hazardous_waste / total_hazardous_waste) * 100",
        "unit": "percentage"
    }
} 