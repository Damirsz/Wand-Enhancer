#!/usr/bin/env python3
"""Personal RFQ letters to playground suppliers from sourcing@cargixhub.com.

  python3 rfq.py --preview               build preview.html with every letter (no network)
  python3 rfq.py --test you@example.com  send sample letters (ids 1-3, or --ids) to yourself
  python3 rfq.py --send all              send to every included recipient
  python3 rfq.py --send 1,5,8            send only these ids (ids are shown in the preview)
  python3 rfq.py --bounces               list bounce notices from noreply@purelymail.com

Recipients: recipients.csv rows with "Включить в рассылку" = "да", one letter per company to the
main address. Letters go one by one with a random 60-120 s pause; each sent letter is copied to
"Sent" over IMAP and recorded in sent_log.json, so a re-run never sends the same address twice.

Template: template.txt (and optional template_zh.txt for rows whose language is "zh").
First line "Subject: ...", then a blank line, then the body. Placeholders:
  {brand} (short name)  {company}  {company_cn}  {contact}
  {greeting_name} (contact, else '<brand> team' / '<brand>负责人')  {product_ref}
Mailbox password: Keychain entry MAILBOX_KEYCHAIN or env SMTP_PASSWORD. Nothing secret is printed.
"""
import argparse
import csv
import html
import imaplib
import json
import os
import random
import re
import shutil
import smtplib
import subprocess
import sys
import time
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid

HERE = os.path.dirname(os.path.abspath(__file__))
FROM_ADDR = "sourcing@cargixhub.com"
FROM_NAME = os.environ.get("RFQ_FROM_NAME", "Cargix Sourcing")
MAILBOX_KEYCHAIN = "purelymail-cargixhub-sourcing"
SMTP_HOST, SMTP_PORT = "smtp.purelymail.com", 465
IMAP_HOST, IMAP_PORT = "imap.purelymail.com", 993
PAUSE = (60, 120)
LOG = os.path.join(HERE, "sent_log.json")
RECIPIENTS = os.path.join(HERE, "recipients.csv")


def load_recipients():
    with open(RECIPIENTS, encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if r["Включить в рассылку"].strip().lower() == "да"]
    out = []
    for i, r in enumerate(rows, 1):
        contact = re.sub(r"\s*\(.*?\)", "", r["Контактное лицо"]).strip()
        company = r["Компания (англ.)"].strip() or r["Компания (кит.)"].strip()
        brand = r["Короткое название для письма"].strip() or company
        lang = r["Язык письма (предложение)"].strip() or "en"
        out.append({
            "id": i,
            "email": r["Email (основной)"].strip(),
            "company": company,
            "company_cn": r["Компания (кит.)"].strip(),
            "contact": contact,
            "brand": brand,
            "greeting_name": contact or (f"{brand}负责人" if lang == "zh" else f"{brand} team"),
            "product_ref": r["Модель/проект для письма"].strip(),
            "lang": lang,
        })
    return out


def load_template(lang):
    path = os.path.join(HERE, "template_zh.txt" if lang == "zh" else "template.txt")
    if lang == "zh" and not os.path.exists(path):
        path = os.path.join(HERE, "template.txt")
    if not os.path.exists(path):
        sys.exit(f"Template not found: {path}")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    head, _, body = text.partition("\n\n")
    if not head.lower().startswith("subject:"):
        sys.exit(f"{path}: first line must be 'Subject: ...' followed by a blank line")
    return head.split(":", 1)[1].strip(), body.strip() + "\n"


def render(rec):
    subject, body = load_template(rec["lang"])
    try:
        return subject.format(**rec), body.format(**rec)
    except KeyError as e:
        sys.exit(f"Unknown placeholder {e} in template")


def build(rec, to_addr=None, subject_prefix=""):
    subject, body = render(rec)
    msg = EmailMessage()
    msg["From"] = formataddr((FROM_NAME, FROM_ADDR))
    msg["To"] = to_addr or rec["email"]
    msg["Subject"] = subject_prefix + subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=FROM_ADDR.split("@")[1])
    msg.set_content(body)
    return msg


def password():
    pw = os.environ.get("SMTP_PASSWORD")
    if not pw and shutil.which("security"):
        r = subprocess.run(["security", "find-generic-password", "-s", MAILBOX_KEYCHAIN, "-w"], capture_output=True, text=True)
        pw = r.stdout.strip() if r.returncode == 0 else None
    if not pw:
        sys.exit(f"No mailbox password: Keychain entry '{MAILBOX_KEYCHAIN}' not found and SMTP_PASSWORD is not set.")
    return pw


def load_log():
    if os.path.exists(LOG):
        with open(LOG, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_log(log):
    tmp = LOG + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=1)
    os.replace(tmp, LOG)


def sent_folder(imap):
    typ, data = imap.list()
    for line in data or []:
        s = line.decode(errors="ignore")
        if "\\Sent" in s:
            return s.rsplit(" ", 1)[-1].strip('"')
    return "Sent"


def copy_to_sent(pw, msg):
    with imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT) as imap:
        imap.login(FROM_ADDR, pw)
        imap.append(sent_folder(imap), "\\Seen", imaplib.Time2Internaldate(time.time()), msg.as_bytes())


def parse_ids(spec, recs):
    if spec == "all":
        return recs
    want = {int(x) for x in spec.split(",") if x.strip()}
    bad = want - {r["id"] for r in recs}
    if bad:
        sys.exit(f"Unknown ids: {sorted(bad)}")
    return [r for r in recs if r["id"] in want]


def preview(recs):
    log = {e["email"].lower() for e in load_log()}
    parts = []
    for r in recs:
        subject, body = render(r)
        state = "уже отправлено" if r["email"].lower() in log else "не отправлено"
        parts.append(
            f"<section><h2>#{r['id']} · {html.escape(r['company'])} {html.escape(r['company_cn'])}</h2>"
            f"<p><b>Кому:</b> {html.escape(r['email'])} · <b>язык:</b> {r['lang']} · {state}</p>"
            f"<p><b>Тема:</b> {html.escape(subject)}</p><pre>{html.escape(body)}</pre></section>"
        )
    page = (
        "<!doctype html><meta charset='utf-8'><title>RFQ preview</title>"
        "<style>body{font-family:Arial,sans-serif;max-width:860px;margin:24px auto;padding:0 16px}"
        "section{border-bottom:1px solid #ccc;padding:12px 0}pre{white-space:pre-wrap;font-family:Arial,sans-serif}</style>"
        f"<h1>RFQ: {len(recs)} писем от {FROM_ADDR}</h1>" + "".join(parts)
    )
    out = os.path.join(HERE, "preview.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"{len(recs)} letters -> {out}")


def send_test(recs, to_addr, ids):
    pw = password()
    chosen = parse_ids(ids, recs) if ids else recs[:3]
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=60) as smtp:
        smtp.login(FROM_ADDR, pw)
        for r in chosen:
            msg = build(r, to_addr=to_addr, subject_prefix=f"[TEST -> {r['email']}] ")
            smtp.send_message(msg)
            print(f"test #{r['id']} ({r['company']}) -> {to_addr}")


def send(recs, spec, assume_yes):
    log = load_log()
    done = {e["email"].lower() for e in log}
    todo = [r for r in parse_ids(spec, recs) if r["email"].lower() not in done]
    skipped = len(parse_ids(spec, recs)) - len(todo)
    if not todo:
        print(f"Nothing to send ({skipped} already in sent_log.json).")
        return
    print(f"About to send {len(todo)} letters from {FROM_ADDR} ({skipped} skipped as already sent):")
    for r in todo:
        print(f"  #{r['id']} {r['company']} <{r['email']}>")
    if not assume_yes and input("Type YES to send: ").strip() != "YES":
        sys.exit("Cancelled.")
    pw = password()
    for n, r in enumerate(todo):
        msg = build(r)
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=60) as smtp:
            smtp.login(FROM_ADDR, pw)
            smtp.send_message(msg)
        entry = {"id": r["id"], "email": r["email"], "company": r["company"], "subject": msg["Subject"],
                 "message_id": msg["Message-ID"], "sent_at": formatdate(localtime=True), "copied_to_sent": False}
        try:
            copy_to_sent(pw, msg)
            entry["copied_to_sent"] = True
        except Exception as e:  # sending already happened; record it anyway
            entry["imap_error"] = f"{type(e).__name__}: {e}"
        log.append(entry)
        save_log(log)
        print(f"sent #{r['id']} {r['company']} <{r['email']}>" + ("" if entry["copied_to_sent"] else " (IMAP copy failed)"))
        if n < len(todo) - 1:
            pause = random.randint(*PAUSE)
            print(f"  pause {pause}s")
            time.sleep(pause)
    print("Done. Check bounces in a few minutes: python3 rfq.py --bounces")


def bounces():
    pw = password()
    with imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT) as imap:
        imap.login(FROM_ADDR, pw)
        imap.select("INBOX", readonly=True)
        typ, data = imap.search(None, '(FROM "noreply@purelymail.com")')
        ids = data[0].split()
        if not ids:
            print("No bounce notices.")
        for i in ids:
            typ, msg = imap.fetch(i, "(BODY.PEEK[HEADER.FIELDS (DATE SUBJECT)])")
            print(msg[0][1].decode(errors="ignore").strip().replace("\r\n", " | "))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--preview", action="store_true")
    g.add_argument("--test", metavar="ADDRESS")
    g.add_argument("--send", metavar="all|1,5,8")
    g.add_argument("--bounces", action="store_true")
    ap.add_argument("--ids", help="with --test: which letters to sample (default 1,2,3)")
    ap.add_argument("--yes", action="store_true", help="with --send: skip the YES prompt")
    a = ap.parse_args()
    recs = load_recipients()
    if a.preview:
        preview(recs)
    elif a.test:
        send_test(recs, a.test, a.ids)
    elif a.send:
        send(recs, a.send, a.yes)
    else:
        bounces()


if __name__ == "__main__":
    main()
