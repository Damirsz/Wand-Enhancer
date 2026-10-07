#!/usr/bin/env python3
"""Merge work/raw/*.jsonl into work/candidates.csv (dedupe by legal name and phone).

Usage: python3 -I playground-china/work/merge.py
Safe to run concurrently: writes to a temp file and renames atomically.
"""
import csv
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "candidates.csv")

FIELDS = [
    ("name_cn", "Название (кит.)"),
    ("name_en", "Название (англ.)"),
    ("type", "Тип"),
    ("type_evidence", "Признаки типа"),
    ("province", "Провинция"),
    ("city", "Город"),
    ("address", "Адрес"),
    ("website", "Сайт"),
    ("url_1688", "1688"),
    ("url_alibaba", "Alibaba"),
    ("url_mic", "Made-in-China"),
    ("contact_person", "Контактное лицо"),
    ("contact_title", "Должность"),
    ("mobile", "Мобильный"),
    ("landline", "Стационарный"),
    ("wechat", "WeChat"),
    ("email", "Email"),
    ("qq", "QQ"),
    ("whatsapp", "WhatsApp"),
    ("main_products", "Основная продукция"),
    ("towers_6m", "Башни от 6 м"),
    ("tower_evidence", "Башни: подтверждение"),
    ("tower_examples", "Башни: примеры (URL)"),
    ("hpl", "HPL"),
    ("hpl_evidence", "HPL: подтверждение"),
    ("tube_slides", "Трубные горки"),
    ("tube_evidence", "Горки: подтверждение"),
    ("certs", "Сертификаты"),
    ("export_cis", "Экспорт / СНГ"),
    ("russian_manager", "Русскоязычный менеджер"),
    ("founded", "Год основания"),
    ("employees", "Сотрудники"),
    ("reg_capital", "Уставный капитал"),
    ("similarity", "Похожесть 1-5"),
    ("comment", "Комментарий"),
    ("contact_sources", "Источники контактов"),
    ("sources", "Все источники"),
    ("checked", "Дата проверки"),
    ("found_by", "Кем/где найдено"),
    ("notes", "Примечания"),
]

CONTACT_KEYS = ["contact_person", "mobile", "landline", "wechat", "email", "qq", "whatsapp"]

SUFFIX_RE = re.compile(
    r"(co\.?,?\s*ltd\.?|company\s+limited|co\.?\s*limited|limited|ltd\.?|inc\.?|corp(oration)?\.?|group|co\.?)$"
)


def norm_en(s):
    s = (s or "").lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    prev = None
    while prev != s:
        prev = s
        s = SUFFIX_RE.sub("", s).strip()
    return s


def norm_cn(s):
    s = re.sub(r"[\s()（）]", "", s or "")
    return s


def phones(rec):
    out = set()
    for k in ("mobile", "landline", "whatsapp"):
        for p in re.split(r"[;,/、，]", str(rec.get(k) or "")):
            d = re.sub(r"\D", "", p)
            if d.startswith("0086"):
                d = d[4:]
            elif d.startswith("86") and len(d) > 11:
                d = d[2:]
            d = d.lstrip("0")
            if len(d) >= 8:
                out.add(d)
    return out


def load():
    recs = []
    if not os.path.isdir(RAW):
        return recs
    for fn in sorted(os.listdir(RAW)):
        if not fn.endswith(".jsonl") or fn.endswith("_searchlog.jsonl"):
            continue
        with open(os.path.join(RAW, fn), encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"WARN {fn}:{i}: {e}", file=sys.stderr)
                    continue
                r.setdefault("found_by", fn[:-6])
                recs.append(r)
    return recs


def as_list(v):
    if v is None or v == "":
        return []
    if isinstance(v, list):
        return [str(x) for x in v if str(x).strip()]
    return [str(v)]


def join_unique(vals, sep="; "):
    seen, out = set(), []
    for v in vals:
        for part in [p.strip() for p in str(v).split(sep)]:
            if part and part.lower() not in seen:
                seen.add(part.lower())
                out.append(part)
    return sep.join(out)


def merge_group(group):
    m = {}
    for key, _ in FIELDS:
        vals = [r.get(key) for r in group]
        if key in ("tower_examples", "sources"):
            items = []
            for v in vals:
                items += as_list(v)
            m[key] = list(dict.fromkeys(items))
        elif key == "contact_sources":
            d = {}
            for v in vals:
                if isinstance(v, dict):
                    for k2, u in v.items():
                        if u:
                            d.setdefault(k2, [])
                            for uu in as_list(u):
                                if uu not in d[k2]:
                                    d[k2].append(uu)
            m[key] = d
        elif key == "similarity":
            nums = []
            for v in vals:
                try:
                    nums.append(int(v))
                except (TypeError, ValueError):
                    pass
            m[key] = max(nums) if nums else ""
        elif key in ("mobile", "landline", "wechat", "email", "qq", "whatsapp", "found_by", "notes", "certs"):
            m[key] = join_unique([v for v in vals if v])
        elif key in ("towers_6m", "hpl"):
            vs = [v for v in vals if v]
            m[key] = "да" if "да" in vs else ("нет" if vs and all(v == "нет" for v in vs) else (vs[0] if vs else ""))
        elif key == "tube_slides":
            vs = set(v for v in vals if v and v != "неясно")
            if "оба" in vs or {"нержавейка", "ротоформ"} <= vs:
                m[key] = "оба"
            elif vs:
                m[key] = vs.pop()
            else:
                m[key] = "неясно" if any(vals) else ""
        elif key == "type":
            vs = [v for v in vals if v]
            m[key] = "завод" if "завод" in vs else (vs[0] if vs else "")
        else:
            nonempty = [str(v) for v in vals if v not in (None, "")]
            if key in ("type_evidence", "comment", "tower_evidence", "hpl_evidence", "tube_evidence", "export_cis", "main_products"):
                m[key] = join_unique(nonempty, sep=" | ")
            else:
                m[key] = max(nonempty, key=len) if nonempty else ""
    return m


def dedupe(recs):
    parent = list(range(len(recs)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    keymap = {}
    for i, r in enumerate(recs):
        keys = []
        if norm_cn(r.get("name_cn")):
            keys.append("cn:" + norm_cn(r.get("name_cn")))
        if norm_en(r.get("name_en")):
            keys.append("en:" + norm_en(r.get("name_en")))
        keys += ["ph:" + p for p in phones(r)]
        for k in keys:
            if k in keymap:
                union(keymap[k], i)
            else:
                keymap[k] = i
    groups = {}
    for i in range(len(recs)):
        groups.setdefault(find(i), []).append(recs[i])
    return [merge_group(g) for g in groups.values()]


def flatten(m):
    row = {}
    for key, _ in FIELDS:
        v = m.get(key, "")
        if key == "contact_sources" and isinstance(v, dict):
            v = "\n".join(f"{k}: {' '.join(u)}" for k, u in v.items())
        elif isinstance(v, list):
            v = "\n".join(v)
        row[key] = v
    return row


def main():
    recs = load()
    merged = dedupe(recs)
    merged.sort(key=lambda m: (-(m["similarity"] or 0), m.get("name_en") or m.get("name_cn") or ""))
    fd, tmp = tempfile.mkstemp(dir=HERE, suffix=".csv")
    with os.fdopen(fd, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow([h for _, h in FIELDS])
        for m in merged:
            row = flatten(m)
            w.writerow([row[k] for k, _ in FIELDS])
    os.replace(tmp, OUT)
    print(f"raw records: {len(recs)}; merged companies: {len(merged)} -> {OUT}")
    # contact-source sanity check
    for m in merged:
        cs = m.get("contact_sources") or {}
        missing = [k for k in CONTACT_KEYS if m.get(k) and k not in cs]
        if missing:
            print(f"WARN no source URL for {missing}: {m.get('name_en') or m.get('name_cn')}", file=sys.stderr)


if __name__ == "__main__":
    main()
