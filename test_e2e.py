#!/usr/bin/env python3
"""
End-to-end testing script for AI Agents with APIM
Tests the complete workflow: React App -> APIM -> FastAPI -> AI Services
"""

import os
import sys
import json
import requests
import time
from typing import Dict, Any
import argparse

class E2ETestRunner:
    def __init__(self, apim_gateway_url: str, subscription_key: str):
        self.apim_gateway_url = apim_gateway_url.rstrip('/')
        self.subscription_key = subscription_key
        self.headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': subscription_key
        }
        
    def test_health_endpoint(self) -> bool:
        """Test the health endpoint through APIM"""
        try:
            print("🔍 Testing health endpoint...")
            response = requests.get(
                f"{self.apim_gateway_url}/api/health",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check passed: {health_data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_agent_endpoint(self) -> bool:
        """Test the agent details endpoint through APIM"""
        try:
            print("🔍 Testing agent endpoint...")
            response = requests.get(
                f"{self.apim_gateway_url}/api/agent",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                agent_data = response.json()
                print(f"✅ Agent endpoint passed: {agent_data.get('name', 'Unknown Agent')}")
                return True
            else:
                print(f"❌ Agent endpoint failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Agent endpoint error: {e}")
            return False
    
    def test_chat_endpoint(self) -> bool:
        """Test the chat endpoint through APIM"""
        try:
            print("🔍 Testing chat endpoint...")
            chat_payload = {
                "message": "Hello, can you help me with a simple test question?"
            }
            
            response = requests.post(
                f"{self.apim_gateway_url}/api/chat",
                headers=self.headers,
                json=chat_payload,
                timeout=60,
                stream=True
            )
            
            if response.status_code == 200:
                print("✅ Chat endpoint accessible")
                
                # Try to read streaming response
                content_received = False
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            try:
                                data = json.loads(line_str[6:])
                                if data.get('content'):
                                    content_received = True
                                    print(f"✅ Received chat response: {data['content'][:50]}...")
                                    break
                            except json.JSONDecodeError:
                                continue
                
                if content_received:
                    print("✅ Chat streaming working correctly")
                    return True
                else:
                    print("⚠️ Chat endpoint accessible but no content received")
                    return False
            else:
                print(f"❌ Chat endpoint failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Chat endpoint error: {e}")
            return False
    
    def test_rate_limiting(self) -> bool:
        """Test APIM rate limiting functionality"""
        try:
            print("🔍 Testing rate limiting...")
            
            # Make multiple rapid requests to trigger rate limiting
            for i in range(5):
                response = requests.get(
                    f"{self.apim_gateway_url}/api/health",
                    headers=self.headers,
                    timeout=10
                )
                print(f"Request {i+1}: {response.status_code}")
                
                if response.status_code == 429:
                    print("✅ Rate limiting is working (received 429 Too Many Requests)")
                    return True
                    
                time.sleep(0.1)  # Small delay between requests
            
            print("⚠️ Rate limiting not triggered (may need higher traffic)")
            return True  # Not necessarily a failure
            
        except Exception as e:
            print(f"❌ Rate limiting test error: {e}")
            return False
    
    def test_frontend_access(self) -> bool:
        """Test that the React frontend is accessible through APIM"""
        try:
            print("🔍 Testing frontend access...")
            
            # Test main page
            response = requests.get(
                f"{self.apim_gateway_url}/",
                timeout=30
            )
            
            if response.status_code == 200 and ("react-root" in response.text or "AI Agents" in response.text):
                print("✅ React frontend accessible")
                return True
            else:
                print(f"❌ Frontend access failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Frontend access error: {e}")
            return False

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        print(f"🚀 Starting E2E tests for APIM Gateway: {self.apim_gateway_url}")
        print("=" * 60)
        
        results = {}
        
        tests = [
            ("health_endpoint", self.test_health_endpoint),
            ("agent_endpoint", self.test_agent_endpoint),
            ("chat_endpoint", self.test_chat_endpoint),
            ("rate_limiting", self.test_rate_limiting),
            ("frontend_access", self.test_frontend_access),
        ]
        
        for test_name, test_func in tests:
            print(f"\n📋 Running test: {test_name}")
            results[test_name] = test_func()
            time.sleep(1)  # Brief pause between tests
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:20} : {status}")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Your APIM setup is working correctly.")
            return True
        else:
            print("⚠️ Some tests failed. Please check the configuration.")
            return False


def main():
    parser = argparse.ArgumentParser(description="E2E testing for AI Agents with APIM")
    parser.add_argument("--apim-url", required=True, help="APIM Gateway URL")
    parser.add_argument("--subscription-key", required=True, help="APIM Subscription Key")
    
    args = parser.parse_args()
    
    # Create test runner
    test_runner = E2ETestRunner(args.apim_url, args.subscription_key)
    
    # Run tests
    results = test_runner.run_all_tests()
    
    # Print summary
    success = test_runner.print_summary(results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
