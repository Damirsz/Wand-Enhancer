# Candidate record schema (one JSON object per line in work/raw/<agent>.jsonl)

Values in Russian where free text (comments), company names as found. Leave "" when unknown.
NEVER invent data. Every contact value must have its source URL in `contact_sources`.

```json
{
  "name_cn": "温州某某游乐设备有限公司",          // only if seen verbatim on a source page
  "name_en": "Wenzhou Xxx Amusement Equipment Co., Ltd.",
  "type": "завод | торговая | неясно",
  "type_evidence": "Audited Supplier на MIC; Business Type: Manufacturer; адрес в промзоне 桥下镇...; фото цеха на сайте",
  "province": "Zhejiang / 浙江",
  "city": "Wenzhou (Yongjia, Qiaoxia)",
  "address": "full address as on source",
  "website": "https://...",
  "url_1688": "",
  "url_alibaba": "",
  "url_mic": "https://xxx.en.made-in-china.com/",
  "contact_person": "",
  "contact_title": "",
  "mobile": "",            // several -> separate with "; "
  "landline": "",
  "wechat": "",            // ONLY if explicitly labeled WeChat/微信 on source; never assume = mobile
  "email": "",
  "qq": "",
  "whatsapp": "",          // ONLY if explicitly labeled WhatsApp
  "contact_sources": {"mobile": "URL", "landline": "URL", "email": "URL", "wechat": "URL", "contact_person": "URL", "address": "URL"},
  "main_products": "",
  "towers_6m": "да | нет | неясно",
  "tower_evidence": "напр.: товар 'XX' высота 9.2 м; фото проекта с 2 башнями ~10 м",
  "tower_examples": ["URL", "URL"],
  "hpl": "да | нет | неясно",
  "hpl_evidence": "URL or short note",
  "tube_slides": "нержавейка | ротоформ | оба | неясно",
  "tube_evidence": "URL or short note",
  "certs": "EN1176; TÜV; ASTM; CE; ISO9001 (only what is stated on source)",
  "export_cis": "экспорт: ...; СНГ: РФ/КЗ/УЗ если упомянуто, с URL",
  "russian_manager": "да | нет | неясно (+основание)",
  "founded": "",
  "employees": "",
  "reg_capital": "",
  "similarity": 3,         // 1..5 per scale below
  "comment": "кратко, почему такая оценка",
  "sources": ["every URL used"],
  "checked": "2026-10-07",
  "found_by": "agent name + source/query",
  "notes": "блокировки, сомнения"
}
```

Similarity scale:
- 5: делали почти такое же (несколько башен от 8 м, трубные горки, панели)
- 4: высокие башни (от 6 м) с трубными горками, но другой материал или стиль
- 3: большие комплексы, но башни ниже 6 м (или высота не подтверждена)
- 1-2: не для шортлиста (крытые лабиринты, только надувное, только аттракционы, тренажёры, мелкие комплексы)

Exclude (do not record, or record with similarity 1 and note) companies that do only indoor soft play (淘气堡),
only inflatables, only mechanical rides, only fitness equipment.
