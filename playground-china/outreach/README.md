# Рассылка запросов каталогов и цен (RFQ) поставщикам игровых комплексов

Запускать на Mac Дамира: токен Purelymail и пароль ящика лежат в Keychain. Порядок и правила взяты из
`PURELYMAIL-ACCESS.md`.

## 1. Ящик

```
python3 mail_setup.py --check     # показать домен cargixhub.com и существующие ящики, ничего не меняет
python3 mail_setup.py --create    # создать sourcing@cargixhub.com
```

- Токен API скрипт берёт из Keychain `purelymail-duoeast`.
- Пароль нового ящика генерируется и сразу кладётся в Keychain `purelymail-cargixhub-sourcing`, на экран он не выводится.
- Домен скрипт не добавляет, DNS и MX не трогает.
- Ящики quote@, latam@ и partners@ под защитой: скрипт откажется их создавать.

## 2. Письма

- `recipients.csv`: строки с «Включить в рассылку = да», сейчас их 24, по одному письму на компанию.
  - Адрес берётся из колонки «Email (основной)».
  - Для личного обращения есть колонки «Короткое название для письма» и «Модель/проект для письма».
- Шаблон: `template.txt` (по образцу `template.example.txt`). Для строк с языком `zh` можно сделать отдельный `template_zh.txt`.
  - Первая строка `Subject: ...`, затем пустая строка и текст письма.
  - Подстановки: `{greeting_name}`, `{brand}`, `{company}`, `{company_cn}`, `{contact}`, `{product_ref}`.

```
python3 rfq.py --preview                  # preview.html со всеми письмами, на проверку Дамиру
python3 rfq.py --test you@example.com     # образцы (письма 1-3 или --ids 4,7) себе
python3 rfq.py --send all                 # только после «да» Дамира; спросит YES
python3 rfq.py --send 1,5,8               # выборочно, номера из preview
python3 rfq.py --bounces                  # возвраты от noreply@purelymail.com
```

- Письма уходят по одному с паузой 60–120 секунд.
- Копия каждого письма кладётся в «Отправленные» через IMAP.
- Журнал пишется в `sent_log.json`: повторный запуск уже отправленным не пишет.
- `preview.html` и `sent_log.json` в git не попадают.
