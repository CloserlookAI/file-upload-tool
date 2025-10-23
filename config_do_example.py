# Digital Ocean Spaces Configuration Example
# Copy this file to config_do.py and fill in your credentials
# Or set these as environment variables

# Required: Digital Ocean Spaces Access Key
DO_SPACES_KEY = "your_spaces_key_here"

# Required: Digital Ocean Spaces Secret Key
DO_SPACES_SECRET = "your_spaces_secret_here"

# Required: Digital Ocean Spaces Endpoint
# Available endpoints: nyc3, sfo3, sgp1, fra1, ams3, blr1, syd1
# Format: {region}.digitaloceanspaces.com
DO_SPACES_ENDPOINT = "nyc3.digitaloceanspaces.com"

# Optional: Digital Ocean Spaces Region (default: nyc3)
DO_SPACES_REGION = "nyc3"

# Required: Digital Ocean Space Name (bucket name)
DO_SPACES_BUCKET = "your-space-name"

# Optional: CDN URL for your Space (if CDN is enabled)
# Example: "https://your-space-name.nyc3.cdn.digitaloceanspaces.com"
DO_SPACES_FILES_URL = ""

# Optional: Prefix/folder path in Space (e.g., "uploads" or "documents/files")
DO_SPACES_PREFIX = ""

