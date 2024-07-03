import json
import os
import socket

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from flask import Flask, jsonify, request, send_file, send_from_directory
from dotenv import load_dotenv

# 🔥 FILL THIS OUT FIRST! 🔥
# Get your Gemini API key by:
# - Selecting "Add Gemini API" in the "Project IDX" panel in the sidebar
# - Or by visiting https://g.co/ai/idxGetGeminiKey
load_dotenv()

app = Flask(__name__)

@app.route("/")
def index():
    return send_file('web/index.html')

@app.route("/flasktest/get")
def flask_get_test():
    return jsonify({ "sucess": "Flask GET method test" })

@app.route("/api/generate", methods=["POST"])
def generate_api():
    if request.method == "POST":
        if os.environ["GOOGLE_API_KEY"] == 'TODO':
            return jsonify({ "error": '''
                To get started, get an API key at
                https://g.co/ai/idxGetGeminiKey and enter it in
                main.py
                '''.replace('\n', '') })
        try:
            req_body = request.get_json()
            content = req_body.get("contents")
            model = ChatGoogleGenerativeAI(model=req_body.get("model"))
            message = HumanMessage(
                content=content
            )
            response = model.stream([message])
            def stream():
                for chunk in response:
                    yield 'data: %s\n\n' % json.dumps({ "text": chunk.content })

            return stream(), {'Content-Type': 'text/event-stream'}

        except Exception as e:
            return jsonify({ "error": str(e) })


# """
# A route for generating content based on a given model.
# Handles POST requests and streams text content from the gemini model.
# """
@app.route("/generativeai/models/<path:model>:generateContent", methods=["POST"])
def gemini_generate_content(model):
    if request.method == "POST":
        if os.environ["GOOGLE_API_KEY"] == 'TODO':
            return jsonify({ "error": '''
                To get started, get an API key at
                https://g.co/ai/idxGetGeminiKey and enter it in
                main.py
                '''.replace('\n', '') })
        try:
            req_body = request.get_json()
            content = req_body.get("contents")
            ai_model = ChatGoogleGenerativeAI(model=model)
            message = HumanMessage(
                content=content
            )
            response = ai_model.stream([message])
            def stream():
                for chunk in response:
                    yield 'data: %s\n\n' % json.dumps({ "text": chunk.content })

            return stream(), {'Content-Type': 'text/event-stream'}

        except Exception as e:
            return jsonify({ "error": str(e) })

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.254.254.254', 1))
        address =s.getsockname()[0]
    except Exception:
        address = '127.0.0.1'
    finally:
        s.close()
    return address

if __name__ == "__main__":
    app.run(debug=True, host=get_local_ip(),  port=int(os.environ.get('PORT', 8082)))
