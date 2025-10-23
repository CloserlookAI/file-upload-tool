# File Uploader

Upload files to Amazon S3 or Digital Ocean Spaces.

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Credentials

**Option A: Using .env file (Recommended)**
```bash
cp .env.example .env
# Then edit .env and fill in your credentials
```

### AWS S3 (`uploader.py`)
- ✅ Upload local files
- ✅ Upload from URLs
- ✅ List files
- ✅ Public/private control
- ✅ Custom paths

### Digital Ocean Spaces (`do_uploader.py`)
- ✅ Upload local files
- ✅ Upload from URLs
- ✅ List files
- ✅ Delete files
- ✅ Public/private control
- ✅ Custom paths
- ✅ CDN support

## Command Reference

### AWS S3 Commands

```bash
# Upload local file
python uploader.py upload myfile.pdf

# Upload from URL
python uploader.py upload-url https://example.com/file.pdf

# Upload to custom path
python uploader.py upload myfile.pdf --s3-path documents/2025/myfile.pdf

# Make file public
python uploader.py upload myfile.pdf --public

# List files
python uploader.py list
python uploader.py list --prefix documents/ --max 50
```

### Digital Ocean Spaces Commands

```bash
# Upload local file
python do_uploader.py upload myfile.pdf

# Upload from URL
python do_uploader.py upload-url https://example.com/file.pdf

# Upload to custom path
python do_uploader.py upload myfile.pdf --space-path documents/2025/myfile.pdf

# Upload as private
python do_uploader.py upload myfile.pdf --private

# List files
python do_uploader.py list
python do_uploader.py list --prefix documents/ --max 50

# Delete file
python do_uploader.py delete documents/old-file.pdf
```

## Python API

### AWS S3

```python
from uploader import S3Uploader

uploader = S3Uploader()

# Upload file
result = uploader.upload_file('myfile.pdf')
print(result['url'])

# Upload from URL
result = uploader.upload_from_url('https://example.com/file.pdf')
print(result['url'])

# List files
files = uploader.list_files(prefix='documents/')
for f in files:
    print(f['key'], f['url'])
```

### Digital Ocean Spaces

```python
from do_uploader import DOSpacesUploader

uploader = DOSpacesUploader()

# Upload file
result = uploader.upload_file('myfile.pdf')
print(result['url'])

# Upload from URL
result = uploader.upload_from_url('https://example.com/file.pdf')
print(result['url'])

# Upload as private
result = uploader.upload_file('secret.pdf', make_public=False)

# List files
files = uploader.list_files(prefix='documents/')
for f in files:
    print(f['key'], f['url'])

# Delete file
result = uploader.delete_file('old-file.pdf')
```

## Getting Credentials

### AWS S3
1. Log in to [AWS Console](https://console.aws.amazon.com/)
2. Go to IAM → Users → Your User → Security Credentials
3. Create Access Key
4. Create an S3 bucket if you don't have one

### Digital Ocean Spaces
1. Log in to [Digital Ocean](https://cloud.digitalocean.com/)
2. Go to API → Spaces Keys
3. Click "Generate New Key"
4. Create a Space if you don't have one

## Environment Variables

### AWS S3

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| AWS_ACCESS_KEY_ID | Yes | AWS access key | AKIAIOSFODNN7EXAMPLE |
| AWS_SECRET_ACCESS_KEY | Yes | AWS secret key | wJalrXUtnFEMI/... |
| S3_BUCKET_NAME | Yes | Bucket name | my-bucket |
| AWS_REGION | No | AWS region | us-east-1 |
| S3_PREFIX | No | Folder prefix | uploads |

### Digital Ocean Spaces

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| DO_SPACES_KEY | Yes | Spaces access key | YOUR_KEY |
| DO_SPACES_SECRET | Yes | Spaces secret key | YOUR_SECRET |
| DO_SPACES_ENDPOINT | Yes | Spaces endpoint | nyc3.digitaloceanspaces.com |
| DO_SPACES_BUCKET | Yes | Space name | my-space |
| DO_SPACES_REGION | No | Region | nyc3 |
| DO_SPACES_FILES_URL | No | CDN URL | https://cdn.example.com |
| DO_SPACES_PREFIX | No | Folder prefix | uploads |
