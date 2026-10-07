# Выборочная сверка 5 случайных строк с источниками (2026-10-07)

Строки выбраны `random.seed(20261007)` из листа «Все» (53 компании). Каждое значение искалось на странице-источнике
(curl, нормализация цифр телефонов); скрипт: scratchpad `verify.py`.

| № в «Все» | Компания | Что сверено | Результат |
|---|---|---|---|
| 5 | 华东游乐设备有限公司 / Huadong Entertainment Equipment | моб. 13738396639, playground@huadongplay.com, WhatsApp-ссылка wa.me (huadongplay.com); 0577-67417777, 400-887-5787, huadongtoys@163.com, кит. название (huadong-toy.com); контакт «anchi», адрес Jilongyu Industrial Zone, год 1996 (MIC contact-info); габарит 2340*2200*900cm (карточка MIC) | всё совпало |
| 15 | 广州中力游乐设备集团有限公司 / Guangzhou Zhongli | 13631331688, 400-180-1168, MIAO@zhongliyoule.com, адрес 迎宾大道163号 (zhongliyoule.com); Mr. Chen, 2018 (MIC contact-info) | всё совпало |
| 19 | 南京万德体育产业集团有限公司 / Nanjing Wande | Mobile 18151937160, +86-25-56218381, sales11@wandeplay.com.cn, WhatsApp +8618112961678, адрес Tiansheng Qiao Road (contactus.html); Minimum Space 2700*1600cm у WD-15011200 | всё совпало (сайт отдаёт сжатый поток с обрывом chunked — читается только с `--compressed`) |
| 23 | Wenzhou East Amusement Equipment | Ms. Yoyo, Meiao Industrial Zone, 2012-02-20, 33 сотр. (MIC contact-info); Size 690*685*470cm (карточка MIC) | всё совпало |
| 53 | 广州市万虹实业有限公司 / Guangzhou Vanhon (Happy Elephant) | +86-136-4149-0587, +7978-015-63-23, оба email, адрес 汉基大道24号, «Михаил» (labirint-cn.ru/contacti.html) | всё совпало |

Дополнительно лично проверены (не случайно) лидеры шортлиста по карточкам и картинкам: Kaiqi KQ24031A и KQ24033A,
Cowboy Giant London Tower и Danali Peak, Yonglang YL26910, Huadong Transnational Series (две карточки).
По итогам: Kaiqi поднят до 5; у Huadong отмечено, что 9 м — габарит со шпилем; у ZZRS «башни от 6 м» исправлено на «нет»
(6,5 м — шпили, площадки до 2,4 м). WeChat у Cowboy («WhatsApp or WeChat: 8619303095295», mt-toys.com) и у Henan Shanghe
(«WeChat:+86-17633991776», shangheyoule.com) подтверждены подписью на сайте.
