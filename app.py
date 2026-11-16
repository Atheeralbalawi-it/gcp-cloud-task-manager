import os
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(_name_)

# إعداد قاعدة البيانات المحلية SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# تعريف جدول المهام في قاعدة البيانات
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Cloud Task Manager</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f6f8; margin: 0; padding: 50px; display: flex; justify-content: center; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 400px; }
        h2 { color: #333; text-align: center; }
        form { display: flex; gap: 10px; margin-bottom: 20px; }
        input[type="text"] { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
        button { padding: 10px 15px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        ul { list-style-type: none; padding: 0; }
        li { background: #f9f9f9; margin-bottom: 8px; padding: 10px; border-radius: 5px; border-left: 4px solid #007bff; }
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
                <li>{{ task.content }}</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template_string(HTML_TEMPLATE, tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    task_content = request.form.get('task')
    if task_content:
        new_task = Task(content=task_content)
        db.db.session.add(new_task) if hasattr(db, 'db') else db.session.add(new_task)
        db.session.commit()
    return redirect(url_for('index'))

if _name_ == '_main_':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
