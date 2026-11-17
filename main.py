import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(_name_)
CORS(app)

tasks = [
    {"id": 1, "title": "مراجعة متطلبات المشروع السحابي", "done": False},
    {"id": 2, "title": "رفع الكود على GitHub", "done": True}
]

@app.route('/')
def home():
    return jsonify({"status": "Online", "message": "Task Manager Microservice API"})

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    
    new_task = {
        "id": len(tasks) + 1,
        "title": data['title'],
        "done": data.get('done', False)
    }
    tasks.append(new_task)
    return jsonify(new_task), 201

if _name_ == '_main_':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
