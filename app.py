# app.py - Python Flask 後端應用程式

from flask import Flask, request, jsonify
from flask_cors import CORS # 引入 CORS 擴展以處理跨域請求
import fitz  # PyMuPDF 用於 PDF 處理
from docx import Document # python-docx 用於 DOCX 處理
import requests # 用於發送 HTTP 請求給新的 API
import json # 用於處理 JSON 數據
import os # 用於讀取環境變數

# 簡化 Flask app 初始化，因為它不再服務靜態文件或模板
app = Flask(__name__)

# 將 CORS 設定為允許所有來源 (用於動態 Vercel URL)
CORS(app)

# 設定 API 金鑰
# 在生產環境中，請務必從環境變數中讀取 API 金鑰，不要硬編碼！
# ChatAnywhere 服務兼容 OpenAI API，請確保您在 Render 環境中設定 OPENAI_API_KEY
API_KEY = os.environ.get("OPENAI_API_KEY", "") 

# === 新增的除錯訊息：打印 API_KEY 的值 (除錯完成後務必移除！) ===
# 這行非常關鍵，用來檢查 Render 服務實際讀取到的 API_KEY 值
print(f"DEBUG: Backend starting. API_KEY (first 5 chars): {API_KEY[:5]}... Length: {len(API_KEY)}")
# =========================================================================

# 將 API_BASE_URL 設定為新的 API 端點
_API_BASE_URL = "https://api.chatanywhere.org/v1/chat/completions" # ChatAnywhere 的標準 completions 端點

# === 新增的除錯訊息 (保留以確認部署版本) ===
print(f"DEBUG: _API_BASE_URL is set to: {_API_BASE_URL}")
# ===============================================

# --- 檔案解析函數 ---

def extract_text_from_pdf(file_stream):
    """從 PDF 檔案流中提取文本，嘗試保留排版。"""
    try:
        doc = fitz.open(stream=file_stream.read(), filetype="pdf")
        full_text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            # 使用 get_text("text") 提取文本，它會嘗試保留基本佈局
            text = page.get_text("text")
            full_text += text.strip() + "\n\n" # 每頁之間加兩個換行符
        doc.close()
        return full_text
    except Exception as e:
        print(f"PDF 解析錯誤: {e}")
        raise ValueError(f"無法解析 PDF 檔案: {e}")

def extract_content_from_docx(file_stream):
    """從 DOCX 檔案流中提取內容，並轉換為 HTML 格式。"""
    try:
        document = Document(file_stream)
        html_content = ""
        for paragraph in document.paragraphs:
            # 簡單地將段落轉換為 HTML <p> 標籤，保留粗體、斜體等
            html_paragraph = "<p>"
            for run in paragraph.runs:
                text = run.text
                if run.bold:
                    text = f"<strong>{text}</strong>"
                if run.italic:
                    text = f"<em>{text}</em>"
                html_paragraph += text
            html_paragraph += "</p>"
            html_content += html_paragraph + "\n"

        # 處理表格
        for table in document.tables:
            html_content += "<table>"
            for row in table.rows:
                html_content += "<tr>"
                for cell in row.cells:
                    # 簡單地將表格單元格內容轉換為 HTML <td> 標籤
                    cell_text = ""
                    for p in cell.paragraphs:
                        for run in p.runs:
                            cell_text += run.text
                    html_content += f"<td>{cell_text}</td>"
                html_content += "</tr>"
            html_content += "</table>"
            html_content += "\n" # 表格後加換行

        return html_content
    except Exception as e:
        print(f"DOCX 解析錯誤: {e}")
        raise ValueError(f"無法解析 DOCX 檔案: {e}")

# --- LLM 互動函數 ---

def call_llm_api(cv_content):
    """呼叫 LLM API 進行履歷驗證。"""
    if not API_KEY:
        # 打印到控制台，因為這是後端錯誤
        print("錯誤: API_KEY 環境變數未設定或為空！請確認您已在 Render 環境中設定 OPENAI_API_KEY。")
        raise ValueError("API_KEY 環境變數未設定。")

    # 針對 ChatAnywhere (OpenAI 兼容) API 調整 payload 結構
    # 您需要選擇一個 ChatAnywhere 支持的模型，例如 'gpt-3.5-turbo' 或 'gpt-4'
    model_name = "gpt-3.5-turbo" # 替換為 ChatAnywhere 支援的模型名稱

    prompt = f"""
        您是一個專業的履歷驗證分析師。請仔細審查以下履歷內容。
        請注意，如果這是從 DOCX 文件轉換而來，內容將是 **HTML 格式**；如果是從 PDF 轉換而來，內容將嘗試保留原始的段落和行距。
        請您根據這些格式資訊來理解內容的結構（例如：標題、列表、粗體字、表格等），並識別任何潛在的造假或盜用內容，特別是關於學歷、工作經驗、比賽或獎項、證書等。
        模擬您正在搜尋公開資訊（例如：官方網站、公開資料庫、新聞報導）以驗證這些資訊的真實性。
        如果發現任何疑點或無法核實的內容，請將其標記為「疑點」。
        對於每個疑點，請提供以下資訊：
        1. 項目名稱 (item): 履歷中被質疑的具體內容。
        2. 原因 (reason): 為什麼這是一個疑點，例如「無公開紀錄」、「資料不符」、「資訊不完整」。
        3. 組織名稱 (organizationName): 與該項目相關的官方組織或機構名稱。
        4. 組織網站 (organizationWebsite): 該組織的官方網站連結。
        5. 公開資訊連結 (publicInfoLink): 模擬找到的相關公開資訊連結（若有）。

        請**嚴格按照以下 JSON 格式**回傳結果。
        **重要提示：`hasDiscrepancies` 欄位必須是布林值，表示是否有疑點。`discrepancies` 欄位必須是一個陣列，即使沒有疑點或沒有找到具體項目，也**必須是一個空陣列**。

        {{
          "hasDiscrepancies": boolean,
          "discrepancies": [
            {{
              "item": "string",
              "reason": "string",
              "organizationName": "string",
              "organizationWebsite": "string",
              "publicInfoLink": "string"
            }}
          ]
        }}

        以下是履歷內容：
        {cv_content}
    """

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}' # OpenAI-compatible API 需要 Bearer Token 認證
    }
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"} # 要求模型以 JSON 格式回應
    }

    try:
        # 增加 timeout 參數，設置為 60 秒
        response = requests.post(
            _API_BASE_URL, 
            headers=headers, 
            data=json.dumps(payload),
            timeout=60 # 設置請求超時為 60 秒
        )
        response.raise_for_status() # 如果響應狀態碼不是 2xx，則引發 HTTPError
        
        llm_response = response.json()
        
        # 檢查 OpenAI 兼容 API 的回應結構
        if 'choices' in llm_response and len(llm_response['choices']) > 0:
            message_content = llm_response['choices'][0]['message']['content']
            # 將 OpenAI 兼容的回應轉換回您前端期望的 Gemini 結構
            return {'candidates': [{'content': {'parts': [{'text': message_content}]}}]}
        else:
            print(f"錯誤: LLM 回應格式不符預期或為空: {llm_response}")
            raise ValueError("LLM 回應格式無效或為空。")

    except requests.exceptions.Timeout as e:
        print(f"錯誤: 呼叫 LLM API 超時: {e}")
        raise ConnectionError(f"無法連接到 LLM API: 超時。 {e}")
    except requests.exceptions.RequestException as e:
        # 打印更詳細的錯誤信息，包括響應文本（如果有的話）
        error_message = f"呼叫 LLM API 失敗: {e}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_content = e.response.json()
                error_message += f", API回應: {error_content}"
            except json.JSONDecodeError:
                error_content = e.response.text
                error_message += f", API回應文本: {error_content[:200]}..." # 只顯示前200字節
        print(f"錯誤: {error_message}")
        raise ConnectionError(f"無法連接到 LLM API: {error_message}")
    except json.JSONDecodeError as e:
        print(f"錯誤: 解析 LLM API 回應失敗: {e}")
        raise ValueError(f"LLM API 回應格式不正確: {e}")

# --- Flask 路由 ---

# 新增的健康檢查路由
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route('/upload_cv', methods=['POST'])
def upload_cv():
    if 'cvFile' not in request.files:
        return jsonify({"error": "沒有檔案被上傳"}), 400

    file = request.files['cvFile']
    if file.filename == '':
        return jsonify({"error": "沒有選擇檔案"}), 400

    file_extension = file.filename.rsplit('.', 1)[1].lower()
    cv_content = ""

    try:
        if file_extension == 'txt':
            cv_content = file.stream.read().decode('utf-8')
        elif file_extension == 'pdf':
            cv_content = extract_text_from_pdf(file.stream)
        elif file_extension == 'docx':
            cv_content = extract_content_from_docx(file.stream)
        else:
            return jsonify({"error": "不支援的檔案格式，請上傳 .txt, .pdf 或 .docx 檔案"}), 400
        
        if not cv_content.strip():
            return jsonify({"error": "檔案內容為空或無法提取有效文本"}), 400

        # 將處理後的內容發送給 LLM
        llm_response = call_llm_api(cv_content) 

        # 這裡可以加入更多對 llm_response 結構的檢查
        if isinstance(llm_response, dict) and "candidates" in llm_response and \
           len(llm_response["candidates"]) > 0 and "content" in llm_response["candidates"][0] and \
           "parts" in llm_response["candidates"][0]["content"] and \
           len(llm_response["candidates"][0]["content"]["parts"]) > 0:
            
            # 從LLM回應中提取JSON字串
            response_text = llm_response["candidates"][0]["content"].parts[0].text
            
            # 解析LLM回應的JSON字串
            parsed_llm_json = json.loads(response_text)

            # 進一步驗證其內部結構是否符合responseSchema
            if "hasDiscrepancies" in parsed_llm_json and isinstance(parsed_llm_json["hasDiscrepancies"], bool) and \
               "discrepancies" in parsed_llm_json and isinstance(parsed_llm_json["discrepancies"], list):
                return jsonify(parsed_llm_json), 200
            else:
                return jsonify({"error": "LLM 回應的 JSON 結構不符預期"}), 500
        else:
            return jsonify({"error": "LLM 回應格式無效或為空"}), 500

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except ConnectionError as e:
        return jsonify({"error": str(e)}), 503 # Service Unavailable
    except Exception as e:
        print(f"伺服器內部錯誤: {e}")
        return jsonify({"error": f"伺服器內部錯誤: {e}"}), 500

# Fly.io/Render 會將請求發送到 $PORT 環境變數指定的埠號
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)