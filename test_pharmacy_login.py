#!/usr/bin/env python3
"""
Quick test script to verify pharmacy authentication works
Run this before testing the full app to ensure the functions work correctly
"""

import pandas as pd
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the authentication function
from app import authenticate_pharmacy, load_pharmacies

def test_pharmacy_authentication():
    """Test pharmacy login with sample credentials"""
    print("🧪 Testing Pharmacy Authentication\n")
    
    # Test credentials from CSV
    test_cases = [
        {
            "name": "Pharmacie de la Paix - Kimironko",
            "phone": "+250788123456",
            "expected": True
        },
        {
            "name": "Pharmacie Conseil - City Center",
            "phone": "+250788234567",
            "expected": True
        },
        {
            "name": "Wrong Pharmacy",
            "phone": "+250999999999",
            "expected": False
        },
        {
            "name": "Pharmacie de la Paix - Kimironko",
            "phone": "+250999999999",  # Wrong phone
            "expected": False
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['name']} / {test['phone']}")
        result = authenticate_pharmacy(test['name'], test['phone'])
        
        if (result is not None) == test['expected']:
            print(f"  ✅ PASS - Authentication {'succeeded' if result else 'failed'} as expected")
            if result is not None:
                print(f"     Found: {result['Pharmacy_Name']}")
        else:
            print(f"  ❌ FAIL - Expected {test['expected']}, got {result is not None}")
            all_passed = False
        print()
    
    return all_passed

def test_load_data():
    """Test that data files can be loaded"""
    print("🧪 Testing Data Loading\n")
    
    try:
        medicines_df = pd.read_csv('data/emergency_medicines.csv')
        pharmacies_df = pd.read_csv('data/emergency_pharmacies.csv')
        
        print(f"✅ Medicines loaded: {len(medicines_df)} medicines")
        print(f"✅ Pharmacies loaded: {len(pharmacies_df)} pharmacies")
        print()
        
        # Check that pharmacy has required columns
        required_cols = ['Pharmacy_Name', 'Phone', 'EpiPen', 'Salbutamol_Inhaler']
        missing = [col for col in required_cols if col not in pharmacies_df.columns]
        
        if missing:
            print(f"❌ Missing columns: {missing}")
            return False
        else:
            print("✅ All required columns present")
            print()
        
        return True
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("FindMyMed - Pharmacy System Test")
    print("=" * 50)
    print()
    
    data_ok = test_load_data()
    auth_ok = test_pharmacy_authentication() if data_ok else False
    
    print("=" * 50)
    if data_ok and auth_ok:
        print("✅ All tests passed! Ready to test the app.")
        print("\nTo run the app:")
        print("  streamlit run app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 50)

