#!/usr/bin/env python
"""
Test script for currency update functionality
"""
import requests
import json

def test_currency_update():
    """Test the currency update endpoint"""
    
    # Test data
    test_data = {
        'currency_code': 'USD',
        'currency_symbol': '$'
    }
    
    # URL for the currency update endpoint
    url = 'http://127.0.0.1:8000/dashboard/update-currency/'
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': 'test-token'  # This will be replaced by actual CSRF token
    }
    
    try:
        print("Testing currency update endpoint...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        # Make the request
        response = requests.post(url, json=test_data, headers=headers)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Data: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Response Text: {response.text}")
        else:
            print(f"Error Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Connection Error: Make sure the Django server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_currency_update() 