import os
from openai import OpenAI

from dotenv import load_dotenv
from flask import Flask, Response, render_template, request

load_dotenv()

app = Flask(__name__)

client = OpenAI(api_key= os.getenv("OPENAI_API_KEY"))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/prompt', methods=['POST'])
def prompt():
    messages = request.json['messages']
    conversation = build_conversation_dict(messages)

    return Response(event_stream(conversation), mimetype='text/event-stream')

def event_stream(conversation: list[dict]) -> str:
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        stream=True,
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content

def build_conversation_dict(messages: list) -> list[dict]:
    return [
        {"role": "user" if i % 2 == 0 else "assistant", "content": message}
        for i, message in enumerate(messages)
    ]


if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)
