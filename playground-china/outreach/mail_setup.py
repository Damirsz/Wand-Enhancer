#!/usr/bin/env python3
"""Create the outreach mailbox on cargixhub.com in Purelymail.

  python3 mail_setup.py --check          show domain and existing mailboxes, change nothing
  python3 mail_setup.py --create         create MAILBOX@DOMAIN, password goes straight to Keychain

The API token is read from the macOS Keychain entry `purelymail-duoeast`
(or from the PURELYMAIL_API_TOKEN environment variable). Nothing secret is printed.
The script never adds domains or touches DNS/MX: the domain must already be in the account.
"""
import argparse
import json
import os
import secrets
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

DOMAIN = "cargixhub.com"
MAILBOX = "sourcing"
TOKEN_KEYCHAIN = "purelymail-duoeast"
MAILBOX_KEYCHAIN = "purelymail-cargixhub-sourcing"
# Mailboxes read by Desk Cargix or used for carrier mail: never create over or reuse.
PROTECTED = {"quote@cargixhub.com", "latam@cargixhub.com", "partners@cargixhub.com", "airys@duoeast.com"}
API = "https://purelymail.com/api/v0/"


def keychain_read(service):
    if not shutil.which("security"):
        return None
    r = subprocess.run(["security", "find-generic-password", "-s", service, "-w"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def api_token():
    tok = os.environ.get("PURELYMAIL_API_TOKEN") or keychain_read(TOKEN_KEYCHAIN)
    if not tok:
        sys.exit(f"No API token: Keychain entry '{TOKEN_KEYCHAIN}' not found and PURELYMAIL_API_TOKEN is not set.")
    return tok


def call(op, body=None):
    req = urllib.request.Request(
        API + op,
        data=json.dumps(body or {}).encode(),
        headers={"Purelymail-Api-Token": api_token(), "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"{op}: HTTP {e.code} {e.read()[:300]!r}")
    if data.get("type") != "success":
        sys.exit(f"{op}: {data.get('code')} {data.get('message')}")
    return data.get("result") or {}


def domain_names(result):
    out = []
    for d in result.get("domains", []):
        out.append(d.get("name") if isinstance(d, dict) else str(d))
    return out


def domain_users():
    users = call("listUser").get("users", [])
    return sorted(u for u in users if str(u).lower().endswith("@" + DOMAIN))


def check():
    domains = call("listDomains")
    names = domain_names(domains)
    print(f"Domains in account: {', '.join(names)}")
    for d in domains.get("domains", []):
        if isinstance(d, dict) and d.get("name") == DOMAIN:
            dns = d.get("dnsSummary")
            if dns:
                print(f"{DOMAIN} DNS: {json.dumps(dns)}")
    if DOMAIN not in names:
        sys.exit(f"{DOMAIN} is not in the account. Not adding it here (MX change would break mail).")
    print(f"Mailboxes on {DOMAIN}: {', '.join(domain_users()) or '(none)'}")
    print(f"Target mailbox: {MAILBOX}@{DOMAIN} — {'EXISTS' if f'{MAILBOX}@{DOMAIN}' in domain_users() else 'not created yet'}")


def create():
    address = f"{MAILBOX}@{DOMAIN}"
    if address in PROTECTED:
        sys.exit(f"{address} is protected (Desk Cargix / partners), pick another name.")
    if DOMAIN not in domain_names(call("listDomains")):
        sys.exit(f"{DOMAIN} is not in the account.")
    if address in domain_users():
        sys.exit(f"{address} already exists, nothing to do.")
    if not shutil.which("security"):
        sys.exit("macOS 'security' not found: run this on the Mac so the password goes to Keychain.")
    password = secrets.token_urlsafe(24)
    r = subprocess.run(
        ["security", "add-generic-password", "-U", "-s", MAILBOX_KEYCHAIN, "-a", address, "-w", password],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        sys.exit(f"Keychain write failed: {r.stderr.strip()}")
    try:
        call("createUser", {"userName": MAILBOX, "domainName": DOMAIN, "password": password, "enablePasswordReset": False})
    except SystemExit:
        subprocess.run(["security", "delete-generic-password", "-s", MAILBOX_KEYCHAIN, "-a", address], capture_output=True)
        raise
    print(f"Created {address}. Password stored in Keychain entry '{MAILBOX_KEYCHAIN}' (not shown).")
    print("SMTP smtp.purelymail.com:465 (SSL), IMAP imap.purelymail.com:993, login = full address.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--create", action="store_true")
    a = ap.parse_args()
    check() if a.check else create()


if __name__ == "__main__":
    main()
