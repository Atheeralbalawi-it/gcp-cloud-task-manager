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

# واجهة محسنة وأنيقة مع زر الحذف الفعّال
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Cloud Task Manager 🚀</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; margin: 0; padding: 50px; display: flex; justify-content: center; }
        .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 6px 15px rgba(0,0,0,0.1); width: 450px; }
        h2 { color: #2c3e50; text-align: center; margin-bottom: 25px; }
        form { display: flex; gap: 10px; margin-bottom: 25px; }
        input[type="text"] { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; }
        input[type="text"]:focus { border-color: #007bff; }
        button { padding: 12px 18px; background-color: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: bold; transition: background 0.2s; }
        button:hover { background-color: #0056b3; }
        ul { list-style-type: none; padding: 0; }
        li { background: #f8f9fa; margin-bottom: 10px; padding: 12px 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; border-right: 5px solid #007bff; box-shadow: 0 2px 4px rgba(0,0,0,0.03); }
        .delete-btn { background-color: #dc3545; color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; }
        .delete-btn:hover { background-color: #c82333; }
    </style>
</head>
<body>
    <div class="container">
        <h2>إدارة المهام الذكية 🚀</h2>
        <form method="POST" action="/add">
            <input type="text" name="task" placeholder="أدخل مهمة جديدة..." required>
            <button type="submit">إضافة</button>
        </form>
        <ul>
            {% for task in tasks %}
                <li>
                    <span>{{ task.content }}</span>
                    <a href="/delete/{{ task.id }}" style="text-decoration: none;">
                        <button class="delete-btn">حذف</button>
                    </a>
                </li>
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
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_task(id):
    task_to_delete = Task.query.get_or_404(id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('index'))

if _name_ == '_main_':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
