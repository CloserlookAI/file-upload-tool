#!/usr/bin/env python3
"""
Digital Ocean Spaces File Uploader Tool for Remote Agent

This tool uploads files to Digital Ocean Spaces. It can:
- Upload local files to DO Spaces
- Download files from URLs and upload them to DO Spaces
- Handle various file types
- Use environment variables for DO Spaces credentials
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


class DOSpacesUploader:
    """Handler for uploading files to Digital Ocean Spaces"""
    
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
        """Initialize DO Spaces client with credentials from environment variables"""
        # Load .env file if it exists
        self._load_env_file()
        
        # Get DO Spaces credentials from environment
        self.do_spaces_key = os.getenv('DO_SPACES_KEY')
        self.do_spaces_secret = os.getenv('DO_SPACES_SECRET')
        self.do_spaces_endpoint = os.getenv('DO_SPACES_ENDPOINT')
        self.do_spaces_region = os.getenv('DO_SPACES_REGION', 'nyc3')
        self.do_spaces_bucket = os.getenv('DO_SPACES_BUCKET')
        self.do_spaces_files_url = os.getenv('DO_SPACES_FILES_URL', '')
        self.do_prefix = os.getenv('DO_SPACES_PREFIX', '')  # Optional folder prefix
        
        # Validate required environment variables
        if not all([self.do_spaces_key, self.do_spaces_secret, self.do_spaces_endpoint, self.do_spaces_bucket]):
            raise ValueError(
                "Missing required environment variables. Please set:\n"
                "  - DO_SPACES_KEY\n"
                "  - DO_SPACES_SECRET\n"
                "  - DO_SPACES_ENDPOINT (e.g., nyc3.digitaloceanspaces.com)\n"
                "  - DO_SPACES_BUCKET\n"
                "Optional: DO_SPACES_REGION, DO_SPACES_FILES_URL, DO_SPACES_PREFIX"
            )
        
        # Initialize S3-compatible client for DO Spaces
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.do_spaces_key,
                aws_secret_access_key=self.do_spaces_secret,
                endpoint_url=f"https://{self.do_spaces_endpoint}",
                region_name=self.do_spaces_region
            )
            print(f"✓ Connected to Digital Ocean Spaces")
            print(f"✓ Endpoint: {self.do_spaces_endpoint}")
            print(f"✓ Target bucket: {self.do_spaces_bucket}")
        except Exception as e:
            raise Exception(f"Failed to initialize DO Spaces client: {str(e)}")
    
    def get_content_type(self, file_path):
        """Determine content type for a file"""
        content_type, _ = mimetypes.guess_type(file_path)
        return content_type or 'application/octet-stream'
    
    def generate_space_key(self, filename, custom_path=None):
        """Generate Space key (path) for the file"""
        if custom_path:
            # Use custom path if provided
            space_key = custom_path
            if not space_key.endswith('/'):
                space_key += '/'
            space_key += filename
        elif self.do_prefix:
            # Use configured prefix
            space_key = f"{self.do_prefix.rstrip('/')}/{filename}"
        else:
            # Just use filename
            space_key = filename
        
        return space_key
    
    def get_public_url(self, space_key):
        """Generate public URL for the file"""
        if self.do_spaces_files_url:
            # Use custom CDN URL if provided
            base_url = self.do_spaces_files_url.rstrip('/')
            return f"{base_url}/{space_key}"
        else:
            # Use default DO Spaces URL
            return f"https://{self.do_spaces_bucket}.{self.do_spaces_endpoint}/{space_key}"
    
    def upload_file(self, file_path, space_path=None, make_public=True):
        """
        Upload a local file to DO Spaces
        
        Args:
            file_path: Path to the local file
            space_path: Optional custom Space path/key
            make_public: Whether to make the file publicly accessible (default: True)
            
        Returns:
            dict: Upload result with URL and metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Not a file: {file_path}")
        
        filename = file_path.name
        space_key = space_path if space_path else self.generate_space_key(filename)
        content_type = self.get_content_type(str(file_path))
        
        # Prepare extra args
        extra_args = {'ContentType': content_type}
        if make_public:
            extra_args['ACL'] = 'public-read'
        
        try:
            print(f"📤 Uploading {filename} to DO Spaces: {self.do_spaces_bucket}/{space_key}")
            
            # Upload file
            self.s3_client.upload_file(
                str(file_path),
                self.do_spaces_bucket,
                space_key,
                ExtraArgs=extra_args
            )
            
            # Generate URL
            url = self.get_public_url(space_key)
            
            # Get file size
            file_size = file_path.stat().st_size
            
            result = {
                'success': True,
                'bucket': self.do_spaces_bucket,
                'space_key': space_key,
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
            error_msg = f"DO Spaces upload failed: {str(e)}"
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
    
    def upload_from_url(self, url, filename=None, space_path=None, make_public=True):
        """
        Download a file from URL and upload it to DO Spaces
        
        Args:
            url: URL of the file to download
            filename: Optional custom filename (extracted from URL if not provided)
            space_path: Optional custom Space path/key
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
            
            # Upload to DO Spaces
            result = self.upload_file(temp_file, space_path, make_public)
            
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
        List files in the DO Space
        
        Args:
            prefix: Optional prefix to filter files
            max_files: Maximum number of files to return
            
        Returns:
            list: List of file objects
        """
        try:
            list_prefix = prefix if prefix else self.do_prefix
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.do_spaces_bucket,
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
                        'url': self.get_public_url(obj['Key'])
                    })
            
            return files
            
        except ClientError as e:
            print(f"✗ Failed to list files: {str(e)}")
            return []
    
    def delete_file(self, space_key):
        """
        Delete a file from DO Spaces
        
        Args:
            space_key: The key/path of the file to delete
            
        Returns:
            dict: Result of deletion
        """
        try:
            print(f"🗑️  Deleting {space_key} from DO Spaces...")
            
            self.s3_client.delete_object(
                Bucket=self.do_spaces_bucket,
                Key=space_key
            )
            
            result = {
                'success': True,
                'space_key': space_key,
                'message': 'File deleted successfully'
            }
            
            print(f"✓ File deleted successfully")
            return result
            
        except ClientError as e:
            error_msg = f"Failed to delete file: {str(e)}"
            print(f"✗ {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'space_key': space_key
            }
    
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
        description='Upload files to Digital Ocean Spaces',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload a local file
  python do_uploader.py upload myfile.pdf
  
  # Upload from URL
  python do_uploader.py upload-url https://example.com/file.pdf
  
  # Upload with custom path
  python do_uploader.py upload myfile.pdf --space-path documents/myfile.pdf
  
  # Upload as private file
  python do_uploader.py upload myfile.pdf --private
  
  # List files in Space
  python do_uploader.py list
  
  # Delete a file
  python do_uploader.py delete documents/myfile.pdf
  
Environment Variables Required:
  DO_SPACES_KEY          - Digital Ocean Spaces access key
  DO_SPACES_SECRET       - Digital Ocean Spaces secret key
  DO_SPACES_ENDPOINT     - Endpoint URL (e.g., nyc3.digitaloceanspaces.com)
  DO_SPACES_BUCKET       - Target Space name
  DO_SPACES_REGION       - Region (default: nyc3)
  DO_SPACES_FILES_URL    - Optional CDN URL
  DO_SPACES_PREFIX       - Optional folder prefix
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload a local file')
    upload_parser.add_argument('file', help='Path to the file to upload')
    upload_parser.add_argument('--space-path', help='Custom Space path/key')
    upload_parser.add_argument('--private', action='store_true', help='Make file private (default is public)')
    
    # Upload from URL command
    url_parser = subparsers.add_parser('upload-url', help='Upload a file from URL')
    url_parser.add_argument('url', help='URL of the file to upload')
    url_parser.add_argument('--filename', help='Custom filename')
    url_parser.add_argument('--space-path', help='Custom Space path/key')
    url_parser.add_argument('--private', action='store_true', help='Make file private (default is public)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List files in Space')
    list_parser.add_argument('--prefix', help='Filter by prefix')
    list_parser.add_argument('--max', type=int, default=100, help='Maximum files to list')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a file from Space')
    delete_parser.add_argument('key', help='Space key/path of file to delete')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Initialize uploader
        uploader = DOSpacesUploader()
        
        if args.command == 'upload':
            result = uploader.upload_file(
                args.file,
                space_path=args.space_path,
                make_public=not args.private
            )
            return 0 if result['success'] else 1
            
        elif args.command == 'upload-url':
            result = uploader.upload_from_url(
                args.url,
                filename=args.filename,
                space_path=args.space_path,
                make_public=not args.private
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
            
        elif args.command == 'delete':
            result = uploader.delete_file(args.key)
            return 0 if result['success'] else 1
            
    except ValueError as e:
        print(f"\n✗ Configuration Error: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

