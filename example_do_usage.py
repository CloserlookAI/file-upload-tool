#!/usr/bin/env python3
"""
Example usage of DOSpacesUploader as a Python library

This demonstrates how to use the DOSpacesUploader class programmatically
in your own Python scripts.
"""

import os
from do_uploader import DOSpacesUploader


def example_usage():
    """Example usage of DOSpacesUploader"""
    
    # Set environment variables (or use .env file)
    # os.environ['DO_SPACES_KEY'] = 'your_key'
    # os.environ['DO_SPACES_SECRET'] = 'your_secret'
    # os.environ['DO_SPACES_ENDPOINT'] = 'nyc3.digitaloceanspaces.com'
    # os.environ['DO_SPACES_BUCKET'] = 'your-space'
    # os.environ['DO_SPACES_REGION'] = 'nyc3'
    
    try:
        # Initialize uploader
        print("Initializing Digital Ocean Spaces Uploader...")
        uploader = DOSpacesUploader()
        
        # Example 1: Upload a local file (public by default)
        print("\n=== Example 1: Upload Local File (Public) ===")
        result = uploader.upload_file(
            file_path='example.txt',
            space_path=None,  # Use default path
            make_public=True
        )
        
        if result['success']:
            print(f"✓ File uploaded successfully!")
            print(f"  URL: {result['url']}")
            print(f"  Space Key: {result['space_key']}")
            print(f"  Size: {result['size_bytes']} bytes")
        else:
            print(f"✗ Upload failed: {result['error']}")
        
        # Example 2: Upload a private file
        print("\n=== Example 2: Upload Private File ===")
        result = uploader.upload_file(
            file_path='secret.txt',
            space_path='private/secret.txt',
            make_public=False
        )
        
        if result['success']:
            print(f"✓ Private file uploaded!")
            print(f"  URL: {result['url']} (requires authentication)")
        
        # Example 3: Upload from URL
        print("\n=== Example 3: Upload from URL ===")
        result = uploader.upload_from_url(
            url='https://example.com/sample.pdf',
            filename='downloaded-file.pdf',
            space_path='documents/downloaded-file.pdf',
            make_public=True
        )
        
        if result['success']:
            print(f"✓ File uploaded from URL!")
            print(f"  Source: {result['source_url']}")
            print(f"  URL: {result['url']}")
        else:
            print(f"✗ Upload failed: {result['error']}")
        
        # Example 4: List files in Space
        print("\n=== Example 4: List Files ===")
        files = uploader.list_files(prefix='documents/', max_files=10)
        
        if files:
            print(f"Found {len(files)} files:")
            for file in files:
                print(f"  • {file['key']} ({file['size']} bytes)")
                print(f"    Modified: {file['last_modified']}")
                print(f"    URL: {file['url']}")
        else:
            print("No files found.")
        
        # Example 5: Upload multiple files
        print("\n=== Example 5: Upload Multiple Files ===")
        files_to_upload = ['file1.txt', 'file2.pdf', 'image.jpg']
        
        results = []
        for file_path in files_to_upload:
            if os.path.exists(file_path):
                result = uploader.upload_file(file_path)
                results.append(result)
        
        successful = [r for r in results if r.get('success')]
        print(f"Uploaded {len(successful)}/{len(results)} files successfully")
        
        # Example 6: Upload to organized folder structure
        print("\n=== Example 6: Organized Upload ===")
        from datetime import datetime
        
        today = datetime.now().strftime('%Y/%m/%d')
        result = uploader.upload_file(
            file_path='report.pdf',
            space_path=f'reports/{today}/report.pdf',
            make_public=True
        )
        
        if result['success']:
            print(f"✓ Uploaded to organized path: {result['space_key']}")
        
        # Example 7: Delete a file
        print("\n=== Example 7: Delete File ===")
        result = uploader.delete_file('old-file.pdf')
        
        if result['success']:
            print(f"✓ File deleted: {result['space_key']}")
        else:
            print(f"✗ Delete failed: {result['error']}")
        
        # Example 8: CDN URL usage
        print("\n=== Example 8: CDN URL ===")
        # If you have DO_SPACES_FILES_URL set (CDN enabled)
        # The URLs will automatically use the CDN endpoint
        result = uploader.upload_file('logo.png', make_public=True)
        if result['success']:
            print(f"✓ File URL (may be CDN): {result['url']}")
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("\nMake sure to set these environment variables:")
        print("  - DO_SPACES_KEY")
        print("  - DO_SPACES_SECRET")
        print("  - DO_SPACES_ENDPOINT")
        print("  - DO_SPACES_BUCKET")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    example_usage()

