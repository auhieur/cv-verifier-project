# CV 履歷驗證專案

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v3-blueviolet?style=flat-square&logo=tailwindcss)](https://tailwindcss.com/)
[![Google Gemini API](https://img.shields.io/badge/Google_Gemini_API-2.0_Flash-orange?style=flat-square&logo=google-gemini)](https://ai.google.dev/gemini-api)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg?style=flat-square)](LICENSE)

這個專案是一個輕量級的 Web 應用程式，旨在利用 Google Gemini 大型語言模型（LLM）來**模擬履歷內容的真實性核查**。它提供了一個直觀的前端介面，讓使用者可以輕鬆上傳或貼上履歷內容，後端則負責與 Gemini LLM 互動，分析履歷中的學歷、工作經驗、比賽獎項等資訊，並標識出潛在的疑點。

## 專案目標

在當今數位化的招聘環境中，履歷的真實性日益受到關注。本專案的目標是：

* **提供初步驗證：** 快速識別履歷中可能存在的不一致或無法核實的資訊。
* **提升效率：** 為招聘人員或個人提供一個自動化的輔助工具，以節省手動核查的時間。
* **探索 LLM 應用：** 展示如何將大型語言模型應用於實際的資訊驗證場景。

**重要提示：** 本工具的驗證結果基於 LLM 的模擬判斷，僅供參考，不應作為最終決策的唯一依據。實際的資訊核實仍需透過官方渠道和人工審查進行。

## 功能特色

* **多格式履歷支援：**
    * 支援上傳 `txt`、`pdf` 和 `docx` 格式的履歷檔案。
    * 後端會自動從這些檔案中提取文本內容。
* **彈性輸入方式：**
    * 使用者可以直接在網頁介面中貼上履歷文本。
* **AI 驅動的驗證邏輯：**
    * 利用 Google Gemini 2.0 Flash 模型作為核心，對提取的履歷內容進行深度分析。
    * 模型會模擬搜尋公開資訊，判斷履歷中的各項條目（如學歷、工作經驗、獎項等）是否存在疑點。
* **詳細的疑點報告：**
    * 如果發現潛在疑點，系統會清晰地列出每個疑點的詳細資訊，包括：
        * **項目名稱 (item):** 履歷中被質疑的具體內容。
        * **原因 (reason):** 簡潔說明為何該項目被標記為疑點（例如：「無公開紀錄」、「資料不符」、「資訊不完整」）。
        * **組織名稱 (organizationName):** 與該項目相關的官方組織或機構名稱。
        * **組織網站 (organizationWebsite):** 該組織的官方網站連結。
        * **公開資訊連結 (publicInfoLink):** 模擬找到的相關公開資訊連結（若有）。
* **直觀的使用者介面：**
    * 採用 Tailwind CSS 構建，介面簡潔、現代且具有玻璃擬物化效果。
    * 提供即時的檔案選擇狀態和載入指示。
    * 錯誤訊息和驗證結果清晰呈現。
* **響應式設計：**
    * 介面針對不同螢幕尺寸（桌面、平板、手機）進行了優化，提供一致且良好的使用者體驗。

## 技術棧

* **前端：**
    * **HTML5:** 頁面結構。
    * **Tailwind CSS:** 快速構建響應式和美觀的 UI。
    * **JavaScript (ES Modules):** 處理前端邏輯、DOM 操作和與後端 API 的非同步通訊。
* **後端 (Python Flask):**
    * **Flask:** 輕量級且靈活的 Web 框架，用於構建 RESTful API。
    * **Flask-CORS:** 處理跨域資源共享，確保前端可以從不同網域存取後端。
    * **PyMuPDF (`fitz`):** 用於高效地從 PDF 檔案中提取文本。
    * **`python-docx`:** 用於從 DOCX 檔案中提取內容，並嘗試轉換為 HTML 格式以保留結構。
    * **`requests`:** 用於向 Google Gemini API 發送 HTTP 請求。
    * **`json`:** 處理 JSON 數據的序列化和反序列化。
    * **`os`:** 用於讀取環境變數（例如 API Key）。
    * **`time`:** 用於實現 API 呼叫的重試延遲。
    * **`gunicorn`:** 生產環境中推薦的 WSGI HTTP 伺服器，用於部署 Flask 應用。
* **大型語言模型：**
    * **Google Gemini 2.0 Flash:** 透過其 API 進行文本分析和驗證邏輯的實現。

## 安裝與執行 (本地開發環境)

### 前置條件

在開始之前，請確保您的系統已安裝以下軟體：

* **Python 3.8 或更高版本**
* **`pip`** (Python 套件管理器，通常隨 Python 一起安裝)
* **一個 Google Gemini API Key**：您可以在 [Google AI Studio](https://ai.google.dev/gemini-api/docs/get-started/python) 網站上免費獲取。

### 步驟

1.  **複製專案：**
    打開您的終端機或命令提示字元，並執行以下指令來複製本專案的程式碼：
    ```bash
    git clone [https://github.com/YOUR_GITHUB_USERNAME/cv-verifier-project.git](https://github.com/YOUR_GITHUB_USERNAME/cv-verifier-project.git)
    cd cv-verifier-project
    ```
    **請將 `YOUR_GITHUB_USERNAME` 替換為您自己的 GitHub 用戶名。**

2.  **建立並啟用虛擬環境 (強烈建議)：**
    虛擬環境有助於隔離專案依賴，避免與其他 Python 專案衝突。
    ```bash
    python -m venv venv
    # 在 Windows 上啟用虛擬環境：
    .\venv\Scripts\activate
    # 在 macOS/Linux 上啟用虛擬環境：
    source venv/bin/activate
    ```

3.  **安裝後端依賴：**
    在虛擬環境啟用後，安裝 `requirements.txt` 中列出的所有 Python 函式庫：
    ```bash
    pip install -r requirements.txt
    ```

4.  **設定 Google Gemini API Key：**
    您的 Gemini API Key 必須作為環境變數提供給後端應用程式。**請勿將您的 API Key 直接寫入程式碼中！**
    * **Linux/macOS (在終端機中)：**
        ```bash
        export GEMINI_API_KEY="您的_實際_GEMINI_API_KEY"
        ```
    * **Windows (CMD 命令提示字元)：**
        ```bash
        set GEMINI_API_KEY="您的_實際_GEMINI_API_KEY"
        ```
    * **Windows (PowerShell)：**
        ```powershell
        $env:GEMINI_API_KEY="您的_實際_GEMINI_API_KEY"
        ```
    **請務必將 `您的_實際_GEMINI_API_KEY` 替換為您從 Google AI Studio 獲取的真實 API Key。**
    **注意：** 這種設定方式只在當前終端機會話中有效。如果您關閉終端機，需要重新設定。在部署到 Railway 等平台時，您將在該平台的配置介面中設定此環境變數。

5.  **啟動後端服務：**
    在已啟用虛擬環境的終端機中，執行以下指令啟動 Flask 後端：
    ```bash
    python app.py
    ```
    後端服務將預設在 `http://127.0.0.1:8080` 上運行。您應該會在終端機中看到類似 `Running on http://127.0.0.1:8080/` 的輸出。

6.  **開啟前端頁面：**
    本專案的前端是一個純 HTML/JavaScript 檔案。您無需額外啟動 Web 伺服器，只需在您的瀏覽器中直接打開 `index.html` 檔案即可。
    * 例如，在檔案瀏覽器中找到 `index.html`，然後雙擊打開。

## 部署到 Railway (或類似 PaaS 平台)

本專案設計為易於部署到 Railway、Vercel (僅限前端，後端需獨立部署) 或其他 PaaS (Platform as a Service) 平台。以下是針對 Railway 的一般步驟：

1.  **將專案推送到 GitHub 儲存庫：** 確保您的本地變更已提交並推送到您 Fork 的 GitHub 儲存庫。
2.  **在 Zeabur 上建立新專案：** 登錄 Zeabur，點擊 "New Project"，選擇 "Deploy from GitHub repo"，"或是一鍵部屬"。
3.  **連接您的 GitHub 儲存庫：** 授權 Zeabur 存取您的儲存庫，並選擇 `cv-verifier-project` 儲存庫。
4.  **設定環境變數：** 在專案設定中，導航到 "Variables" 或 "Environment Variables" 部分，添加一個名為 `GEMINI_API_KEY` 的變數，並填入您的 Gemini API Key。
5.  **部署：** 將會自動檢測您的 `requirements.txt` 和 `app.py`，並使用 Gunicorn 啟動您的 Flask 應用程式。部署完成後，Zeabur 會提供一個公開的 URL 給您的後端服務。

**關鍵部署步驟：更新前端的後端 URL**

當您的後端服務成功部署到 Zeabur 或其他雲平台後，它會獲得一個公開的 URL（例如：`https://your-backend-name.up.app`）。**您必須將這個實際的後端 URL 更新到前端 `index.html` 檔案中**，否則前端將無法連接到您的後端服務。

打開 `index.html` 檔案，找到 `<script type="module">` 標籤內的以下這行：

```javascript
const BACKEND_URL = ''; // 預設留空，需手動配置
```

**請將 `''` (空字串) 替換為您部署後端服務的實際公開 URL。例如：**

```javascript
const BACKEND_URL = '[https://your-backend-name.up.app](https://your-backend-name.up.app)'; // 替換為您實際的後端 URL
```
**完成修改後，請務必將更新後的 `index.html` 檔案重新提交並推送到您的 GitHub 儲存庫，以確保前端頁面使用正確的後端地址。**

## 使用說明

1.  **開啟應用程式：** 在瀏覽器中打開 `index.html`。
2.  **輸入履歷內容：**
    * 您可以直接在「請在此貼上或輸入履歷內容」的文本框中輸入或貼上履歷文本。
    * 或者，點擊「選擇檔案」按鈕，上傳您的 `txt`、`pdf` 或 `docx` 格式的履歷檔案。
        * **注意：** 如果您同時輸入文本和上傳檔案，上傳檔案將會優先，並清空文本框內容。
3.  **點擊驗證：** 點擊「驗證履歷」按鈕。
4.  **查看結果：**
    * 如果驗證過程中發現潛在疑點，結果區塊將會顯示每個疑點的詳細資訊。
    * 如果初步驗證未發現明顯疑點，則會顯示「初步驗證未發現明顯疑點」的訊息。
5.  **備註：** 頁面底部有重要備註，提醒您本工具的性質和限制。

## 專案結構

```
├── app.py              # Flask 後端應用程式，處理檔案上傳和 LLM 互動
├── index.html          # 前端使用者介面 (HTML, Tailwind CSS, JavaScript)
├── requirements.txt    # Python 依賴列表，列出所有必要的 Python 函式庫
└── README.md           # 專案說明文件 (您正在閱讀的檔案)
```

## 常見問題排解

* **`錯誤: 解析 LLM 回應的 JSON 字串失敗: Unterminated string...`**
    * 這通常表示 Gemini 模型返回的 JSON 內容不完整或被截斷。
    * **解決方案：** 確保您的 `app.py` 中的 `generationConfig` 包含了 `maxOutputTokens` 參數，並設定一個足夠大但合理的數值（例如 `2048` 或 `4096`），以限制模型輸出長度，防止其在生成完整 JSON 之前被截斷。同時，簡化對 `reason` 等可能產生長文本的欄位的提示，讓模型生成更簡潔的內容。

* **`GEMINI_API_KEY 環境變數未設定。`**
    * 這表示後端無法找到您的 Gemini API Key。
    * **解決方案：** 確保您已按照「設定 Gemini API Key」步驟正確設定了環境變數。在部署到Zeabur時，請在環境變數設定中添加 `GEMINI_API_KEY`。

* **`後端服務 URL 未配置。請在 index.html 中設定 BACKEND_URL`(前端錯誤)**
    * 這表示前端的 `index.html` 中的 `BACKEND_URL` 變數仍為空字串或不正確。
    * **解決方案：** 請按照「關鍵部署步驟：更新前端的後端 URL」中的說明，將 `index.html` 中的 `BACKEND_URL` 替換為您部署在Zeabur上的後端服務的實際公開 URL。

* **`API請求失敗 (狀態碼: 500)` 或 `伺服器內部錯誤`**
    * 這表示後端服務在處理請求時發生了未預期的錯誤。
    * **解決方案：** 檢查部署日誌或本地運行 `app.py` 的終端機輸出，查找詳細的錯誤訊息。常見原因可能包括依賴未安裝、程式碼邏輯錯誤或與外部服務（如 Gemini API）的通訊問題。

## 貢獻

我們非常歡迎對本專案做出貢獻！無論是 Bug 報告、功能建議、程式碼改進還是文件修正，您的貢獻都將使這個專案變得更好。

### 貢獻流程：

1.  **Fork 專案：** 點擊 GitHub 頁面右上角的 "Fork" 按鈕，將本專案複製到您的個人帳戶下。
2.  **複製您的 Fork：**
    ```bash
    git clone [https://github.com/您的GitHub用戶名/cv-verifier-project.git](https://github.com/您的GitHub用戶名/cv-verifier-project.git)
    cd cv-verifier-project
    ```
3.  **建立新的功能分支：** 為您的新功能或 Bug 修正建立一個獨立的分支。
    ```bash
    git checkout -b feature/your-feature-name
    # 或
    git checkout -b bugfix/fix-issue-description
    ```
4.  **進行變更：** 在您的分支上進行程式碼修改和測試。
5.  **提交變更：** 使用有意義的提交訊息提交您的變更。
    ```bash
    git add .
    git commit -m "feat: Add a new awesome feature"
    # 或
    git commit -m "fix: Resolve an issue with file upload"
    ```
6.  **推送到您的 Fork：**
    ```bash
    git push origin feature/your-feature-name
    ```
7.  **開啟 Pull Request：** 訪問您 Fork 的 GitHub 儲存庫頁面，點擊 "Compare & pull request" 按鈕，填寫詳細的說明，然後提交 Pull Request。

## 許可協議

本專案根據 **Apache-2.0 許可協議** 發布，這意味著您可以自由地使用、修改和分發本專案，但需遵守許可協議中的條款。詳情請參閱專案根目錄下的 `LICENSE` 檔案。
