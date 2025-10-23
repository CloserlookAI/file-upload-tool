# Setup Guide for Remote Agent

## Digital Ocean Spaces Configuration

This guide is for setting up the file uploader with your Digital Ocean Spaces bucket.

### Your Configuration

Based on your setup:

```env
DO_SPACES_KEY=your_key_here
DO_SPACES_SECRET=your_secret_here
DO_SPACES_ENDPOINT=nyc3.digitaloceanspaces.com
DO_SPACES_BUCKET=remoteagent
DO_SPACES_REGION=nyc3
DO_SPACES_FILES_URL=https://files.remoteagent.com
```

### Setting Up .env File

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` and add:
```env
DO_SPACES_KEY=your_actual_key
DO_SPACES_SECRET=your_actual_secret
DO_SPACES_ENDPOINT=nyc3.digitaloceanspaces.com
DO_SPACES_BUCKET=remoteagent
DO_SPACES_REGION=nyc3
DO_SPACES_FILES_URL=https://files.remoteagent.com
```

### Fixing "AccessDenied" Error

If you're getting an AccessDenied error when viewing uploaded files, it means the files are not publicly accessible. Here's how to fix it:

#### Option 1: Make Files Public by Default (Recommended)
The uploader already sets files to public by default. Make sure you're uploading with:

```bash
python do_uploader.py upload myfile.pdf
# or
python do_uploader.py upload-url https://example.com/file.pdf
```

#### Option 2: Set Space-Wide Public Access
In Digital Ocean dashboard:
1. Go to your Space: `remoteagent`
2. Click **Settings** tab
3. Under **File Listing**, enable **Public**
4. This makes all files in the Space publicly readable

#### Option 3: Set CORS Rules
If files are public but still showing access denied from browsers:

1. Go to your Space settings
2. Add CORS configuration:
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

### Testing the Upload

```bash
# Upload a test file
python do_uploader.py upload test.txt

# Expected output:
# ✓ Upload successful!
#   URL: https://files.remoteagent.com/test.txt
```

The URL should use your CDN domain: `https://files.remoteagent.com`

### Remote Agent Setup

Create an agent with your configuration:

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

Once the agent is created, you can chat:

**User:** "Upload this file: https://example.com/document.pdf"

**Agent:** Downloads and uploads to DO Spaces, returns:
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

### Troubleshooting

#### Files Upload But Return AccessDenied
- Check that `make_public=True` (default)
- Verify Space permissions in DO dashboard
- Check CORS settings if accessing from browser

#### URLs Use Wrong Domain
- Ensure `DO_SPACES_FILES_URL=https://files.remoteagent.com` is set
- Restart uploader after changing .env

#### CDN Not Working
- Verify CDN is enabled in DO Spaces settings
- Check CDN endpoint matches `DO_SPACES_FILES_URL`
- CDN can take 5-10 minutes to propagate

### Commands Reference

```bash
# Upload from URL (for Remote Agent file links)
python do_uploader.py upload-url https://example.com/file.pdf

# Upload local file
python do_uploader.py upload myfile.pdf

# Upload to specific path
python do_uploader.py upload report.pdf --space-path documents/2025/report.pdf

# List files
python do_uploader.py list

# Delete file
python do_uploader.py delete old-file.pdf
```

All uploaded files will be accessible at:
`https://files.remoteagent.com/{filename}`

