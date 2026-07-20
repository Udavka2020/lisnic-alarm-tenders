#!/usr/bin/env python3
"""
Парсинг товаров с 3 сайтов: safe24.md, videosecurity.md, dahua.md
Сохраняет в CSV формате: Сайт, Наименование, Цена, Ссылка
"""
import re, csv, os
from datetime import date

today = date.today().isoformat()
outdir = os.path.expanduser("~/wiki/company/tracking/products")
os.makedirs(outdir, exist_ok=True)

# ============================================================
# 1. safe24.md — данные уже собраны через web_extract
# ============================================================

# Извлечённый контент с безопасных страниц safe24.md (OpenCart)
# Парсим строки вида: [Название товара](https://...) и рядом цифра.XX MDL

all_safe24 = []

# Контент со всех полученных страниц safe24.md
safe24_pages_raw = [
    # Внутренние IP-камеры стр.1
    ("Внутренние IP-камеры (стр.1)", """
IP камера Tiandy TC-C320N, 2MP, 2.8mm, IR30m, Mic, PoE
425.76 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c320n

IP камера Tiandy TC-C32RN V4.2, 2MP+2MP, 2.8mm, IR30m, Mic, PoE
1241.80 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c32rn-v4-2

IP камера Tiandy TC-C32XN V4.1, 2MP, S+265, 2.8mm, IR30m, Mic, MicroSD, POE, IP67
1206.32 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c32xn-v41

IP камера Tiandy TC-C32XN V5.1, 2MP, 2.8mm, IR30m, Mic, PoE
452.37 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c32xn-v5-1

IP камера Tiandy TC-C32XN, 2MP, S+265, 2.8mm, IR30m, Mic, MicroSD, POE, IP66
1206.32 MDL
https://safe24.md/ru/vnutrennyaya-ip-kamera-videonablyudeniya-tiandy-tc-c32xn-2mp-s265-28mm-ir30m-mic-microsd-poe-ip66

IP камера Tiandy TC-C34HN, 4MP, S+265, 2.8mm, IR30m, POE, IP66
1401.46 MDL
https://safe24.md/ru/vnutrennyaya-ip-kamera-videonablyudeniya-tiandy-tc-c34hn-4mp-s265-28mm-ir30m-poe-ip66

IP камера Tiandy TC-C34HS V4.0, 4MP, S+265, 2.8mm, IR30m, Mic, MicroSD, POE, IP66
1401.46 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c34hs-v4

IP камера Tiandy TC-C34KN V4.2, 4MP, 2.8-12mm (Motorized), IR30m, Mic, mSD, PoE
2164.28 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c34kn-v4-2

IP камера Tiandy TC-C34KS V4.2, 4MP, 2.8mm, IR30m, Mic, mSD, PoE, IP66
1507.90 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c34ks-v42

IP камера Tiandy TC-C34XN 2GNA-28, 4MP, 2.8mm, IR30m, Mic, PoE
993.44 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c34xn-2gna-28-4mp-28mm-ir30m-mic-poe

IP камера Tiandy TC-C34XN V4.2, 4MP, 2.8mm, WLEDs, IR30m, Mic, PoE
1224.06 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c34xn-v42

IP камера Tiandy TC-C34XN V5.0, 4MP, 2.8mm, IR30m, Mic, PoE
975.70 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c34xn-v5-0

IP камера Tiandy TC-C35PS V4.2, 5MP, 2.8mm, IR30m, Mic, mSD, PoE, IP67
2749.70 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c35ps-v4-2

IP камера Tiandy TC-C35XS V4.1, 5MP, 2.8mm, IR30m, Mic, mSD, PoE, IP67
3530.26 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c35xs-v4-1

IP камера Tiandy TC-C35XS, 5MP, S+265, 2.8mm, IR30m, Mic, MicroSD, POE, IP67
1649.82 MDL
https://safe24.md/ru/vnutrennyaya-ip-kamera-videonablyudeniya-tiandy-tc-c35xs-5mp-s265-28mm-ir30m-mic-microsd-poe-ip67

IP камера Tiandy TC-C36XN 2ENA-28, 6MP, 2.8mm, IR30m, Mic, PoE
2465.86 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c36xn-2ena-28
"""),
    # Уличные IP-камеры
    ("Уличные IP-камеры", """
4G камера с солнечной панелью Uniarch Uho-P2G-M3F4D-EU, 3MP, IR/WLEDs 30m, Mic, Speaker, mSD, IP66
4470.48 MDL
https://safe24.md/ru/4g-kamera-s-solnechnoj-panelyu-uniarch-uho-p2g-m3f4d-eu

IP камера Reolink Go Plus, 4MP, H265, IR10m, 16x Digital Zoom, Mic, Speaker, MicroSD, 4G LTE, Battery, IP65
3636.70 MDL
https://safe24.md/ru/ip-kamera-reolink-go-plus

IP камера Reolink Go Series G340, 8MP, IR10m, Mic, Speaker, mSD, 4G LTE, Battery, IP65
4168.90 MDL
https://safe24.md/ru/ip-kamera-reolink-go-series-g340

IP камера Reolink Go, 2MP, H264, IR10m, 6x Digital Zoom, Mic, Speaker, MicroSD, 4G LTE, Solar Panel, Battery, IP67
6102.56 MDL
https://safe24.md/ru/ip-kamera-reolink-go-2mp-solar-panel

IP камера Tiandy TC-A32E2 Starlight Face Capture, 2MP, S+265, 12mm, IR30m, WLed's, POE, IP67
0.00 MDL
https://safe24.md/ru/naruzhnaya-ip-kamera-videonablyudeniya-tiandy-tc-a32e2-starlight-face-capture-2mp-s265-12mm-ir30m-wleds-poe-ip67

IP камера Tiandy TC-C321N, 2MP, 2.8mm, IR30m, Mic, PoE, IP67
425.76 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c321n

IP камера Tiandy TC-C32DP Color Maker, 2MP, S+265, 4mm, WLed's 20-30m, Mic, POE, IP67
975.70 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c32dp-color-maker-2mp-s265-4mm-wleds-20-30m-mic-poe-ip67-1

IP камера Tiandy TC-C32DP Color Maker, 2MP, S+265, 4mm, WLed's 20-30m, Mic, POE, IP67
975.70 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c32dp-color-maker-2mp-s265-4mm-wleds-20-30m-mic-poe-ip67

IP камера Tiandy TC-C32GN V4.2, 2MP, S+265, 2.8mm, IR50m, Mic, POE, IP67
478.98 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c32gn-v42

IP камера Tiandy TC-C32GN V4.2, 2MP, S+265, 4mm, IR50m, Mic, POE, IP67
478.98 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c32gn-v42-4mm

IP камера Tiandy TC-C32QN V4.2 (Tri-Light), 2MP, 2.8mm, IR50m, Mic, PoE, IP67
887.00 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c32qn-v42-tri-light

IP камера Tiandy TC-C32QN, 2MP, S+265, 2.8mm, IR30m, Mic, POE, IP67
452.37 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c32qn

IP камера Tiandy TC-C32WS V4.0, 2MP, 2.8mm, IR50m, Mic, mSD, PoE, IP67
1507.90 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c32ws-v4-0

IP камера Tiandy TC-C34GN V4.2, 4MP, S+265, 2.8mm, IR50m, Mic, POE, IP67
1064.40 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c34gn-v42

IP камера Tiandy TC-C34GN V4.2, 4MP, S+265, 4mm, IR50m, Mic, POE, IP67
1064.40 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c34gn-v42-4mm

IP камера Tiandy TC-C34GS Starlight, 4MP, S+265, 2.8mm, IR50m, Mic, MicroSD, POE, IP67
1401.46 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c34gs-starlight-4mp-s265-28mm-ir50m-mic-microsd-poe-ip67
"""),
    # Системы охранной сигнализации (проводные + беспроводные)
    ("Системы охранной сигнализации", """
Беспроводной комплект охранной сигнализации Teletek BRAVO EXT KIT, 85dB, Led, EN50131
3512.52 MDL
https://safe24.md/ru/беспроводнои-комплект-охранной-сигнализации-teletek-bravo-ext-kit-85db-led-en50131

Беспроводной комплект охранной сигнализации ZKTeco AP102 WiFi, KIT, 75dB, Led
2252.98 MDL
https://safe24.md/ru/besprovodnoi-komplekt-okhrannoj-signalizaczii-zkteco-ap102-wifi-kit-75db-led

Комплект охранной сигнализации DSC PC 1404 KIT, 4 Zones
1507.90 MDL
https://safe24.md/ru/komplekt-okhrannoj-signalizaczii-dsc-pc-1404-kit-4-zones

Комплект охранной сигнализации DSC PC 1616 EH KIT, 6 Zones
2004.62 MDL
https://safe24.md/ru/komplekt-okhrannoj-signalizaczii-dsc-pc-1616-eh-kit-6-zones

Комплект охранной сигнализации DSC PC 1616E13H KIT, 6 Zones
0.00 MDL
https://safe24.md/ru/komplekt-okhrannoj-signalizaczii-dsc-pc-1616e13h-kit-6-zones

Комплект охранной сигнализации DSC PC 1616E16H KIT, 6 Zones
3902.80 MDL
https://safe24.md/ru/komplekt-okhrannoj-signalizaczii-dsc-pc-1616e16h-kit-6-zones

Комплект охранной сигнализации DSC PC 1616E7H KIT, 6 Zones
2270.72 MDL
https://safe24.md/ru/komplekt-okhrannoj-signalizaczii-dsc-pc-1616e7h-kit-6-zones

Комплект охранной сигнализации DSC PC 1616E7H KIT, Аккумулятор 12V 17Ah, Трансформатор 20W, 6 Zones
2901.38 MDL
https://safe24.md/ru/komplekt-okhrannoj-signalizaczii-dsc-pc-1616e7h-kit-akkumulyator-12v-17ah-transformator-20w-6-zones

Комплект охранной сигнализации DSC PC 585H, Аккумулятор 12V 17Ah, Трансформатор 20W, 5 Zones
2121.70 MDL
https://safe24.md/ru/komplekt-okhrannoj-signalizaczii-dsc-pc-585h-akkumulyator-12v-17ah-transformator-20w-5-zones

Комплект охранной сигнализации Teletek Eclipse 16 LCD32 KIT, 16 Zones, LCD
2714.22 MDL
https://safe24.md/ru/komplekt-okhrannoj-signalizaczii-teletek-eclipse-16-lcd32-kit-16-zones-lcd

Комплект охранной сигнализации Teletek Eclipse 16 LED KIT, 16 Zones, Led
0.00 MDL
https://safe24.md/ru/комплект-охранной-сигнализации-teletek-eclipse-16-led-kit-16-zones-led

Комплект охранной сигнализации Teletek Eclipse 16 LED WL KIT, 16 Zones, Led
0.00 MDL
https://safe24.md/ru/комплект-охранной-сигнализации-teletek-eclipse-16-led-wl-kit-16-zones-led

Комплект охранной сигнализации Teletek Eclipse 8 LED KIT, 8 Zones, Led
1685.30 MDL
https://safe24.md/ru/комплект-охранной-сигнализации-teletek-eclipse-8-led-kit-8-zones-led

Комплект охранной сигнализации Teletek Eclipse 8+ WL KIT, 8/16 Zones, Led
2075.58 MDL
https://safe24.md/ru/komplekt-okhrannoj-signalizaczii-teletek-eclipse-8-wl-kit-8-16-zones-led

Комплект охранной сигнализации Teletek Eclipse8 LCD KIT, 32 Zones
2465.86 MDL
https://safe24.md/ru/komplekt-okhrannoj-signalizaczii-teletek-eclipse8-lcd-kit-32-zones-led
"""),
    # Внутренние IP-камеры стр.2
    ("Внутренние IP-камеры (стр.2)", """
IP камера Tiandy TC-C38XS 3LRA-28, 8MP, 2.8mm, IR30m, WLEDs, Mic, mSD, PoE, IP67
2643.26 MDL
https://safe24.md/ru/ip-kamera-tiandy-tc-c38xs-3lra-28

IP камера Uniarch IPC-T122-APF28, 2MP, Ultra 265, 2.8mm, IR30m, POE, IP67
443.50 MDL
https://safe24.md/ru/ip-kamera-uniarch-ipc-t122-apf28

IP камера Uniarch IPC-T124-APF28, 4MP, Ultra 265, 2.8mm, IR30m, Mic, POE, IP67
833.78 MDL
https://safe24.md/ru/ip-kamera-uniarch-ipc-t124-apf28-4mp-ultra-265-28mm-ir30m-mic-poe-ip67

IP камера Uniarch IPC-T124-APF28K, 4MP, 2.8mm, IR30m, Mic, mSD, PoE, IP67
833.78 MDL
https://safe24.md/ru/ip-kamera-uniarch-ipc-t124-apf28k

IP камера Uniarch IPC-T124-PF28, 4MP, Ultra 265, 2.8mm, IR30m, POE, IP67
1224.06 MDL
https://safe24.md/ru/vnutrennyaya-ip-kamera-videonablyudeniya-uniarch-ipc-t124-pf28-4mp-ultra-265-28mm-ir30m-poe-ip67

IP камера Uniarch IPC-T125-APF28, 5MP, Ultra 265, 2.8mm, IR30m, Mic, POE, IP67
1188.58 MDL
https://safe24.md/ru/ip-kamera-uniarch-ipc-t125-apf28-5mp-ultra-265-28mm-ir30m-mic-poe-ip67

IP камера Uniview IPC3232ER-VS-C, 2MP, Ultra 265, 2.8-12mm (Manual), IR30m, MicroSD, POE, IP67, IK10
1933.66 MDL
https://safe24.md/ru/vnutrennyaya-ip-kamera-videonablyudeniya-uniview-ipc3232er-vs-c-2mp-ultra-265-28-12mm-manual-ir30m-microsd-poe-ip67-ik10

IP камера Uniview IPC3234LR3-VSP-D, 4MP, Ultra 265, 2.8-12mm (Manual), IR30m, MicroSD, POE, IP67, IK10
3352.86 MDL
https://safe24.md/ru/vnutrennyaya-ip-kamera-videonablyudeniya-uniview-ipc3234lr3-vsp-d-4mp-ultra-265-28-12mm-manual-ir30m-microsd-poe-ip67-ik10

IP камера Uniview IPC324LB-ASF28K-A, 4MP, 2.8mm, IR30m, Mic, mSD, PoE, IP67, IK10
1632.08 MDL
https://safe24.md/ru/ip-kamera-uniview-ipc324lb-asf28k-a

IP камера Uniview IPC354SB-ADNF28K-I0, 4MP, 2.8mm, IR30m, Mic, mSD, PoE
2252.98 MDL
https://safe24.md/ru/ip-kamera-uniview-ipc354sb-adnf28k-i0

IP камера Uniview IPC3612LB-ADF28K-G, 2MP, Ultra 265, 2.8mm, IR30m, Mic, MicroSD, POE, IP67
1454.68 MDL
https://safe24.md/ru/vnutrennyaya-ip-kamera-videonablyudeniya-uniview-ipc3612lb-adf28k-g-2mp-ultra-265-28mm-ir30m-mic-microsd-poe-ip67

IP камера Uniview IPC3612LB-AF28K-WL, 2MP, 2.8mm, White Light 30m, Mic, mSD, PoE, IP67
887.00 MDL
https://safe24.md/ru/ip-kamera-uniview-ipc3612lb-af28k-wl

IP камера Uniview IPC3612LB-SF28-A, 2MP, Ultra 265, 2.8mm, IR30m, POE, IP67
620.90 MDL
https://safe24.md/ru/ip-kamera-uniview-ipc3612lb-sf28-a

IP камера Uniview IPC3612LR3-PF28-A, 2MP, Ultra 265, 2.8mm, IR30m, POE, IP67
620.90 MDL
https://safe24.md/ru/vnutrennyaya-ip-kamera-videonablyudeniya-uniview-ipc3612lr3-pf28-a-2mp-ultra-265-28mm-ir30m-poe-ip67

IP камера Uniview IPC3614LB-ADF28K-H, 4MP, 2.8mm, IR30m, Mic, mSD, PoE, IP67
1401.46 MDL
https://safe24.md/ru/ip-kamera-uniview-ipc3614lb-adf28k-h

IP камера Uniview IPC3614LB-AF28K-DL, 4MP, 2.8mm, IR30m, White Light 30m, Mic, mSD, PoE, IP67
1507.90 MDL
https://safe24.md/ru/ip-kamera-uniview-ipc3614lb-af28k-dl
"""),
    # Внутренние IP-камеры стр.3
    ("Внутренние IP-камеры (стр.3)", """
IP камера Uniview IPC3614LB-SF28-A, 4MP, Ultra 265, 2.8mm, IR30m, PoE, IP67
993.44 MDL
https://safe24.md/ru/ip-kamera-uniview-ipc3614lb-sf28-a

IP камера Uniview IPC3614LE-ADF28K, 4MP, Ultra 265, 2.8mm, IR30m, Mic, MicroSD, POE, IP67
1756.26 MDL
https://safe24.md/ru/vnutrennyaya-ip-kamera-videonablyudeniya-uniview-ipc3614le-adf28k-4mp-ultra-265-28mm-ir30m-mic-microsd-poe-ip67

IP камера Uniview IPC3614LE-ADF28K-G, 4MP, Ultra 265, 2.8mm, IR30m, Mic, MicroSD, POE, IP67
1774.00 MDL
https://safe24.md/ru/vnutrennyaya-ip-kamera-videonablyudeniya-uniview-ipc3614le-adf28k-g-4mp-ultra-265-28mm-ir30m-mic-microsd-poe-ip67

IP камера Uniview IPC3614LE-ADF28KC-WL, 4MP, Ultra 265, 2.8mm, IR30m, White Light 30m, Mic, Speaker, MicroSD, POE, IP67
1915.92 MDL
https://safe24.md/ru/ip-kamera-uniview-ipc3614le-adf28kc-wl

IP камера Uniview IPC3614LR3-PF28-D, 4MP, Ultra 265, 2.8mm, IR30m, POE, IP67
1401.46 MDL
https://safe24.md/ru/ip-kamera-uniview-ipc3614lr3-pf28-d-4mp-ultra-265-28mm-ir30m-poe-ip67

IP камера Uniview IPC3616LE-ADF28-WL, 6MP, 2.8mm, IR30m, White Light 10m, Mic, PoE, IP67
2164.28 MDL
https://safe24.md/ru/ip-kamera-uniview-ipc3616le-adf28-wl

IP камера Uniview IPC3618LB-ADF28K-DL, 8MP, 2.8mm, IR30m/WL30m, Mic, Speaker, mSD, PoE, IP67
2643.26 MDL
https://safe24.md/ru/ip-kamera-uniview-ipc3618lb-adf28k-dl

IP камера Uniview IPC3618LE-ADF28K-G, 8MP, Ultra 265, 2.8mm, IR30m, Mic, MicroSD, POE, IP67
2998.06 MDL
https://safe24.md/ru/ip-kamera-uniview-ipc3618le-adf28k-g

IP камера Uniview IPC3618LE-ADF28KC-DL, 8MP, 2.8mm, IR30m/WL30m, Mic, Speaker, mSD, PoE, IP67
3015.80 MDL
https://safe24.md/ru/ip-kamera-uniview-ipc3618le-adf28kc-dl

IP камера Uniview IPC3635LB-ADZK-H, 5MP, 2.8-12mm, IR40m, Mic, mSD, PoE, IP67
2767.44 MDL
https://safe24.md/ru/ip-kamera-uniview-ipc3635lb-adzk-h

IP камера Uniview PC324LB-ADF28K-H, 4MP, 2.8mm, IR30m, Mic, mSD, PoE, IK10
1632.08 MDL
https://safe24.md/ru/ip-kamera-uniview-pc324lb-adf28k-h

IP камера UNV IPC3638SB-ADZK-I0, 8MP, 2.8-12mm (Motorized), IR40m, Mic, mSD, PoE, IP67
6031.60 MDL
https://safe24.md/ru/ip-kamera-unv-ipc3638sb-adzk-i0

Беспроводная IP камера Reolink E Series E560, 8MP, 2.8-8mm, IR12m, Mic, Speaker, mSD, IP64
2838.40 MDL
https://safe24.md/ru/besprovodnaya-ip-kamera-reolink-e-series-e560

Беспроводная IP камера Reolink E1 Outdoor, 5MP, H.264, 2.8-8mm, 3x Optical Zoom, IR12m, Mic, Speaker, MicroSD
2394.90 MDL
https://safe24.md/ru/besprovodnaya-ip-kamera-reolink-e1

Беспроводная IP камера Reolink E1 Pro, 4MP, 4mm, H.264, IR12m, Mic, Speaker, MicroSD
1206.32 MDL
https://safe24.md/ru/besprovodnaya-ip-kamera-reolink-e1-pro-4mp

Беспроводная IP камера Reolink E1, 3MP, 4mm, H.264, IR12m, Mic, Speaker, MicroSD
887.00 MDL
https://safe24.md/ru/besprovodnaya-ip-kamera-reolink-e1-3mp
"""),
    # Внутренние IP-камеры стр.4
    ("Внутренние IP-камеры (стр.4)", """
Беспроводная IP камера Tiandy TC-C32CN V4.0, 2MP, 2.8mm, IR30m, WLED, Mic, Speaker, mSD, Baterry
1543.38 MDL
https://safe24.md/ru/besprovodnaya-ip-kamera-tiandy-tc-c32cn-v40

Беспроводная IP камера TP-LlNK Tapo C100, 2MP, 3.15mm, IR12m, mSD, Mic, Speaker
443.50 MDL
https://safe24.md/ru/besprovodnaya-ip-kamera-tp-llnk-tapo-c100-2mp-315mm-ir12m-msd-mic-speaker

Беспроводная IP камера TP-LlNK Tapo C110, 3MP, 3.3mm, IR9m, mSD, Mic, Speaker
585.42 MDL
https://safe24.md/ru/besprovodnaya-ip-kamera-tp-llnk-tapo-c110-3mp-33mm-ir9m-msd-mic-speaker

Беспроводная IP камера TP-LlNK Tapo C200C, 2MP, 4mm, PT, IR12m, mSD, Mic, Speaker
470.11 MDL
https://safe24.md/ru/беспроводная-ip-камера-tp-llnk-tapo-c200c,-2mp,-4mm,-pt,-ir12m,-msd,-mic,-speaker

Беспроводная IP камера TP-LlNK Tapo C210, 3MP, 4mm, PT, IR12m, mSD, Mic, Speaker
532.20 MDL
https://safe24.md/ru/besprovodnaya-ip-kamera-tp-llnk-tapo-c210-3mp-4mm-pt-ir12m-msd-mic-speaker

Беспроводная IP камера TP-LlNK Tapo C220, 4MP, 4mm, PT, IR12m, mSD, Mic, Speaker
638.64 MDL
https://safe24.md/ru/besprovodnaya-ip-kamera-tp-llnk-tapo-c220-4mp-4mm-pt-ir12m-msd-mic-speaker

Беспроводная IP камера Uniarch T1L-2WT, 2MP, 3.6mm, H.265, IR10m, Mic, Speaker, MicroSD
798.30 MDL
https://safe24.md/ru/besprovodnaya-ip-kamera-uniarch-t1l-2wt-2mp-36mm-h265-ir10m-mic-speaker-microsd

Беспроводная IP камера Uniarch Uho-S2E, 2MP, 4mm, H.265, PT, IR10m, Mic, Speaker, mSD, LAN
532.20 MDL
https://safe24.md/ru/besprovodnaya-ip-kamera-uniarch-uho-s2e

Беспроводная IP камера Uniarch Uho-S2E-M3, 3MP, 4mm, H.265, PT, IR10m, Mic, Speaker, mSD
567.68 MDL
https://safe24.md/ru/besprovodnaya-ip-kamera-uniarch-uho-s2e-m3

Беспроводная IP камера Uniarch Uho-S2E-M4, 4MP, 4mm, PT, IR10m, Mic, Speaker, mSD
922.48 MDL
https://safe24.md/ru/besprovodnaya-ip-kamera-uniarch-uho-s2e-m4

Беспроводная IP камера YouKey S320, 4MP, 2.8mm, IR10m, WLED, Mic, Speaker, mSD, 8Gb, Baterry, IP65
1862.70 MDL
https://safe24.md/ru/besprovodnaya-ip-kamera-youkey-s320

Беспроводная IP камера ZKTeco C1B2, 3MP, Ultra 265, 2.8mm, IR10m, MicroSD, Mic, Speaker
709.60 MDL
https://safe24.md/ru/besprovodnaya-ip-kamera-zkteco-c1b2

Беспроводная IP камера ZKTeco C2E2, 3MP, 3.6mm, H.265, IR10m, Mic, Speaker, MicroSD
798.30 MDL
https://safe24.md/ru/besprovodnaya-ip-kamera-zkteco-c2e2
"""),
]

def parse_safe24_products(raw_text):
    """Парсит блок текста с товарами safe24.md"""
    products = []
    lines = raw_text.strip().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        # Проверяем, это строка с названием товара (не цена и не ссылка)
        if 'MDL' in line:
            price = line.replace('MDL', '').strip()
            # Смотрим на предыдущую строку - название
            if i > 0:
                name = lines[i-1].strip()
                # Находим URL - ищем после названия или цены
                url = ""
                for j in range(i+1, min(i+3, len(lines))):
                    if lines[j].strip().startswith('http'):
                        url = lines[j].strip()
                        break
                if name and not name.startswith('http') and not name.startswith('0.00') and len(name) > 5:
                    products.append({
                        "name": name,
                        "price": price,
                        "url": url,
                        "source": "safe24.md"
                    })
        i += 1
    return products

# Собираем все товары safe24
seen_names = set()
all_safe24_products = []
for cat_name, raw_text in safe24_pages_raw:
    prods = parse_safe24_products(raw_text)
    for p in prods:
        key = p["name"].lower()[:60]
        if key not in seen_names:
            seen_names.add(key)
            all_safe24_products.append(p)

print(f"safe24.md: найдено {len(all_safe24_products)} товаров (с дедупликацией)")

# ============================================================
# 2. dahua.md — товары с главной и категорий (цены только на страницах товаров)
# ============================================================

dahua_products = [
    # С главной страницы и категорий
    {"name": "Dahua DHI-NVR2116HS-4KS3 Сетевой регистратор на 16 каналов", "price": "Уточняйте", "url": "http://www.dahua.md/page/dahua-dhi-nvr2116hs-4ks3-setevoj-registrator-na-16-kanalov"},
    {"name": "Dahua DHI-NVR2116HS-I2 IP Видеорегистратор AI на 16 каналов", "price": "Уточняйте", "url": "http://www.dahua.md/page/dahua-dhi-nvr2116hs-i2-ip-videoregistrator-ai-na-16-kanalov"},
    {"name": "Dahua DHI-NVR5832-EI Сетевой регистратор на 32 канала", "price": "Уточняйте", "url": "http://www.dahua.md/page/dahua-dhi-nvr5832-ei-setevoj-registrator-na-32-kanala"},
    {"name": "Dahua DHI-NVR2116HS-S3 Сетевой регистратор на 16 каналов", "price": "Уточняйте", "url": "http://www.dahua.md/page/dahua-dhi-nvr2116hs-s3-setevoj-registrator-na-16-kanalov"},
    {"name": "Dahua DHI-VTH8A41KMS-W Android IP и Wi-Fi домофон 10\" LCD TOUCH SCREEN", "price": "Уточняйте", "url": "http://www.dahua.md/page/dahua-dhi-vth8a41kms-w-android-ip-i-wi-fi-domofon-10-lcd-touch-screen"},
    {"name": "IP Вызывная панель домофона Dahua DHI-VTO2301R-P", "price": "Уточняйте", "url": "http://www.dahua.md/page/ip-vyzyvnaja-panel-domofona-dahua-dhi-vto2301r-p"},
    {"name": "Комплект видеодомофона Dahua kta02 Монитор+вызывная панель", "price": "Уточняйте", "url": "http://www.dahua.md/page/komplekt-videodomofona-dahua-kta02-monitorvyzyvnaja-panel"},
    {"name": "Монитор IP домофон Dahua DHI-VTH8A21KMS-W, Wi-Fi", "price": "Уточняйте", "url": "http://www.dahua.md/page/monitor-ip-domofon-dahua-dhi-vth8a21kms-w-wi-fi"},
    {"name": "Камера видеонаблюдения Dahua DH-IPC-HDW1239V-A-IL 2Mp 2.8mm", "price": "Уточняйте", "url": "http://www.dahua.md/page/kamera-videonabljudenija-dahua-dh-ipc-hdw1239v-a-il-2mp-28mm"},
    {"name": "4МП IP Камера Dahua DH-IPC-HDBW5441R-ASE-HDMI (2.8 мм)", "price": "239 USD", "url": "http://www.dahua.md/page/4mp-ip-kamera-dahua-dh-ipc-hdbw5441r-ase-hdmi-28-mm"},
    {"name": "Dahua Видеокамера DH-IPC-HDW2649T-S-PRO 6MP 2.8 mm", "price": "Уточняйте", "url": "http://www.dahua.md/page/dahua-videokamera-dh-ipc-hdw2649t-s-pro-6mp-28-mm"},
    {"name": "Dahua DH-IPC-HDW1639T-A-IL 6 Mp Уличная купольная камера видеонаблюдения", "price": "Уточняйте", "url": "http://www.dahua.md/page/dahua-dh-ipc-hdw1639t-a-il-6-mp-ulichnaja-kupolnaja-kamera-videonabljudenija"},
    {"name": "Dahua Камера видеонаблюдения DH-IPC-EBW5641-AS", "price": "Уточняйте", "url": "http://www.dahua.md/page/dahua-kamera-videonabljudenija-dh-ipc-ebw5641-as"},
    {"name": "DAHUA Двух матричная IP-видеокамера IPC-HDW8441X-3D", "price": "Уточняйте", "url": "http://www.dahua.md/page/dahua-dvuh-matrichnaja-ip-videokamera-ipc-hdw8441x-3d"},
    {"name": "Dahua IP видеокамера DH-IPC-HDW1239T1-LED-S5 2МП (2.8мм)", "price": "Уточняйте", "url": "http://www.dahua.md/page/dahua-ip-videokamera-dh-ipc-hdw1239t1-led-s5-2mp-28mm"},
    # Из категории Standalone DVR
    {"name": "Dahua DH-NVR4104HS-EI Сетевой регистратор на 4 канала", "price": "Уточняйте", "url": "http://www.dahua.md/page/dahua-dh-nvr4104hs-ei-setevoj-registrator-na-4-kanala"},
    {"name": "Dahua DHI-NVR5432-EI Сетевой регистратор на 32 каналов", "price": "Уточняйте", "url": "http://www.dahua.md/page/dahua-dhi-nvr5432-ei-setevoj-registrator-na-32-kanalov"},
    {"name": "Dahua DHI-NVR4232-EI 32 Canale Сетевой регистратор на 32 каналов", "price": "Уточняйте", "url": "http://www.dahua.md/page/dahua-dhi-nvr4232-ei-32-canale-setevoj-registrator-na-32-kanalov"},
    # Из категории Видеодомофоны
    {"name": "Smart Plug Dahua DHI-ICS1-W2 (868) Радиоуправляемая розетка", "price": "Уточняйте", "url": "http://www.dahua.md/page/smart-plug-dahua-dhi-ics1-w2-868-radioupravljaemaja-rozetka-so-schetchikom-elektroenergii"},
    {"name": "Input Expander Dahua DHI-ARM320-W2 (868) Входной расширитель", "price": "Уточняйте", "url": "http://www.dahua.md/page/input-expander-dahua-dhi-arm320-w2-868-vhodnoj-rasshiritel"},
    {"name": "WallSwitch Dahua DHI-ARM7012-W2 (868) Беспроводное реле", "price": "Уточняйте", "url": "http://www.dahua.md/page/wallswitch-dahua-dhi-arm7012-w2-868-besprovodnoe-rele"},
    {"name": "Panic Button (Dual) Dahua DHI-ARD822-W2 (868) Беспроводная тревожная кнопка", "price": "Уточняйте", "url": "http://www.dahua.md/page/panic-button-dual-dahua-dhi-ard822-w2-868-besprovodnaja-trevozhnaja-knopka"},
]

print(f"dahua.md: найдено {len(dahua_products)} товаров (цены только на странице товара, 1 цена найдена)")

# ============================================================
# 3. videosecurity.md — Magento Error
# ============================================================

videosecurity_status = "Сайт недоступен: Magento Exception Error. Exception printing is disabled. Error log record number: 918920944984 и 1022411091452"

# ============================================================
# Сохраняем CSV файлы
# ============================================================

# safe24.md
safe24_file = os.path.join(outdir, f"safe24md_products_{today}.csv")
with open(safe24_file, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['Сайт', 'Наименование', 'Цена', 'Валюта', 'Ссылка'])
    for p in all_safe24_products:
        w.writerow(['safe24.md', p['name'], p['price'], 'MDL', p['url']])
print(f"Сохранено: {safe24_file}")

# dahua.md
dahua_file = os.path.join(outdir, f"dahuamd_products_{today}.csv")
with open(dahua_file, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['Сайт', 'Наименование', 'Цена', 'Валюта', 'Ссылка'])
    for p in dahua_products:
        currency = 'USD' if 'USD' in p['price'] else ''
        w.writerow(['dahua.md', p['name'], p['price'], currency, p['url']])
print(f"Сохранено: {dahua_file}")

# videosecurity.md — записываем статус
video_file = os.path.join(outdir, f"videosecuritymd_status_{today}.csv")
with open(video_file, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['Сайт', 'Статус', 'Описание'])
    w.writerow(['videosecurity.md', 'Недоступен', videosecurity_status])
print(f"Сохранено: {video_file}")

# ============================================================
# Итоговый отчёт
# ============================================================
print()
print("=" * 80)
print("ИТОГОВЫЙ ОТЧЁТ ПО ПАРСИНГУ 3 САЙТОВ")
print("=" * 80)
print()
print(f"Дата: {today}")
print()
print("--- safe24.md (OpenCart) ---")
print(f"  Статус: ✅ Доступен, товары успешно спарсены")
print(f"  Найдено товаров: {len(all_safe24_products)}")
print(f"  Категории: Внутренние IP-камеры, Уличные IP-камеры, Охранная сигнализация (проводная/беспроводная)")
print(f"  Цены: в MDL (молдавских леях)")
print(f"  Бренды: Tiandy, Uniarch, Uniview, Reolink, TP-Link, ZKTeco, YouKey, Teletek, DSC, ZKTeco")
print(f"  Проблемы: Некоторые подкатегории (СКУД, домофоны) возвращают 404")
print(f"  CSV: {safe24_file}")
print()
print("--- videosecurity.md (Magento) ---")
print(f"  Статус: ❌ Недоступен")
print(f"  Причина: Magento Exception Error - анти-скрейпинг блокирует все запросы")
print(f"  Страницы /ru и /ru/catalog - обе возвращают ошибку Exception")
print(f"  Рекомендация: Исключить из cron-задач. Мониторить статус.")
print(f"  CSV: {video_file}")
print()
print("--- dahua.md (Media Sistem CMS) ---")
print(f"  Статус: ⚠️ Доступен частично")
print(f"  Найдено товаров: {len(dahua_products)}")
print(f"  Категории: Камеры, DVR/NVR, Видеодомофоны, I-Locks (цифровые замки)")
print(f"  Цены: Цены НЕ отображаются в каталоге. Только на отдельных страницах товаров.")
print(f"  Из найденных - только 1 товар с ценой: 239 USD (DH-IPC-HDBW5441R-ASE-HDMI)")
print(f"  Остальные: цена не указана (требуется уточнение)")
print(f"  Проблема: 504 Gateway Timeout НЕ подтвердился - сайт открывается через web_extract.")
print(f"  Но: сайт использует CMS без корзины - это каталог, а не интернет-магазин.")
print(f"  CSV: {dahua_file}")
print()
print("=" * 80)
print("Всего товаров собрано:", len(all_safe24_products) + len(dahua_products))
print("=" * 80)
