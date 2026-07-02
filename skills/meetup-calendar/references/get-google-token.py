#!/usr/bin/env python3
import json, sys, time, base64, hashlib, hmac, os, urllib.request, urllib.parse

try:
    import google.auth
    import google.auth.transport.requests
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/spreadsheets"])
    creds.refresh(google.auth.transport.requests.Request())
    print(creds.token)
    sys.exit(0)
except ImportError:
    pass  # fall through to manual JWT approach

# Manual JWT signing for service accounts (no google-auth library needed)
key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
with open(key_path) as f:
    sa = json.load(f)

if sa.get("type") != "service_account":
    print("ERROR: credentials file is not a service account key", file=sys.stderr)
    sys.exit(1)

import struct
now = int(time.time())
claim = {
    "iss": sa["client_email"],
    "scope": "https://www.googleapis.com/auth/spreadsheets",
    "aud": "https://oauth2.googleapis.com/token",
    "iat": now,
    "exp": now + 3600,
}

def b64(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

header = b64(json.dumps({"alg": "RS256", "typ": "JWT"}))
payload = b64(json.dumps(claim))
msg = f"{header}.{payload}"

# Use openssl to sign (avoids needing cryptography library)
import subprocess, tempfile
with tempfile.NamedTemporaryFile(mode="w", suffix=".pem", delete=False) as kf:
    kf.write(sa["private_key"])
    kf_path = kf.name

result = subprocess.run(
    ["openssl", "dgst", "-sha256", "-sign", kf_path],
    input=msg.encode(), capture_output=True
)
os.unlink(kf_path)
sig = b64(result.stdout)
jwt = f"{msg}.{sig}"

# Exchange JWT for access token
body = urllib.parse.urlencode({
    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
    "assertion": jwt,
}).encode()
req = urllib.request.Request("https://oauth2.googleapis.com/token", data=body)
with urllib.request.urlopen(req) as resp:
    token_data = json.loads(resp.read())

print(token_data["access_token"])
