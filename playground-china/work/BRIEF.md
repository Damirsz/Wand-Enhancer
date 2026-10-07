# Research brief (shared by all agents)

Goal: list Chinese MANUFACTURERS of large outdoor playground complexes with HIGH TOWERS (analogues of
Polish Buglo MEGA collection, not copies) plus their contacts. Procurement stage 1 for a client in Kazakhstan.
**Do not contact anyone. Do not fill forms, send inquiries, chat, log in, or register. Only collect and check public data.**

## References (images in playground-china/refs/)
- Buglo 1404: two towers ~8.6 m, rope bridge + platforms between them, several spiral tube slides and open slides,
  HPL panels with printed graphics, footprint 20.08 × 12.21 m, free fall 2.63 m.
- Buglo 1401: main tower ~8.6 m + small tower, spiral tube slides, 11.07 × 8.83 m.
- Buglo 1403: two towers ~8.6 m with bridge, 13.65 × 9.21 m.

## A good manufacturer
- makes outdoor complexes with towers from 6 m (better 8-10 m)
- post-and-platform frame, HPL or HDPE panel cladding
- tube slides: stainless steel (不锈钢) or rotomolded (滚塑)
- bridges and nets between towers
- accepts non-standard custom work (非标定制)
NOT wanted: companies that do only indoor soft play (淘气堡), only inflatables, only mechanical rides, only fitness.

## Keywords
CN: 非标高塔滑梯, 大型高塔滑梯, 双塔组合滑梯, 户外大型组合滑梯, HPL组合滑梯, HPL板滑梯, 不锈钢滑梯定制, 不锈钢螺旋滑梯,
滚塑螺旋滑梯, 无动力游乐设备定制, 绳网吊桥滑梯, 城堡滑梯, 森林主题滑梯, 欧标EN1176滑梯, 高塔滑梯, 塔式滑梯
EN: tower playground, multi-tower playground, high tower tube slide, HPL playground, stainless steel tube slide,
custom non-standard playground, double tower playground, giant tower slide, castle tower playground

## What is reachable from this environment (tested 2026-10-07)
- made-in-china.com (English): works with curl + browser User-Agent. Product search:
  `https://www.made-in-china.com/products-search/hot-china-products/Tower_Playground.html`
  Supplier showroom `https://<sub>.en.made-in-china.com/`, contact page `/contact-info.html`
  (shows Business Type, Main Products, Year, Employees, Address, Audited Supplier, contact person; phone may be hidden).
- cn.made-in-china.com: search URLs redirect and the keyword likely needs GBK encoding; try, don't fight it long.
- alibaba.com search: returns a JS-rendered shell (company names not in static HTML). Try WebFetch or supplier
  pages `https://<sub>.en.alibaba.com/` / `contactinfo.html` directly; skip if empty.
- 1688.com: anti-bot captcha (x5sec punish) on search → BLOCKED. Do not try to bypass. You may record a 1688 shop URL
  only if you saw it on a source page (company website etc.). No logged-in browser session is available.
- baidu.com and b2b.baidu.com: connection reset via proxy → try once at most, then mark blocked.
- tianyancha.com 419, aiqicha.baidu.com 302 (login) → skip. qcc.com home 200, search likely needs login — try once.
- WebSearch tool (US-based) and WebFetch tool are available; company websites (联系我们 / Contact Us pages) usually work.
- Use curl with UA `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36`.
  Pass `-L -m 30`. Save raw HTML only into your own scratch dir under /tmp/claude-0/-home-user-Wand-Enhancer/de8f786b-7d0e-51b7-a787-5f5665581811/scratchpad/<agent>/ and parse with `python3 -I`.

## Politeness
- No mass crawling. Sequential requests, pause ~2 s between requests to the same site (`sleep 2` inside your scripts is fine),
  roughly ≤ 80 requests per site in total. If a site blocks/captchas you, note it in the search log and move on.

## Data rules (strict)
- NOTHING invented. Empty string when unknown. Every contact value (person, mobile, landline, WeChat, email, QQ, WhatsApp)
  must have its source URL in `contact_sources`.
- `name_cn` only if seen verbatim on a page (company site footer, cn.made-in-china, business-license photo, qcc). Never translate.
- WeChat / WhatsApp only when explicitly labeled as such. Do not assume WeChat = mobile.
- Tower height: "да" only when a listing/project page states a height ≥ 6 m (e.g. "Height: 9.5 m", "高度8米",
  "size 20x15x10m"), or the specs/dimensions clearly show it. Put the URL in `tower_examples` and the quote in `tower_evidence`.
  Otherwise "неясно".
- Type: "завод" needs evidence (MIC Audited Supplier + Business Type Manufacturer, factory photos, address in industrial zone,
  1688 源头工厂 seen on a page, own production line). "торговая" if Business Type is Trading Company only / no factory.
- Similarity 1-5 per work/SCHEMA.md. 5 only if they show multiple towers ≥ 8 m + tube slides + panels.
- Write in Russian for free-text fields (comment, evidence notes), keep names/addresses as on source.

## Output
- One JSON object per company per line, schema in `playground-china/work/SCHEMA.md`, appended to
  `playground-china/work/raw/<agent>.jsonl` (you are the only writer of that file; you may rewrite it to fix a record).
- Search log: append one JSON per query/source to `playground-china/work/raw/<agent>_searchlog.jsonl`:
  `{"agent":"...","source":"made-in-china.com","query":"tower playground","url":"...","result":"12 suppliers, 5 relevant / blocked: captcha","date":"2026-10-07"}`
- After every ~10 companies run `python3 -I /home/user/Wand-Enhancer/playground-china/work/merge.py` (rebuilds work/candidates.csv).
- Do not touch files outside `playground-china/`. Do not git commit/push. Do not delete anything except your own scratch files.
- Final reply: short list of companies you recorded (name, city, similarity), what was blocked, and notable gaps. Keep it brief.
