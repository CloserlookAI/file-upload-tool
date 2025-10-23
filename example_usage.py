#!/usr/bin/env python3
"""
Example usage of S3Uploader as a Python library

This demonstrates how to use the S3Uploader class programmatically
in your own Python scripts.
"""

import os
from uploader import S3Uploader


def example_usage():
    """Example usage of S3Uploader"""
    
    # Set environment variables (or use .env file)
    # os.environ['AWS_ACCESS_KEY_ID'] = 'your_key'
    # os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_secret'
    # os.environ['S3_BUCKET_NAME'] = 'your-bucket'
    # os.environ['AWS_REGION'] = 'us-east-1'
    
    try:
        # Initialize uploader
        print("Initializing S3 Uploader...")
        uploader = S3Uploader()
        
        # Example 1: Upload a local file
        print("\n=== Example 1: Upload Local File ===")
        result = uploader.upload_file(
            file_path='example.txt',
            s3_path=None,  # Use default path
            make_public=False
        )
        
        if result['success']:
            print(f"✓ File uploaded successfully!")
            print(f"  URL: {result['url']}")
            print(f"  S3 Key: {result['s3_key']}")
            print(f"  Size: {result['size_bytes']} bytes")
        else:
            print(f"✗ Upload failed: {result['error']}")
        
        # Example 2: Upload from URL
        print("\n=== Example 2: Upload from URL ===")
        result = uploader.upload_from_url(
            url='https://example.com/sample.pdf',
            filename='downloaded-file.pdf',
            s3_path='documents/downloaded-file.pdf',
            make_public=False
        )
        
        if result['success']:
            print(f"✓ File uploaded from URL!")
            print(f"  Source: {result['source_url']}")
            print(f"  URL: {result['url']}")
        else:
            print(f"✗ Upload failed: {result['error']}")
        
        # Example 3: List files in bucket
        print("\n=== Example 3: List Files ===")
        files = uploader.list_files(prefix='documents/', max_files=10)
        
        if files:
            print(f"Found {len(files)} files:")
            for file in files:
                print(f"  • {file['key']} ({file['size']} bytes)")
                print(f"    Modified: {file['last_modified']}")
                print(f"    URL: {file['url']}")
        else:
            print("No files found.")
        
        # Example 4: Upload multiple files
        print("\n=== Example 4: Upload Multiple Files ===")
        files_to_upload = ['file1.txt', 'file2.pdf', 'image.jpg']
        
        results = []
        for file_path in files_to_upload:
            if os.path.exists(file_path):
                result = uploader.upload_file(file_path)
                results.append(result)
        
        successful = [r for r in results if r.get('success')]
        print(f"Uploaded {len(successful)}/{len(results)} files successfully")
        
        # Example 5: Upload to specific folder structure
        print("\n=== Example 5: Organized Upload ===")
        from datetime import datetime
        
        today = datetime.now().strftime('%Y/%m/%d')
        result = uploader.upload_file(
            file_path='report.pdf',
            s3_path=f'reports/{today}/report.pdf',
            make_public=False
        )
        
        if result['success']:
            print(f"✓ Uploaded to organized path: {result['s3_key']}")
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("\nMake sure to set these environment variables:")
        print("  - AWS_ACCESS_KEY_ID")
        print("  - AWS_SECRET_ACCESS_KEY")
        print("  - S3_BUCKET_NAME")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    example_usage()

