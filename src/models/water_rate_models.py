"""
Water Rate Models Implementation

This module implements water percentage calculation models
as specified in the ESG Knowledge Graph RDF.

Models:
- High Stress Water Consumption Rate Model
- High Stress Water Withdrawal Rate Model
"""

def calculate_high_stress_water_consumption_rate(high_stress_water_consumed, total_water_consumed):
    """
    Calculate High Stress Water Consumption Rate
    
    Args:
        high_stress_water_consumed (float): Water consumed in high stress regions in cubic meters
        total_water_consumed (float): Total water consumed in cubic meters
        
    Returns:
        float: High stress water consumption percentage (0-100)
        None: If total_water_consumed is <= 0 or inputs are invalid
        
    Raises:
        ValueError: If any input is negative
        TypeError: If inputs are not numeric
    """
    
    # Type validation
    try:
        high_stress_water_consumed = float(high_stress_water_consumed)
        total_water_consumed = float(total_water_consumed)
    except (TypeError, ValueError):
        raise TypeError("All inputs must be numeric values")
    
    # Value validation
    if high_stress_water_consumed < 0:
        raise ValueError("High stress water consumed cannot be negative")
    if total_water_consumed < 0:
        raise ValueError("Total water consumed cannot be negative")
    
    # Handle zero total water case
    if total_water_consumed == 0:
        return None
    
    # Calculate percentage
    percentage = (high_stress_water_consumed / total_water_consumed) * 100
    
    # Ensure percentage doesn't exceed 100%
    return min(percentage, 100.0)


def calculate_high_stress_water_withdrawal_rate(high_stress_water_withdrawn, total_water_withdrawn):
    """
    Calculate High Stress Water Withdrawal Rate
    
    Args:
        high_stress_water_withdrawn (float): Water withdrawn in high stress regions in cubic meters
        total_water_withdrawn (float): Total water withdrawn in cubic meters
        
    Returns:
        float: High stress water withdrawal percentage (0-100)
        None: If total_water_withdrawn is <= 0 or inputs are invalid
        
    Raises:
        ValueError: If any input is negative
        TypeError: If inputs are not numeric
    """
    
    # Type validation
    try:
        high_stress_water_withdrawn = float(high_stress_water_withdrawn)
        total_water_withdrawn = float(total_water_withdrawn)
    except (TypeError, ValueError):
        raise TypeError("All inputs must be numeric values")
    
    # Value validation
    if high_stress_water_withdrawn < 0:
        raise ValueError("High stress water withdrawn cannot be negative")
    if total_water_withdrawn < 0:
        raise ValueError("Total water withdrawn cannot be negative")
    
    # Handle zero total water case
    if total_water_withdrawn == 0:
        return None
    
    # Calculate percentage
    percentage = (high_stress_water_withdrawn / total_water_withdrawn) * 100
    
    # Ensure percentage doesn't exceed 100%
    return min(percentage, 100.0)


# Model metadata for validation
MODELS = {
    "High Stress Water Consumption Rate Model": {
        "function": calculate_high_stress_water_consumption_rate,
        "inputs": ["high_stress_water_consumed", "total_water_consumed"],
        "formula": "(high_stress_water_consumed / total_water_consumed) * 100",
        "unit": "percentage"
    },
    "High Stress Water Withdrawal Rate Model": {
        "function": calculate_high_stress_water_withdrawal_rate,
        "inputs": ["high_stress_water_withdrawn", "total_water_withdrawn"],
        "formula": "(high_stress_water_withdrawn / total_water_withdrawn) * 100",
        "unit": "percentage"
    }
} 