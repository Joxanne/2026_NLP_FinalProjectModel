# NLP 課程檢索問答系統

本專案為國立中興大學 NLP 課程期末專案，實作一個基於 LLM API 的課程問答系統。  
系統將課程專屬資訊注入系統提示詞（System Prompt），使模型能針對課程相關問題給出精確回答。

---

## 功能

- **互動式問答**：在終端機輸入問題，即時獲得 LLM 回答
- **批次推論**：讀入 CSV（欄位：`題目`），輸出包含答案的 CSV（欄位：`題目`, `答案`）
- **課程資料注入**：自動讀取 `data/NLP-Course-Info.csv` 與 `data/slides/` 投影片，組成系統提示詞

---

## 專案結構

```
retrieval-system/
├── main.py              # 互動式終端機問答
├── batch_infer.py       # 批次推論（輸入/輸出 CSV）
├── src/
│   ├── llm_client.py    # OpenAI 相容 API 封裝（台智雲 AFS）
│   └── prompt_builder.py# 系統提示詞建構
├── data/
│   ├── NLP-Course-Info.csv  # 課程 Q&A 資料
│   └── slides/          # 投影片 .txt 檔（可選）
├── .env.example         # 環境變數範本
└── requirements.txt     # Python 套件需求
```

---

## 環境設定

### 1. 安裝套件

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows bash
# 或 .venv\Scripts\Activate.ps1  # PowerShell
pip install -r requirements.txt
```

### 2. 設定 API 金鑰

複製範本並填入你的 API 金鑰：

```bash
cp .env.example .env
```

編輯 `.env`：

```
TWCC_API_KEY=你的-API-KEY
TWCC_API_URL=https://api-ams.twcc.ai/api
TWCC_MODEL=llama3.3-ffm-70b-32k-chat
TWCC_TIMEOUT=60
TWCC_MAX_RETRY=2
TWCC_MAX_CONCURRENT=10
```

> API 金鑰請至 [台智雲 AFS](https://afs.twcc.ai) 的「公用模式 - API 金鑰管理」頁面取得。

---

## 使用方式

### 互動式問答

```bash
python main.py
```

輸入問題後按 Enter，輸入 `exit` 離開。

### 批次推論

準備一個 `input.csv`，欄位需包含 `題目`：

```csv
題目
什麼是時間均勻的馬可夫過程？
HMM 的三個假設是什麼？
```

執行：

```bash
python batch_infer.py input.csv output.csv
```

輸出的 `output.csv` 會新增 `答案` 欄位。

---

## 自訂提示詞

編輯 `src/prompt_builder.py` 中的 `_SYSTEM_TEMPLATE`，可調整模型的回答規則、語氣與輸出格式。

---

## 新增課程資料

- **Q&A 資料**：編輯 `data/NLP-Course-Info.csv`，欄位為 `關鍵問題` 與 `答案`
- **投影片內容**：將 `.txt` 檔放入 `data/slides/`，會自動附加至提示詞

---

## 技術架構

| 元件 | 說明 |
|------|------|
| LLM | 台智雲 AFS `llama3.3-ffm-70b-32k-chat` |
| API | OpenAI 相容介面（`openai` Python SDK） |
| 提示詞策略 | System Prompt 注入課程資料 |
| 批次並行 | `asyncio.Semaphore` 控制並行數 |
