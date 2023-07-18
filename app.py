import os
import time
import json
import random

from g4f import Model, ChatCompletion, Provider
from flask import Flask, request, Response, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/v1/chat/completions", methods=['POST'])
@app.route("/v1/completions", methods=['POST'])
def chat_completions():
    streaming = request.json.get('stream', False)
    model = request.json.get('model', 'gpt-3.5-turbo')
    messages = request.json.get('messages')
    
    response = ChatCompletion.create(model=model, stream=streaming,
                                     messages=messages)
    
    if not streaming:
        while 'curl_cffi.requests.errors.RequestsError' in response:
            response = ChatCompletion.create(model=model, stream=streaming,
                                             messages=messages)

        completion_timestamp = int(time.time())
        completion_id = ''.join(random.choices(
            'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=28))

        return {
            'id': 'chatcmpl-%s' % completion_id,
            'object': 'chat.completion',
            'created': completion_timestamp,
            'model': model,
            'usage': {
                'prompt_tokens': None,
                'completion_tokens': None,
                'total_tokens': None
            },
            'choices': [{
                'message': {
                    'role': 'assistant',
                    'content': response
                },
                'finish_reason': 'stop',
                'index': 0
            }]
        }

    def stream():
        for token in response:
            completion_timestamp = int(time.time())
            completion_id = ''.join(random.choices(
                'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=28))

            completion_data = {
                'id': f'chatcmpl-{completion_id}',
                'object': 'chat.completion.chunk',
                'created': completion_timestamp,
                'model': model,
                'choices': [
                    {
                        'delta': {
                            'content': token
                        },
                        'index': 0,
                        'finish_reason': None
                    }
                ]
            }

            yield 'data: %s\n\n' % json.dumps(completion_data, separators=(',' ':'))
            time.sleep(0.1)

    return app.response_class(stream(), mimetype='text/event-stream')
    
@app.route("/v1/dashboard/billing/subscription")
@app.route("/dashboard/billing/subscription")
def billing_subscription():
  return jsonify({
    "id": "sub_0947613321",
    "plan": "Enterprise",
    "status": "active",
    "start_date": "2023-01-01",
    "end_date": None,
    "current_period_start": "2023-01-01",
    "current_period_end": None,
    "trial_start": None,
    "trial_end": None,
    "cancel_at_period_end": False,
    "canceled_at": None,
    "created_at": "2023-01-01",
    "updated_at": "2023-01-01",
    "hard_limit_usd": 99999.99
  })


@app.route("/v1/dashboard/billing/usage")
@app.route("/dashboard/billing/usage")
def billing_usage():
  return jsonify({"total": 99999.99, "total_usage": 1.01})

@app.route("/v1/models")
@app.route("/models")
def models():
  import g4f.models
  model = {"data":[]}
  for i in g4f.models.ModelUtils.convert:
    print(i)
    model['data'].append({
            "id": i,
            "object": "model",
            "owned_by": g4f.models.ModelUtils.convert[i].base_provider,
            "tokens": 99999,
            "fallbacks": None,
            "endpoints": [
                "/v1/chat/completions"
            ],
            "limits": None,
            "permission": []
        })
  return jsonify(model)

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({
        "error": {
            "message": f"Invalid URL ({request.method} /)",
            "type": "invalid_request_error",
            "param": None,
            "code": None
        }
    }), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({
        "error": {
            "message": "Something went wrong on our end",
            "type": "internal_server_error",
            "param": None,
            "code": None
        }
    }), 500

@app.errorhandler(415)
def unsupported_media_type(e):
    return jsonify({
        "error": {
            "message": "Unsupported media type",
            "type": "unsupported_media_type",
            "param": None,
            "code": None
        }
    }), 415
if __name__ == '__main__':
    config = {
        'host': '0.0.0.0',
        'port': 80,
        'debug': False
    }

    app.run(**config)