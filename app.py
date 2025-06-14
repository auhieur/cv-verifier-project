from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import fitz  # PyMuPDF for PDF handling
from docx import Document
from io import BytesIO
import requests
import json
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

@app.route("/")
def index():
    return render_template("index.html")


def extract_text_from_pdf(file_stream):
    doc = fitz.open(stream=file_stream.read(), filetype="pdf")
    full_text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        full_text += text.strip() + "\n\n"
    doc.close()
    return full_text


def extract_content_from_docx(file_stream):
    file_bytes = BytesIO(file_stream.read())
    document = Document(file_bytes)
    html_content = ""
    for paragraph in document.paragraphs:
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
    for table in document.tables:
        html_content += "<table>"
        for row in table.rows:
            html_content += "<tr>"
            for cell in row.cells:
                cell_text = ""
                for p in cell.paragraphs:
                    for run in p.runs:
                        cell_text += run.text
                html_content += f"<td>{cell_text}</td>"
            html_content += "</tr>"
        html_content += "</table>\n"
    return html_content


def call_gemini_api(cv_content):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY 環境變數未設定。")

    prompt = f"""
        您是一個專業的履歷驗證分析師。請仔細審查以下履歷內容。
        如果這是從 DOCX 文件轉換而來，內容將是 HTML 格式；如果是從 PDF 轉換而來，內容將嘗試保留段落和行距。
        模擬搜尋公開資訊（例如官方網站、新聞報導）驗證資訊真實性，若有疑點請以下列格式回傳：

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

    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "hasDiscrepancies": {"type": "BOOLEAN"},
                    "discrepancies": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "item": {"type": "STRING"},
                                "reason": {"type": "STRING"},
                                "organizationName": {"type": "STRING"},
                                "organizationWebsite": {"type": "STRING"},
                                "publicInfoLink": {"type": "STRING"}
                            }
                        }
                    }
                },
                "required": ["hasDiscrepancies", "discrepancies"]
            }
        }
    }

    response = requests.post(
        f"{GEMINI_BASE_URL}?key={GEMINI_API_KEY}",
        headers=headers,
        data=json.dumps(payload),
        timeout=60
    )
    response.raise_for_status()
    return response.json()


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

        llm_response = call_gemini_api(cv_content)

        if isinstance(llm_response, dict) and "candidates" in llm_response:
            candidate = llm_response["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                response_text = candidate["content"]["parts"][0]["text"]
                parsed_llm_json = json.loads(response_text)
                return jsonify(parsed_llm_json), 200

        return jsonify({"error": "LLM 回應格式無效或為空"}), 500

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except ConnectionError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": f"伺服器內部錯誤: {e}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)