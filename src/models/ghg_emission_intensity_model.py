"""
GHG Emission Intensity Model Implementation

This module implements the GHG Emission Intensity calculation model
as specified in the ESG Knowledge Graph RDF.

Model: GHGEmissionIntensityModel
Formula: GHG_Intensity = (Scope1_Emissions + Scope2_Emissions) / Revenue
Unit: tons CO2e per million USD
"""

def calculate_ghg_emission_intensity(scope1_emissions, scope2_emissions, revenue):
    """
    Calculate GHG Emission Intensity
    
    Args:
        scope1_emissions (float): Direct emissions in tons CO2e
        scope2_emissions (float): Indirect emissions in tons CO2e  
        revenue (float): Total revenue in millions of USD
        
    Returns:
        float: GHG intensity in tons CO2e per million USD
        None: If revenue is <= 0 or inputs are invalid
        
    Raises:
        ValueError: If any input is negative (except for zero revenue)
        TypeError: If inputs are not numeric
    """
    
    # Type validation
    try:
        scope1_emissions = float(scope1_emissions)
        scope2_emissions = float(scope2_emissions)
        revenue = float(revenue)
    except (TypeError, ValueError):
        raise TypeError("All inputs must be numeric values")
    
    # Value validation
    if scope1_emissions < 0:
        raise ValueError("Scope 1 emissions cannot be negative")
    if scope2_emissions < 0:
        raise ValueError("Scope 2 emissions cannot be negative")
    if revenue < 0:
        raise ValueError("Revenue cannot be negative")
    
    # Handle zero revenue case
    if revenue == 0:
        return None
    
    # Calculate total emissions
    total_emissions = scope1_emissions + scope2_emissions
    
    # Calculate intensity (revenue is already in millions)
    ghg_intensity = total_emissions / revenue
    
    return ghg_intensity


def validate_inputs(scope1_emissions, scope2_emissions, revenue):
    """
    Validate inputs for GHG intensity calculation
    
    Args:
        scope1_emissions: Scope 1 emissions value
        scope2_emissions: Scope 2 emissions value
        revenue: Revenue value
        
    Returns:
        dict: Validation result with 'valid' boolean and 'errors' list
    """
    errors = []
    
    # Check if inputs are numeric
    for name, value in [('scope1_emissions', scope1_emissions), 
                       ('scope2_emissions', scope2_emissions), 
                       ('revenue', revenue)]:
        try:
            float(value)
        except (TypeError, ValueError):
            errors.append(f"{name} must be a numeric value")
    
    # If not numeric, return early
    if errors:
        return {'valid': False, 'errors': errors}
    
    # Convert to float for further validation
    scope1 = float(scope1_emissions)
    scope2 = float(scope2_emissions)
    rev = float(revenue)
    
    # Check for negative values
    if scope1 < 0:
        errors.append("Scope 1 emissions cannot be negative")
    if scope2 < 0:
        errors.append("Scope 2 emissions cannot be negative")
    if rev < 0:
        errors.append("Revenue cannot be negative")
    
    return {'valid': len(errors) == 0, 'errors': errors}


def get_model_metadata():
    """
    Get metadata about the GHG Emission Intensity model
    
    Returns:
        dict: Model metadata including formula, units, and description
    """
    return {
        'model_name': 'GHGEmissionIntensityModel',
        'formula': '(scope1_emissions + scope2_emissions) / revenue',
        'mathematical_expression': 'GHG_Intensity = (Scope1_Emissions + Scope2_Emissions) / Revenue',
        'input_units': {
            'scope1_emissions': 'tons CO2e',
            'scope2_emissions': 'tons CO2e', 
            'revenue': 'million USD'
        },
        'output_unit': 'tons CO2e per million USD',
        'calculation_type': 'intensity_ratio',
        'description': 'GHG Intensity (tons CO2e per million USD) = (CO2DIRECTSCOPE1 (tons) + CO2INDIRECTSCOPE2 (tons)) / Revenue (in million USD)',
        'required_inputs': ['scope1_emissions', 'scope2_emissions', 'revenue'],
        'rdf_reference': 'esg:GHGEmissionIntensityModel'
    }


# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_cases = [
        {'scope1': 1000, 'scope2': 500, 'revenue': 100, 'expected': 15.0},
        {'scope1': 0, 'scope2': 1000, 'revenue': 50, 'expected': 20.0},
        {'scope1': 2000, 'scope2': 0, 'revenue': 200, 'expected': 10.0},
    ]
    
    print("Testing GHG Emission Intensity Model:")
    print("=" * 50)
    
    for i, case in enumerate(test_cases):
        try:
            result = calculate_ghg_emission_intensity(case['scope1'], case['scope2'], case['revenue'])
            print(f"Test {i+1}: Scope1={case['scope1']}, Scope2={case['scope2']}, Revenue={case['revenue']}M")
            print(f"  Result: {result:.2f} tons CO2e per million USD")
            print(f"  Expected: {case['expected']} tons CO2e per million USD")
            print(f"  Status: {'PASS' if abs(result - case['expected']) < 0.01 else 'FAIL'}")
            print()
        except Exception as e:
            print(f"Test {i+1}: ERROR - {e}")
            print()
    
    # Test validation
    print("Testing input validation:")
    print("-" * 30)
    validation_tests = [
        {'scope1': -100, 'scope2': 500, 'revenue': 100},  # Negative scope1
        {'scope1': 1000, 'scope2': -200, 'revenue': 100}, # Negative scope2
        {'scope1': 1000, 'scope2': 500, 'revenue': -50},  # Negative revenue
        {'scope1': 1000, 'scope2': 500, 'revenue': 0},    # Zero revenue
        {'scope1': 'abc', 'scope2': 500, 'revenue': 100}, # Non-numeric
    ]
    
    for i, case in enumerate(validation_tests):
        validation = validate_inputs(case['scope1'], case['scope2'], case['revenue'])
        print(f"Validation Test {i+1}: {case}")
        print(f"  Valid: {validation['valid']}")
        if not validation['valid']:
            print(f"  Errors: {validation['errors']}")
        print() 