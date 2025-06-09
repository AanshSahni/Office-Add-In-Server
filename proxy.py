from flask import Flask, request, jsonify, abort, session
from flask_cors import CORS
import requests

app = Flask(__name__)
app.secret_key = "your-super-secret-key"
CORS(app)

API_URL = "http://13.126.140.151/api/login"
TOGETHER_URL = "https://api.together.xyz/v1/chat/completions"
TOGETHER_API_KEY = "be58cfd2fb73b1dac499050e5b8bcc020e8ecd9559bfdf2b3416f6378fe90f93"

def call_together_api(prompt, selected_text):
    combined_prompt = f"""
You are an AI assistant. A user has selected the following text from their document:

\"{selected_text}\"

Now they asked: \"{prompt}\"

Respond helpfully and clearly.
"""
    response = requests.post(
        TOGETHER_URL,
        headers={
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": combined_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }
    )
    response.raise_for_status()
    result = response.json()
    print("Response from Together API:", result)
    return result["choices"][0]["message"]["content"]

@app.route("/proxy-chat-bot", methods=["POST"])
def proxy_chat_bot():
    data = request.get_json()
    auth_header = request.headers.get("Authorization", "")

    prompt = data.get("prompt", "")
    selected_text = data.get("selected_text", "")

    try:
        reply = call_together_api(prompt, selected_text)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error from Together API: {str(e)}"}), 500

@app.route("/proxy-login", methods=["POST"])
def proxy_login():
    try:
        print("Received request for proxy-login")
        data = request.json
        Payload = {
            "email": data.get("username"),
            "password": data.get("password")
        }

        response = requests.post(API_URL, json=Payload)
        reply = response.json().get("token")
        session['token'] = reply
        print("Received token:", session.get('token'))
        session['token'] = reply
        return jsonify({"token": reply, "status_code": response.status_code}), 200

    except Exception as e:
        return jsonify({ "error": str(e) }), 500

if __name__ == "__main__":
    app.run(port=5443)
