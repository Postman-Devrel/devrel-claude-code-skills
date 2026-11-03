#!/usr/bin/env python3
"""One-time LinkedIn OAuth consent helper for qbr-metrics.

Runs the OAuth 2.0 authorization-code flow for the Postman LinkedIn developer app, prints an access token
(and a refresh token when LinkedIn issues one) to the terminal, then probes which organization data the
token can read: admin role, followers, and events. Tokens are never written to a file.

Before the first run, in the LinkedIn developer portal (your app -> Auth -> OAuth 2.0 settings) add this
exact Authorized redirect URL:  http://localhost:8765/callback   (change the port with --port, and add that URL instead)

Env vars (read from the environment first, then the "env" block of the Claude settings files):
  LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET   the app's credentials
  LINKEDIN_SCOPES                              space-separated scopes to request
  LINKEDIN_AUTHOR_URN                          the organization, urn:li:organization:NNNN (used by --verify)
  LINKEDIN_ACCESS_TOKEN                        used by --verify

Usage:
  python3 linkedin-oauth-setup.py              # consent, print token, probe the API
  python3 linkedin-oauth-setup.py --no-browser # print the consent URL instead of opening it
  python3 linkedin-oauth-setup.py --verify     # skip consent, probe with LINKEDIN_ACCESS_TOKEN
"""
import os
import secrets
import sys
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(__file__))
import qbrlib as q  # noqa: E402

AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
API = "https://api.linkedin.com"
CONSENT_TIMEOUT_SECONDS = 300
# LinkedIn REST versions are YYYYMM and each is active for about a year. The first one the API accepts is used.
VERSIONS = ["202611", "202610", "202609", "202607", "202604", "202601", "202510", "202507", "202504"]


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def run_consent(client_id, client_secret, scopes, port, open_browser):
    redirect_uri = f"http://localhost:{port}/callback"
    result, done, state = {}, threading.Event(), secrets.token_urlsafe(24)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != "/callback":
                self.send_response(404)
                self.end_headers()
                return
            params = urllib.parse.parse_qs(parsed.query)
            if params.get("state", [""])[0] != state:
                result["error"] = "state mismatch (possible CSRF); aborting"
            elif "error" in params:
                result["error"] = f"{params['error'][0]}: {params.get('error_description', [''])[0]}"
            elif "code" in params:
                result["code"] = params["code"][0]
            else:
                result["error"] = "no code returned"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            msg = "Consent failed. Return to the terminal." if "error" in result else "Consent received. You can close this tab."
            self.wfile.write(f"<html><body style='font-family:sans-serif'><p>{msg}</p></body></html>".encode())
            done.set()

        def log_message(self, *args):
            pass

    try:
        server = HTTPServer(("127.0.0.1", port), Handler)
    except OSError as e:
        die(f"could not listen on port {port}: {e}. Pick another with --port and register that redirect URL.")
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = AUTH_URL + "?" + urllib.parse.urlencode({"response_type": "code", "client_id": client_id,
                                                   "redirect_uri": redirect_uri, "state": state, "scope": scopes})
    print(f"Make sure this redirect URL is registered in your LinkedIn app: {redirect_uri}\n")
    print("Open this URL and approve access with a LinkedIn account that is an admin of the Postman page:\n")
    print(url + "\n")
    if open_browser:
        webbrowser.open(url)
    print(f"Waiting up to {CONSENT_TIMEOUT_SECONDS // 60} minutes for the redirect ...")
    if not done.wait(CONSENT_TIMEOUT_SECONDS):
        server.shutdown()
        die("timed out waiting for consent")
    server.shutdown()
    if "error" in result:
        die(f"consent failed: {result['error']}")
    status, body = q.http_json(TOKEN_URL, data={"grant_type": "authorization_code", "code": result["code"],
                                                "redirect_uri": redirect_uri, "client_id": client_id, "client_secret": client_secret},
                               headers={"Content-Type": "application/x-www-form-urlencoded"})
    if status != 200 or "access_token" not in body:
        die(f"token exchange failed: HTTP {status} {str(body)[:300]}")
    return body


def get(path, token, version, params=None):
    headers = {"Authorization": f"Bearer {token}", "X-Restli-Protocol-Version": "2.0.0", "LinkedIn-Version": version}
    url = API + path + (("?" + params) if params else "")
    return q.http_json(url, headers, retries=1)


def probe(token, org_urn):
    print("\nProbing what this token can read ...")
    version = None
    for v in VERSIONS:
        status, body = get("/rest/organizationAcls", token, v, "q=roleAssignee&role=ADMINISTRATOR&count=10")
        if status != 426:  # 426 means the version is not active
            version = v
            break
    if not version:
        print("  [fail] no active LinkedIn-Version found; set one manually in LINKEDIN_API_VERSION")
        return False
    ok = status == 200
    if ok:
        orgs = [e.get("organization") for e in body.get("elements", [])]
        print(f"  [ok]   API version {version}; administrator of: {', '.join(o for o in orgs if o) or 'no organizations'}")
        if org_urn and org_urn not in orgs:
            print(f"  [warn] {org_urn} is not in that list. The consenting account must be an admin of the Postman page.")
    else:
        print(f"  [fail] organizationAcls: HTTP {status} {str(body)[:200]}")
    enc = urllib.parse.quote(org_urn or "", safe="")
    checks = [("followers (networkSizes)", f"/rest/networkSizes/{enc}", "edgeType=COMPANY_FOLLOWED_BY_MEMBER"),
              ("follower statistics", "/rest/organizationalEntityFollowerStatistics", f"q=organizationalEntity&organizationalEntity={enc}"),
              ("page statistics", "/rest/organizationPageStatistics", f"q=organization&organization={enc}"),
              ("events (LinkedIn Live)", "/rest/events", f"q=eventsByOrganizer&organizer={enc}&count=5")]
    for name, path, params in checks:
        st, bd = get(path, token, version, params)
        if st == 200:
            print(f"  [ok]   {name}: {str(bd)[:140]}")
        else:
            hint = " (the app needs the matching LinkedIn product approved)" if st in (401, 403) else ""
            print(f"  [fail] {name}: HTTP {st} {str(bd.get('message', bd))[:110]}{hint}")
            ok = False
    print("\nNewsletter subscribers and article views have no documented API endpoint. If the probes above do not return them,"
          " copy them from LinkedIn analytics into channels-input.json.")
    return ok


def main():
    q.load_settings_env()
    client_id, client_secret = os.environ.get("LINKEDIN_CLIENT_ID", ""), os.environ.get("LINKEDIN_CLIENT_SECRET", "")
    scopes = os.environ.get("LINKEDIN_SCOPES", "r_organization_social rw_organization_admin")
    org = os.environ.get("LINKEDIN_AUTHOR_URN", "")
    port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8765
    if "--verify" in sys.argv:
        token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
        if not token:
            die("LINKEDIN_ACCESS_TOKEN is not set.")
    else:
        if not client_id or not client_secret:
            die("set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET first.")
        body = run_consent(client_id, client_secret, scopes, port, "--no-browser" not in sys.argv)
        token = body["access_token"]
        print("\nConsent granted. Add these to the \"env\" block of .claude/settings.json:\n")
        print(f'  "LINKEDIN_ACCESS_TOKEN": "{token}"')
        if body.get("refresh_token"):
            print(f'  "LINKEDIN_REFRESH_TOKEN": "{body["refresh_token"]}"')
        print(f"\nThe access token expires in about {int(body.get('expires_in', 0)) // 86400} days. Treat tokens like passwords.")
    sys.exit(0 if probe(token, org) else 2)


if __name__ == "__main__":
    main()
