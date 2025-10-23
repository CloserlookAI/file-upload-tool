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

## Remote Agent Setup

### Create Agent for Digital Ocean Spaces

```bash
curl -X POST https://ra-hyp-1.raworc.com/api/v0/agents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "file-uploader",
    "description": "Upload files to Digital Ocean Spaces",
    "env": {
      "DO_SPACES_KEY": "your_actual_key",
      "DO_SPACES_SECRET": "your_actual_secret",
      "DO_SPACES_ENDPOINT": "nyc3.digitaloceanspaces.com",
      "DO_SPACES_BUCKET": "remoteagent",
      "DO_SPACES_REGION": "nyc3",
      "DO_SPACES_FILES_URL": "https://files.remoteagent.com"
    },
    "setup": "git clone https://github.com/CloserlookAI/file-upload-tool.git && cd file-upload-tool && pip install -r requirements.txt",
    "instructions": "You are a file upload assistant. When users provide file URLs, download and upload them to Digital Ocean Spaces. Use: python do_uploader.py upload-url <url>. Always return the uploaded file URL from https://files.remoteagent.com"
  }'
```

### Usage Examples

**User:** "Upload this file: https://example.com/document.pdf"

**Agent:** Downloads and uploads, returns:
```
✓ File uploaded successfully!
URL: https://files.remoteagent.com/document.pdf
```

**User:** "Upload report.pdf to the documents folder"

**Agent:** Uploads with custom path:
```
✓ File uploaded to: documents/report.pdf
URL: https://files.remoteagent.com/documents/report.pdf
```

## Making Files Public (Important!)

**By default, files are uploaded as PUBLIC** so they're accessible via direct URL.

### Ensure Files Are Public

The uploader sets `ACL='public-read'` by default when uploading:

```bash
# ✅ Uploads as PUBLIC (default)
python do_uploader.py upload myfile.pdf
python do_uploader.py upload-url https://example.com/file.pdf

# ❌ Uploads as PRIVATE (only if you use --private flag)
python do_uploader.py upload myfile.pdf --private
```

### Enable Space-Wide Public Access

To ensure all files in your Space are publicly accessible:

1. Go to [Digital Ocean Dashboard](https://cloud.digitalocean.com/)
2. Navigate to **Spaces** → **Your Space Name** (e.g., `remoteagent`)
3. Click **Settings** tab
4. Under **File Listing**, enable **Public**
5. Save changes

This makes all files in the Space publicly readable without individual ACL settings.

### Set CORS Rules (For Browser Access)

If accessing files from web browsers, add CORS rules:

1. Go to your Space settings
2. Click on **CORS Configurations**
3. Add this configuration:

```xml
<CORSConfiguration>
  <CORSRule>
    <AllowedOrigin>*</AllowedOrigin>
    <AllowedMethod>GET</AllowedMethod>
    <AllowedMethod>HEAD</AllowedMethod>
    <AllowedHeader>*</AllowedHeader>
  </CORSRule>
</CORSConfiguration>
```

## Troubleshooting

### "AccessDenied" Error When Viewing Files

If uploaded files return `AccessDenied` XML error:

**Solution 1: Enable Space Public Access** (Recommended)
- Go to Digital Ocean dashboard → Spaces → Settings
- Enable "Public" under File Listing
- This makes all files publicly accessible

**Solution 2: Verify Upload Command**
- Ensure you're NOT using the `--private` flag
- Default behavior is public: `python do_uploader.py upload-url <url>`

**Solution 3: Check ACL Permissions**
- Files should have `public-read` ACL
- The uploader sets this automatically unless `--private` is used

### "Missing required environment variables"
Set all required environment variables for your chosen service in `.env` file.

### "Access Denied" (Credentials Issue)
- Verify credentials are correct in `.env` file
- Check IAM/API key permissions
- Ensure bucket/space exists

### "ModuleNotFoundError: boto3"
Run: `pip install -r requirements.txt`

### URL download fails
- Check the URL is accessible
- Verify network connectivity
- Some URLs may require authentication

### CDN URLs not working (DO Spaces)
- Enable CDN in Digital Ocean dashboard
- Set `DO_SPACES_FILES_URL` to your CDN endpoint (e.g., `https://files.remoteagent.com`)
- CDN can take 5-10 minutes to propagate changes
