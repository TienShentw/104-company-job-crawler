# 104 Company Job Crawler
透過多線程加速，快速爬取 104 人力銀行指定公司的所有公開職缺資訊（支援公司網址 / 職缺網址自動辨識），並自動輸出為 Excel 檔案。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/status-active-success)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🚀 功能特色

### 🔍 自動辨識公司 ID
支援以下格式輸入：

- `https://www.104.com.tw/company/18xr5ki`
- `https://www.104.com.tw/company/18xr5ki?jobsource=company_job`
- `https://www.104.com.tw/job/8w2u0`
- `https://www.104.com.tw/job/8w2u0?jobsource=company_job`

輸入任何一種，程式都能自動找出 company_id。

---

### ⚡ 多線程爬蟲（速度提升 5～10 倍）
使用 ThreadPoolExecutor 平行處理每個職缺內容頁面，效能大幅提升。

---

### 📝 自動輸出 Excel（含動態檔名）
匯出結果格式：

JobList_公司名_YYYY-MM-DD-HHMM.xlsx


---

### 🧩 使用 JSON API，不依賴 HTML
不會因畫面改版而失效，比傳統 BeautifulSoup 網頁爬蟲穩定得多。

---

## 📦 安裝

先安裝必要套件：

```bash
pip install -r requirements.txt
```
▶️ 使用方式

執行：
```bash
python crawler.py
```
輸入：

公司或職缺網址

要爬的頁數（建議直接輸入 1～5）

程式會自動：

辨識公司 ID

逐頁讀取職缺列表

多線程抓取職缺詳細內容

合併成 DataFrame

匯出 Excel 檔案到 Downloads

📁 範例輸出

JobList_國家原子能科技研究院_2025-12-02-1235.xlsx

📂 專案結構建議

104-company-job-crawler/

│── crawler.py              # 主程式

│── README.md               # 說明文件

│── requirements.txt        # 依賴套件

│── .gitignore              # 忽略的檔案類型

│── output/                 # Excel 匯出資料夾（可選）

│── screenshots/            # 程式執行示意圖（可選）

📜 License

MIT License

你可以任意使用、修改、商用。

✨ 作者

Developed by TienShenTW

如果喜歡這個專案，歡迎給顆 ⭐ Star 支持一下！
