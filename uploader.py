#!/usr/bin/env python3
"""
S3 File Uploader Tool for Remote Agent

This tool uploads files to Amazon S3 bucket. It can:
- Upload local files to S3
- Download files from URLs and upload them to S3
- Handle various file types
- Use environment variables for AWS credentials
"""

import os
import sys
import argparse
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import mimetypes
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class S3Uploader:
    """Handler for uploading files to Amazon S3"""
    
    def _load_env_file(self):
        """Load environment variables from .env file if it exists"""
        env_path = Path('.env')
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        if value and not os.getenv(key):  # Don't override existing env vars
                            os.environ[key] = value
    
    def __init__(self):
        """Initialize S3 client with credentials from environment variables"""
        # Load .env file if it exists
        self._load_env_file()
        
        # Get AWS credentials from environment
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        self.s3_prefix = os.getenv('S3_PREFIX', '')  # Optional folder prefix in bucket
        
        # Validate required environment variables
        if not all([self.aws_access_key_id, self.aws_secret_access_key, self.bucket_name]):
            raise ValueError(
                "Missing required environment variables. Please set:\n"
                "  - AWS_ACCESS_KEY_ID\n"
                "  - AWS_SECRET_ACCESS_KEY\n"
                "  - S3_BUCKET_NAME\n"
                "Optional: AWS_REGION (default: us-east-1), S3_PREFIX"
            )
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region
            )
            print(f"✓ Connected to S3 in region: {self.aws_region}")
            print(f"✓ Target bucket: {self.bucket_name}")
        except Exception as e:
            raise Exception(f"Failed to initialize S3 client: {str(e)}")
    
    def get_content_type(self, file_path):
        """Determine content type for a file"""
        content_type, _ = mimetypes.guess_type(file_path)
        return content_type or 'application/octet-stream'
    
    def generate_s3_key(self, filename, custom_path=None):
        """Generate S3 key (path) for the file"""
        if custom_path:
            # Use custom path if provided
            s3_key = custom_path
            if not s3_key.endswith('/'):
                s3_key += '/'
            s3_key += filename
        elif self.s3_prefix:
            # Use configured prefix
            s3_key = f"{self.s3_prefix.rstrip('/')}/{filename}"
        else:
            # Just use filename
            s3_key = filename
        
        return s3_key
    
    def upload_file(self, file_path, s3_path=None, make_public=False):
        """
        Upload a local file to S3
        
        Args:
            file_path: Path to the local file
            s3_path: Optional custom S3 path/key
            make_public: Whether to make the file publicly accessible
            
        Returns:
            dict: Upload result with URL and metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Not a file: {file_path}")
        
        filename = file_path.name
        s3_key = s3_path if s3_path else self.generate_s3_key(filename)
        content_type = self.get_content_type(str(file_path))
        
        # Prepare extra args
        extra_args = {'ContentType': content_type}
        if make_public:
            extra_args['ACL'] = 'public-read'
        
        try:
            print(f"📤 Uploading {filename} to s3://{self.bucket_name}/{s3_key}")
            
            # Upload file
            self.s3_client.upload_file(
                str(file_path),
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            
            # Generate URL
            url = f"https://{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/{s3_key}"
            
            # Get file size
            file_size = file_path.stat().st_size
            
            result = {
                'success': True,
                'bucket': self.bucket_name,
                's3_key': s3_key,
                'url': url,
                'filename': filename,
                'size_bytes': file_size,
                'content_type': content_type,
                'uploaded_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            print(f"✓ Upload successful!")
            print(f"  URL: {url}")
            print(f"  Size: {self._format_size(file_size)}")
            
            return result
            
        except ClientError as e:
            error_msg = f"S3 upload failed: {str(e)}"
            print(f"✗ {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'filename': filename
            }
        except Exception as e:
            error_msg = f"Upload failed: {str(e)}"
            print(f"✗ {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'filename': filename
            }
    
    def upload_from_url(self, url, filename=None, s3_path=None, make_public=False):
        """
        Download a file from URL and upload it to S3
        
        Args:
            url: URL of the file to download
            filename: Optional custom filename (extracted from URL if not provided)
            s3_path: Optional custom S3 path/key
            make_public: Whether to make the file publicly accessible
            
        Returns:
            dict: Upload result with URL and metadata
        """
        print(f"🌐 Downloading file from URL: {url}")
        
        # Extract filename from URL if not provided
        if not filename:
            parsed_url = urlparse(url)
            filename = Path(parsed_url.path).name
            if not filename:
                # Generate filename if none in URL
                filename = f"download_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Create temporary file
        temp_dir = Path('/tmp') if os.path.exists('/tmp') else Path('.')
        temp_file = temp_dir / f"temp_{filename}"
        
        try:
            # Download file
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get content type from response if available
            content_type = response.headers.get('Content-Type', 'application/octet-stream')
            
            # Save to temporary file
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = temp_file.stat().st_size
            print(f"✓ Downloaded {self._format_size(file_size)}")
            
            # Upload to S3
            result = self.upload_file(temp_file, s3_path, make_public)
            
            # Add source URL to result
            if result.get('success'):
                result['source_url'] = url
            
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to download from URL: {str(e)}"
            print(f"✗ {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'source_url': url
            }
        except Exception as e:
            error_msg = f"Upload from URL failed: {str(e)}"
            print(f"✗ {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'source_url': url
            }
        finally:
            # Clean up temporary file
            if temp_file.exists():
                temp_file.unlink()
    
    def list_files(self, prefix=None, max_files=100):
        """
        List files in the S3 bucket
        
        Args:
            prefix: Optional prefix to filter files
            max_files: Maximum number of files to return
            
        Returns:
            list: List of file objects
        """
        try:
            list_prefix = prefix if prefix else self.s3_prefix
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=list_prefix,
                MaxKeys=max_files
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'url': f"https://{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/{obj['Key']}"
                    })
            
            return files
            
        except ClientError as e:
            print(f"✗ Failed to list files: {str(e)}")
            return []
    
    def _format_size(self, size_bytes):
        """Format bytes to human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(
        description='Upload files to Amazon S3',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload a local file
  python uploader.py upload myfile.pdf
  
  # Upload from URL
  python uploader.py upload-url https://example.com/file.pdf
  
  # Upload with custom S3 path
  python uploader.py upload myfile.pdf --s3-path documents/myfile.pdf
  
  # Upload and make public
  python uploader.py upload myfile.pdf --public
  
  # List files in bucket
  python uploader.py list
  
Environment Variables Required:
  AWS_ACCESS_KEY_ID       - AWS access key
  AWS_SECRET_ACCESS_KEY   - AWS secret key
  S3_BUCKET_NAME          - Target S3 bucket name
  AWS_REGION              - AWS region (default: us-east-1)
  S3_PREFIX               - Optional folder prefix in bucket
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload a local file')
    upload_parser.add_argument('file', help='Path to the file to upload')
    upload_parser.add_argument('--s3-path', help='Custom S3 path/key')
    upload_parser.add_argument('--public', action='store_true', help='Make file publicly accessible')
    
    # Upload from URL command
    url_parser = subparsers.add_parser('upload-url', help='Upload a file from URL')
    url_parser.add_argument('url', help='URL of the file to upload')
    url_parser.add_argument('--filename', help='Custom filename')
    url_parser.add_argument('--s3-path', help='Custom S3 path/key')
    url_parser.add_argument('--public', action='store_true', help='Make file publicly accessible')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List files in bucket')
    list_parser.add_argument('--prefix', help='Filter by prefix')
    list_parser.add_argument('--max', type=int, default=100, help='Maximum files to list')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Initialize uploader
        uploader = S3Uploader()
        
        if args.command == 'upload':
            result = uploader.upload_file(
                args.file,
                s3_path=args.s3_path,
                make_public=args.public
            )
            return 0 if result['success'] else 1
            
        elif args.command == 'upload-url':
            result = uploader.upload_from_url(
                args.url,
                filename=args.filename,
                s3_path=args.s3_path,
                make_public=args.public
            )
            return 0 if result['success'] else 1
            
        elif args.command == 'list':
            files = uploader.list_files(prefix=args.prefix, max_files=args.max)
            if files:
                print(f"\n📁 Found {len(files)} files:")
                for f in files:
                    size = uploader._format_size(f['size'])
                    print(f"  • {f['key']} ({size})")
                    print(f"    {f['url']}")
            else:
                print("No files found.")
            return 0
            
    except ValueError as e:
        print(f"\n✗ Configuration Error: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

