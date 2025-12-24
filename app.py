from flask import Flask, render_template, request, redirect, session
import sqlite3
from models import init_db

app = Flask(__name__)
app.secret_key = "task_secret"

def get_db():
    return sqlite3.connect("database.db")

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        result = cur.fetchone()
        if result:
            session['user_id'] = result[0]
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        db = get_db()
        db.execute("INSERT INTO users (username,password) VALUES (?,?)", (user,pwd))
        db.commit()
        return redirect('/')
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    db = get_db()
    tasks = db.execute("SELECT * FROM tasks WHERE user_id=?", (session['user_id'],)).fetchall()

    # Count tasks for summary
    pending = sum(1 for t in tasks if t[4]=='Pending')
    ongoing = sum(1 for t in tasks if t[4]=='Ongoing')
    completed = sum(1 for t in tasks if t[4]=='Completed')

    return render_template('dashboard.html', tasks=tasks, pending=pending, ongoing=ongoing, completed=completed)

@app.route('/add', methods=['GET','POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['description']
        tools = request.form['tools']
        status = request.form['status']
        db = get_db()
        db.execute("INSERT INTO tasks (title,description,tools,status,user_id) VALUES (?,?,?,?,?)",
                   (title, desc, tools, status, session['user_id']))
        db.commit()
        return redirect('/dashboard')
    return render_template('add_task.html')

@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit_task(id):
    db = get_db()
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['description']
        tools = request.form['tools']
        status = request.form['status']
        db.execute("UPDATE tasks SET title=?,description=?,tools=?,status=? WHERE id=?",
                   (title, desc, tools, status, id))
        db.commit()
        return redirect('/dashboard')
    task = db.execute("SELECT * FROM tasks WHERE id=?", (id,)).fetchone()
    return render_template('edit_task.html', task=task)

@app.route('/delete/<int:id>')
def delete_task(id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id=?", (id,))
    db.commit()
    return redirect('/dashboard')

@app.route('/task/<int:id>')
def task_detail(id):
    db = get_db()
    task = db.execute("SELECT * FROM tasks WHERE id=?", (id,)).fetchone()
    return render_template('task_detail.html', task=task)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)