#!/usr/bin/env python3
"""Copy a period's report.pdf to the shared Google Drive folder "QBR" in the DeveloperRelations shared drive.

Usage: upload-drive.py OUT_DIR START END
Uploads OUT_DIR/report.pdf as devrel-qbr-{START}_to_{END}.pdf into the folder DRIVE_QBR_FOLDER_ID (default: the DevRel QBR
folder). If a file with that name is already in the folder it is updated in place, so the link stays the same and no
duplicates pile up. Prints one JSON line with the file name, id and link.

Method 1 (preferred): Google Drive for Desktop. If the target folder is mounted on this computer, the PDF is copied into it and
Drive for Desktop uploads it as the signed-in person, so no credentials are needed. The folder is found by its Drive ID, which
Drive for Desktop stores as the extended attribute com.google.drivefs.item-id#S, so renamed or moved folders still match.

Method 2 (fallback): the Google service account in GOOGLE_APPLICATION_CREDENTIALS (the one meetup-calendar uses). The folder must be
shared with that account as an Editor, once. The full drive scope is needed because drive.file only sees files the account
created itself and cannot see a folder shared with it; a service account can still see only what has been shared with it.
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
import qbrlib as q  # noqa: E402

DEFAULT_FOLDER = "1rJ7ysQLIGkT06uCaHsgJxkLv041VlWI3"  # DeveloperRelations shared drive, folder "QBR"
API = "https://www.googleapis.com"


def drive_id_of(path):
    """The Drive file id Drive for Desktop stores on a synced file or folder, or None."""
    r = subprocess.run(["xattr", "-p", "com.google.drivefs.item-id#S", path], capture_output=True, text=True)
    return r.stdout.strip() or None if r.returncode == 0 else None


def find_local_folder(folder_id):
    """Locate the synced copy of a Drive folder under ~/Library/CloudStorage/GoogleDrive-*/ (macOS)."""
    override = os.environ.get("DRIVE_QBR_LOCAL_DIR")
    if override and os.path.isdir(os.path.expanduser(override)):
        return os.path.expanduser(override)
    for root in glob.glob(os.path.expanduser("~/Library/CloudStorage/GoogleDrive-*")):
        for pattern in ("Shared drives/*/*", "Shared drives/*", "My Drive/*", "My Drive"):
            for p in glob.glob(os.path.join(root, pattern)):
                if os.path.isdir(p) and drive_id_of(p) == folder_id:
                    return p
    return None


def copy_local(pdf_path, name, local_dir, folder_id):
    dst = os.path.join(local_dir, name)
    existed = os.path.exists(dst)
    shutil.copyfile(pdf_path, dst)
    link = f"https://drive.google.com/drive/folders/{folder_id}"
    for _ in range(15):  # Drive for Desktop assigns the file id once it has synced; give it a few seconds
        fid = drive_id_of(dst)
        if fid:
            link = f"https://drive.google.com/file/d/{fid}/view"
            break
        time.sleep(2)
    return {"name": name, "id": None, "link": link, "updated_existing": existed, "method": "Google Drive for Desktop", "path": dst}


def request(method, url, headers, body=None):
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


def fail(step, status, raw, email):
    """Exit with one readable line. A 403 about storage quota gets the shared-drive explanation."""
    text = raw.decode(errors="replace")
    try:
        text = json.loads(text)["error"]["message"]
    except (ValueError, KeyError, TypeError):
        pass
    text = " ".join(text.split())[:240]
    if status == 403 and "quota" in text.lower():
        sys.exit("Drive refused the upload: service accounts have no storage of their own, so a file the account creates in a normal "
                 "(My Drive) folder is rejected. Move the folder into a Shared Drive and add " + email + " as a Content manager. "
                 "See the README, 'Google Drive copy'.")
    sys.exit(f"Drive upload {step}: HTTP {status} {text}")


def upload(pdf_path, name, folder, token, email):
    auth = {"Authorization": f"Bearer {token}"}
    parent_q = f" and '{folder}' in parents" if folder else ""
    query = urllib.parse.urlencode({"q": f"name = '{name}'{parent_q} and trashed = false", "fields": "files(id,name,webViewLink)",
                                    "supportsAllDrives": "true", "includeItemsFromAllDrives": "true"})
    status, _, raw = request("GET", f"{API}/drive/v3/files?{query}", auth)
    if status != 200:
        hint = (f" The folder is not visible to {email}. Share the folder with that address as an Editor, then rerun." if status == 404 or
                (folder and "notFound" in raw.decode(errors="replace")) else "")
        sys.exit(f"Drive lookup failed: HTTP {status} {raw[:200].decode(errors='replace')}.{hint}")
    existing = json.loads(raw).get("files", [])
    if folder and not existing:  # confirm the folder itself is reachable and writable before creating anything
        s2, _, r2 = request("GET", f"{API}/drive/v3/files/{folder}?fields=id,name,capabilities(canAddChildren)&supportsAllDrives=true", auth)
        if s2 != 200:
            sys.exit(f"The Drive folder is not visible to {email} (HTTP {s2}). Share the folder with that address as an Editor, then rerun.")
        if not (json.loads(r2).get("capabilities") or {}).get("canAddChildren"):
            sys.exit(f"{email} can see the folder but cannot add files. Give it the Editor role on the folder.")
    meta = {"name": name, "mimeType": "application/pdf"}
    if existing:
        url = f"{API}/upload/drive/v3/files/{existing[0]['id']}?uploadType=resumable&supportsAllDrives=true&fields=id,name,webViewLink"
        method = "PATCH"
    else:
        if folder:
            meta["parents"] = [folder]
        url = f"{API}/upload/drive/v3/files?uploadType=resumable&supportsAllDrives=true&fields=id,name,webViewLink"
        method = "POST"
    status, headers, raw = request(method, url, {**auth, "Content-Type": "application/json; charset=UTF-8"}, json.dumps(meta).encode())
    session = next((v for k, v in headers.items() if k.lower() == "location"), None)
    if status != 200 or not session:
        fail("could not start", status, raw, email)
    with open(pdf_path, "rb") as f:
        data = f.read()
    status, _, raw = request("PUT", session, {"Content-Type": "application/pdf", "Content-Length": str(len(data))}, data)
    if status not in (200, 201):
        fail("failed", status, raw, email)
    out = json.loads(raw)
    return {"name": out["name"], "id": out["id"], "link": out.get("webViewLink"), "updated_existing": bool(existing)}


def main():
    q.load_settings_env()
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    out_dir, start, end = sys.argv[1:]
    pdf = os.path.join(out_dir, "report.pdf")
    if not os.path.exists(pdf):
        sys.exit(f"No PDF at {pdf}. Build the report first (it needs Chrome).")
    folder = os.environ.get("DRIVE_QBR_FOLDER_ID", DEFAULT_FOLDER)
    folder = None if folder.lower() == "none" else folder  # "none" uploads to the service account's own space, for testing
    name = f"devrel-qbr-{start}_to_{end}.pdf"
    local = find_local_folder(folder) if folder else None
    if local:
        print(json.dumps(copy_local(pdf, name, local, folder)))
        return
    token, email = q.google_access_token("https://www.googleapis.com/auth/drive")
    print(json.dumps(upload(pdf, name, folder, token, email)))


if __name__ == "__main__":
    main()
