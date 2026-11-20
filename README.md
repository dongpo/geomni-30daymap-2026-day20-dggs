# Day20 — Hexagons: DGGS × Taipei transit

同一個地方，兩種交通節奏。最新版 v3，待使用者審稿。

下載並開啟 `portable.html` 即可操作，無須安裝 GIS 或連接底圖服務。`index.html` 搭配 data.js/vendor 亦可使用。

使用 DGGAL ISEA3H level 16/17/18，透過共同網格編碼與時間鍵，對照 2023 年 12 月臺北市捷運出站人次與 YouBike 轉乘租借子集。可選格、切換尺度、播放小時、比較平假日、追溯站點及匯出 CSV。

## 資料與限制

詳見 [DATA-NOTES.txt](DATA-NOTES.txt)、source/manifest.json 與 evidence。兩者不是同一批人的接駁紀錄；YouBike 非全部租借；2023 統計使用 2026 站點定位，缺值不補零。不宣稱完整 OGC API-DGGS 服務或認證。

## 重現

原始月檔以 gzip 無損壓縮保存，避免 GitHub 單檔限制。於本目錄執行：

```sh
gunzip -k source/metro-202312.csv.gz source/youbike-202312.csv.gz
python3 -m venv .venv
.venv/bin/pip install -r requirements-lock.txt
.venv/bin/python scripts/build.py
.venv/bin/python scripts/verify_sample.py
.venv/bin/python scripts/package.py
```

上游授權與來源逐項見 DATA-NOTES.txt；政府資料開放授權條款第1版，保留來源標示。vendor 保留原套件授權。審稿資料上傳不表示 Facebook 文章獲批准。
