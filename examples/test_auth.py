#!/usr/bin/env python3
"""Test script to verify Grafana API authentication"""
import os
import sys
import requests

def test_auth():
    host = os.getenv("GRAFANA_HOST", "localhost")
    port = int(os.getenv("GRAFANA_PORT", "3000"))
    api_key = os.getenv("GRAFANA_API_KEY")
    auth_user = os.getenv("GRAFANA_USER")
    auth_pass = os.getenv("GRAFANA_PASSWORD")
    
    url = f"http://{host}:{port}/api/health"
    
    print("Testing Grafana API authentication...")
    print(f"URL: {url}")
    print()
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    auth = None
    
    if api_key:
        api_key = api_key.strip()
        # Use X-Grafana-API-Key header (traditional Grafana format)
        headers["X-Grafana-API-Key"] = api_key
        print(f"Using API Key authentication")
        print(f"  Key preview: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
        print(f"  Key length: {len(api_key)}")
        print(f"  Header: X-Grafana-API-Key")
    elif auth_user and auth_pass:
        auth = (auth_user, auth_pass)
        print(f"Using Basic Auth")
        print(f"  User: {auth_user}")
    else:
        print("ERROR: No authentication method provided!")
        print("Set either GRAFANA_API_KEY or GRAFANA_USER/GRAFANA_PASSWORD")
        return 1
    
    print()
    print("Testing connection...")
    
    try:
        # First test health endpoint (doesn't require auth)
        health_response = requests.get(f"http://{host}:{port}/api/health", timeout=5)
        print(f"✓ Grafana is reachable (health check: {health_response.status_code})")
    except Exception as e:
        print(f"✗ Cannot reach Grafana: {e}")
        return 1
    
    # Test authenticated endpoint
    try:
        response = requests.get(
            f"http://{host}:{port}/api/datasources",
            headers=headers,
            auth=auth,
            timeout=5
        )
        
        print(f"\nAuthentication test result: HTTP {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Authentication successful!")
            datasources = response.json()
            print(f"  Found {len(datasources)} datasources")
            return 0
        elif response.status_code == 401:
            print("✗ Authentication failed (401 Unauthorized)")
            try:
                error = response.json()
                if "message" in error:
                    print(f"  Error message: {error['message']}")
                print(f"  Full response: {json.dumps(error, indent=2)}")
            except:
                print(f"  Response: {response.text}")
            
            print("\nTroubleshooting:")
            if api_key:
                print("  - Verify the API key in Grafana UI: Configuration > API Keys")
                print("  - Check that the key has 'Admin' role (not Viewer/Editor)")
                print("  - Ensure the key hasn't expired")
                print("  - Service account tokens (glsa_*) might need the service account to be active")
                print("  - Try creating a NEW API key (not service account token)")
                print("  - Make sure you copied the ENTIRE key (they're very long!)")
                print("  - Alternative: Use basic auth with GRAFANA_USER/GRAFANA_PASSWORD")
                print("\n  To test basic auth:")
                print("    export GRAFANA_USER='admin'")
                print("    export GRAFANA_PASSWORD='admin'")
                print("    python examples/test_auth.py")
            else:
                print("  - Check username and password")
                print("  - Default Grafana credentials: admin/admin (change on first login)")
            
            return 1
        else:
            print(f"✗ Unexpected status code: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return 1
            
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return 1

if __name__ == "__main__":
    import json
    sys.exit(test_auth())

