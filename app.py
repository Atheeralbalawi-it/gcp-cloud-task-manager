from flask import Flask, render_template_string, request, redirect, url_for
import os

app = Flask(__name__)

tasks = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Cloud Task Manager</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h2 { color: #333; text-align: center; }
        form { display: flex; gap: 10px; margin-bottom: 20px; }
        input[type="text"] { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 10px 15px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        ul { list-style-type: none; padding: 0; }
        li { background: #f9f9f9; margin-bottom: 8px; padding: 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; border-left: 4px solid #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Cloud Task Manager 🚀</h2>
        <form method="POST" action="/add">
            <input type="text" name="task" placeholder="أدخل مهمة جديدة..." required>
            <button type="submit">إضافة مهمة</button>
        </form>
        <ul>
            {% for task in tasks %}
                <li>{{ task }}</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    task = request.form.get('task')
    if task:
        tasks.append(task)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
