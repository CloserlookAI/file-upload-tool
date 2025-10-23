#!/usr/bin/env python3
"""
Test script to verify Digital Ocean Spaces upload and public access
"""

import os
import sys
from pathlib import Path

# Load .env file
env_path = Path('.env')
if env_path.exists():
    print("Loading .env file...")
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                if value:
                    os.environ[key] = value

from do_uploader import DOSpacesUploader

def test_upload():
    """Test file upload and verify public access"""
    
    print("\n" + "="*60)
    print("  DIGITAL OCEAN SPACES - UPLOAD TEST")
    print("="*60 + "\n")
    
    try:
        # Initialize uploader
        print("1. Initializing uploader...")
        uploader = DOSpacesUploader()
        print(f"   ✓ Connected to Space: {uploader.do_spaces_bucket}")
        print(f"   ✓ Endpoint: {uploader.do_spaces_endpoint}")
        print(f"   ✓ CDN URL: {uploader.do_spaces_files_url or 'Not set'}")
        
        # Create a test file
        print("\n2. Creating test file...")
        test_file = Path('test_public_access.txt')
        test_content = f"Test file created at {uploader.do_spaces_bucket}\nThis file should be publicly accessible."
        test_file.write_text(test_content)
        print(f"   ✓ Test file created: {test_file}")
        
        # Upload the file
        print("\n3. Uploading file with public access...")
        result = uploader.upload_file(
            file_path=str(test_file),
            space_path=None,
            make_public=True  # Explicitly set to public
        )
        
        if result['success']:
            print(f"   ✓ Upload successful!")
            print(f"   ✓ URL: {result['url']}")
            print(f"   ✓ File size: {result['size_bytes']} bytes")
            
            # Test public access
            print("\n4. Testing public access...")
            import requests
            
            try:
                response = requests.get(result['url'], timeout=10)
                print(f"   ✓ HTTP Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✓ File is PUBLICLY ACCESSIBLE!")
                    print(f"   ✓ Content length: {len(response.content)} bytes")
                    print(f"\n   SUCCESS! Files are uploading with public access.")
                elif response.status_code == 403:
                    print(f"   ✗ ACCESS DENIED (403)")
                    print(f"\n   PROBLEM: File uploaded but not publicly accessible")
                    print(f"\n   SOLUTION:")
                    print(f"   1. Go to: https://cloud.digitalocean.com/spaces/{uploader.do_spaces_bucket}")
                    print(f"   2. Click 'Settings' tab")
                    print(f"   3. Under 'File Listing', change to 'Public'")
                    print(f"   4. Save and try again")
                else:
                    print(f"   ? Unexpected status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ✗ Request failed: {str(e)}")
            
            # Check if we can list the file
            print("\n5. Verifying file in Space...")
            files = uploader.list_files(max_files=10)
            test_files = [f for f in files if 'test_public_access' in f['key']]
            if test_files:
                print(f"   ✓ Found {len(test_files)} test file(s) in Space")
                for f in test_files:
                    print(f"     - {f['key']}")
            
            print("\n6. Cleanup...")
            if input("   Delete test file from Space? (y/n): ").lower() == 'y':
                uploader.delete_file(result['space_key'])
                print("   ✓ Test file deleted from Space")
            
            test_file.unlink()
            print("   ✓ Local test file deleted")
            
        else:
            print(f"   ✗ Upload failed: {result['error']}")
            return False
        
        print("\n" + "="*60)
        print("  TEST COMPLETE")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_upload()
    sys.exit(0 if success else 1)

