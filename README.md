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

If uploaded files return `AccessDenied` XML error, this is a **Digital Ocean Spaces permissions issue**. Follow these steps:

#### REQUIRED FIX: Enable Space Public Access

Digital Ocean Spaces require the **entire Space** to be set as Public, not just individual files:

1. Go to https://cloud.digitalocean.com/spaces
2. Click on your Space (e.g., `remoteagent`)
3. Click the **Settings** tab
4. Find **"File Listing"** section
5. Change from **"Restricted"** to **"Public"**
6. Click **Save**

**This is REQUIRED** even though the uploader sets `ACL=public-read` on individual files.

#### Test Upload & Access

Run the test script to verify:

```bash
python test_upload.py
```

This will:
- Upload a test file with public ACL
- Test if it's accessible via HTTP
- Show exactly what's wrong if access is denied
- Clean up after testing

#### Manual Verification

After enabling Space public access:

1. Upload a file:
   ```bash
   python do_uploader.py upload-url https://example.com/test.pdf
   ```

2. Check the returned URL (e.g., `https://files.remoteagent.com/test.pdf`)

3. Open the URL in a browser or test with curl:
   ```bash
   curl -I https://files.remoteagent.com/test.pdf
   ```

4. Should return `HTTP/1.1 200 OK` (not 403 Forbidden)

#### Still Getting AccessDenied?

If you still get errors after enabling Space public access:

1. **Check Space ACL Settings:**
   - In DO dashboard, go to Space Settings
   - Verify "File Listing" shows "Public" (not "Restricted")

2. **Verify Spaces API Keys:**
   - Make sure your API keys have write permissions
   - Regenerate keys if needed

3. **Check File ACL After Upload:**
   - In DO dashboard, click on an uploaded file
   - Check if "Public URL" is shown
   - If not, the Space is still restricted

4. **Clear CDN Cache:**
   - If using CDN, it may cache the 403 error
   - Wait 5-10 minutes or invalidate CDN cache

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
