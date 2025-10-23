# Cloud Storage Uploader for Remote Agent

Upload files to Amazon S3 or Digital Ocean Spaces. Designed for Remote Agent integration.

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

**Option B: Using Environment Variables**

**For Amazon S3:**
```bash
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export S3_BUCKET_NAME="your-bucket-name"
export AWS_REGION="us-east-1"
```

**For Digital Ocean Spaces:**
```bash
export DO_SPACES_KEY="your_spaces_key"
export DO_SPACES_SECRET="your_spaces_secret"
export DO_SPACES_ENDPOINT="nyc3.digitaloceanspaces.com"
export DO_SPACES_BUCKET="your-space-name"
export DO_SPACES_REGION="nyc3"
export DO_SPACES_FILES_URL="https://your-space.nyc3.cdn.digitaloceanspaces.com"
```

### 3. Upload Files

**AWS S3:**
```bash
python uploader.py upload myfile.pdf
python uploader.py upload-url https://example.com/file.pdf
python uploader.py list
```

**Digital Ocean Spaces:**
```bash
python do_uploader.py upload myfile.pdf
python do_uploader.py upload-url https://example.com/file.pdf
python do_uploader.py list
python do_uploader.py delete old-file.pdf
```

## Remote Agent Setup

### Create AWS S3 Agent

```bash
curl -X POST https://ra-hyp-1.raworc.com/api/v0/agents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "s3-uploader",
    "description": "Upload files to Amazon S3",
    "env": {
      "AWS_ACCESS_KEY_ID": "your_access_key",
      "AWS_SECRET_ACCESS_KEY": "your_secret_key",
      "S3_BUCKET_NAME": "your-bucket-name",
      "AWS_REGION": "us-east-1"
    },
    "setup": "git clone https://github.com/CloserlookAI/file-upload-tool.git file-upload-tool && cd file-upload-tool && pip install -r requirements.txt",
    "instructions": "You are an S3 file upload assistant. Help users upload files to S3 using: cd file-upload-tool && python uploader.py [command]"
  }'
```

### Create Digital Ocean Spaces Agent

```bash
curl -X POST https://ra-hyp-1.raworc.com/api/v0/agents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "do-spaces-uploader",
    "description": "Upload files to Digital Ocean Spaces",
    "env": {
      "DO_SPACES_KEY": "your_spaces_key",
      "DO_SPACES_SECRET": "your_spaces_secret",
      "DO_SPACES_ENDPOINT": "nyc3.digitaloceanspaces.com",
      "DO_SPACES_BUCKET": "your-space-name",
      "DO_SPACES_REGION": "nyc3"
    },
    "setup": "git clone https://github.com/CloserlookAI/file-upload-tool.git file-upload-tool && cd file-upload-tool && pip install -r requirements.txt",
    "instructions": "You are a Digital Ocean Spaces upload assistant. Help users upload files using: cd file-upload-tool && python do_uploader.py [command]"
  }'
```

### Chat with Agent

Once created, chat naturally:
- "Upload this file: https://example.com/document.pdf"
- "Upload report.pdf to the documents folder"
- "List all files"
- "Delete old-file.pdf" (DO Spaces only)

## Features

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

## Troubleshooting

### "Missing required environment variables"
Set all required environment variables for your chosen service.

### "Access Denied"
- Verify credentials are correct
- Check IAM/API key permissions
- Ensure bucket/space exists

### "ModuleNotFoundError: boto3"
Run: `pip install -r requirements.txt`

### URL download fails
- Check the URL is accessible
- Verify network connectivity

### CDN URLs not working (DO Spaces)
- Enable CDN in Digital Ocean dashboard
- Set DO_SPACES_FILES_URL to your CDN endpoint

## AWS vs Digital Ocean Comparison

| Feature | AWS S3 | Digital Ocean |
|---------|--------|---------------|
| **Pricing** | Pay per GB + requests | Fixed $5/month (250GB + 1TB bandwidth) |
| **CDN** | Extra cost (CloudFront) | Included free |
| **API** | Native S3 | S3-compatible |
| **Regions** | 20+ worldwide | 7 regions |
| **Best for** | Enterprise, global | Small-medium projects |

**Choose AWS S3 if:** You need global presence, advanced features, or are in AWS ecosystem.

**Choose Digital Ocean if:** You want predictable costs, built-in CDN, and simpler setup.

## Security Best Practices

1. ✅ Never commit credentials (use environment variables)
2. ✅ Use `.gitignore` to exclude `.env` files
3. ✅ Rotate credentials regularly
4. ✅ Use least-privilege permissions
5. ✅ Enable bucket/space encryption
6. ✅ Monitor access logs

## Required Permissions

### AWS S3 IAM Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:PutObject",
      "s3:PutObjectAcl",
      "s3:GetObject",
      "s3:ListBucket"
    ],
    "Resource": [
      "arn:aws:s3:::your-bucket-name",
      "arn:aws:s3:::your-bucket-name/*"
    ]
  }]
}
```

### Digital Ocean Spaces
When creating Spaces Keys, ensure they have:
- Read access (for listing)
- Write access (for uploading)
- Delete access (optional, for delete feature)

## Output Format

Both uploaders return JSON-compatible results:

```json
{
  "success": true,
  "bucket": "my-bucket",
  "space_key": "uploads/myfile.pdf",
  "url": "https://my-bucket.s3.us-east-1.amazonaws.com/uploads/myfile.pdf",
  "filename": "myfile.pdf",
  "size_bytes": 1024,
  "content_type": "application/pdf",
  "uploaded_at": "2025-10-23T12:00:00Z"
}
```

## License

MIT License - Free to use and modify.

## Support

- **AWS S3 Docs:** https://docs.aws.amazon.com/s3/
- **Digital Ocean Docs:** https://docs.digitalocean.com/products/spaces/
- **Remote Agent API:** https://ra-hyp-1.raworc.com/docs
