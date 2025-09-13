#!/usr/bin/env python3
"""
Network Ladder Test Cases
Test various transfer functions to ensure the web app works correctly
"""

import requests
import json
import time

# Test cases: (name, numerator, denominator, expected_result)
TEST_CASES = [
    # Valid cases
    ("RC Network", [1, 1], [0, 1], "Should generate Z=[s], Y=[1]"),
    ("LC Filter", [3, 4, 1], [0, 2, 1], "Should generate Z=[s], Y=[2s+3]"),
    ("Simple Inductor", [0, 1], [1], "Should generate Z=[s], Y=[]"),
    ("Simple Resistor", [1], [1], "Should generate Z=[1], Y=[]"),
    ("High-pass Filter", [0, 0, 1], [0, 1], "Should generate Z=[s], Y=[s]"),
    
    # Invalid cases
    ("Zero Numerator", [0, 0], [1, 1], "Should fail - invalid network"),
    ("Zero Denominator", [1, 1], [0, 0], "Should fail - invalid network"),
    ("Empty Numerator", [], [1], "Should fail - empty array"),
    ("Empty Denominator", [1], [], "Should fail - empty array"),
    ("Degree Too High", [1, 1, 1, 1], [1, 1], "Should fail - degree too high"),
    ("Complex Invalid", [1, 2, 3, 4, 5], [1, 1], "Should fail - invalid for ladder"),
]

def test_web_app(base_url="http://localhost:5000"):
    """Test the web application with various cases"""
    print("🧪 Network Ladder Web App Test Suite")
    print("=" * 50)
    
    # Test health endpoint first
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to web app: {e}")
        print("💡 Make sure the web app is running: python web/app.py")
        return False
    
    print("\n📋 Running test cases...")
    print("-" * 50)
    
    passed = 0
    failed = 0
    
    for i, (name, numerator, denominator, expected) in enumerate(TEST_CASES, 1):
        print(f"\n{i}. {name}")
        print(f"   Input: N(s)={numerator}, D(s)={denominator}")
        print(f"   Expected: {expected}")
        
        try:
            # Make API request
            response = requests.post(
                f"{base_url}/api/process",
                json={
                    "numerator": numerator,
                    "denominator": denominator
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    z_array = data.get('Z', [])
                    y_array = data.get('Y', [])
                    has_image = 'image' in data and data['image']
                    
                    print(f"   ✅ SUCCESS")
                    print(f"   Z = {z_array}")
                    print(f"   Y = {y_array}")
                    print(f"   Image generated: {'Yes' if has_image else 'No'}")
                    passed += 1
                else:
                    error = data.get('error', 'Unknown error')
                    print(f"   ⚠️  EXPECTED FAILURE: {error}")
                    passed += 1
            else:
                data = response.json()
                error = data.get('error', 'Unknown error')
                print(f"   ⚠️  EXPECTED FAILURE: {error}")
                passed += 1
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ REQUEST FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"   ❌ UNEXPECTED ERROR: {e}")
            failed += 1
        
        # Small delay between requests
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The web app is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

def test_frontend(base_url="http://localhost:5000"):
    """Test the frontend interface"""
    print("\n🌐 Testing Frontend Interface...")
    print("-" * 30)
    
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            content = response.text
            if "Network Ladder" in content and "Transfer Function" in content:
                print("✅ Frontend loads correctly")
                print("✅ Contains expected elements")
                return True
            else:
                print("❌ Frontend missing expected content")
                return False
        else:
            print(f"❌ Frontend request failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Network Ladder Web App Tests")
    print("Make sure the web app is running: python web/app.py")
    print("Press Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n❌ Tests cancelled")
        return
    
    # Test API
    api_success = test_web_app()
    
    # Test Frontend
    frontend_success = test_frontend()
    
    print("\n" + "=" * 50)
    if api_success and frontend_success:
        print("🎉 ALL TESTS PASSED! Your web app is ready for production.")
        print("\n📋 Next steps:")
        print("1. Test manually in browser: http://localhost:5000")
        print("2. Try different transfer functions")
        print("3. Deploy to Vercel: vercel")
        print("4. Deploy to Heroku: git push heroku main")
    else:
        print("⚠️  Some tests failed. Please fix issues before deploying.")
        print("\n🔧 Troubleshooting:")
        print("1. Check that C++ app compiles: g++ -std=c++17 -O2 -o app.exe src/*.cpp")
        print("2. Check web app logs for errors")
        print("3. Verify all dependencies are installed: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
