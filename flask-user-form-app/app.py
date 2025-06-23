from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

os.makedirs('database', exist_ok=True)

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database/users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL,
            identidad TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        identidad = request.form['identidad']
        save_user(nombre, correo, identidad)
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('database/users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    usuarios = cursor.fetchall()
    conn.close()
    return render_template('index.html', usuarios=usuarios)

def save_user(nombre, correo, identidad):
    conn = sqlite3.connect('database/users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (nombre, correo, identidad) VALUES (?, ?, ?)', (nombre, correo, identidad))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)