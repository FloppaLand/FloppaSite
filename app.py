import os
import psycopg2
from flask import Flask, render_template, flash, url_for, redirect, request, flash, send_from_directory, jsonify
from hashlib import md5
import re
import time
app = Flask(__name__)



def get_db_connection():
    conn = psycopg2.connect(host='db',
                            port=5432,
                            database='db',
                            user="postgres",
                            password="example")
    return conn


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        conn = get_db_connection()
        cur = conn.cursor()

        username = request.form.get('username')
        password = md5(request.form.get('password').encode()).hexdigest()
        if username == "":
            error = 'Введите логин'
            return render_template('register.html', error=error)
        elif not re.match(r'^[a-zA-Z0-9_]{3,16}$', username):
            error = f'Логин дожен содержать только: цифры (0-9), латинские буквы (a-z) или подчёркивание(_) и быть от 3 до 16 символов {username}'
            return render_template('register.html', error=error)
        elif request.form.get('password') == "":
            error = 'Введите пароль'
            return render_template('register.html', error=error)

        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        if cur.fetchall():
            error = 'Вы уже были зарегестрированы'
            return render_template('register.html', error=error)

        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()

        cur.close()
        conn.close()
        message = 'Вы зарегестрированы'
        return render_template('register.html', message=message)

    return render_template('register.html')
@app.route('/skin', methods=['GET','POST'])
def skin():
    if request.method == 'POST':
        conn = get_db_connection()
        cur = conn.cursor()

        username = request.form.get('username')
        password = md5(request.form.get('password').encode()).hexdigest()

        cur.execute(f"SELECT password FROM users WHERE username = '{username}'")
        db_pass = cur.fetchone()
        if db_pass != None:
            if db_pass[0] == password:
                if 'file' not in request.files:
                    return 'No files provided'+ str(request.files)
                file = request.files['file']
                
                if file.filename == '':
                    error = 'Файл скина не выбран'
                    return render_template('skin.html', error=error)
                if file and file.filename.rsplit('.', 1)[1].lower() == 'png':
                    file.save(os.path.join("./data/skins", username + ".png"))
                    message = 'Скин успешно загружен!'
                    return render_template('skin.html', message=message)
                else:
                    error = 'Скин должен быть в формате png'
                    return render_template('skin.html', error=error)
            else:
                error = 'Неверный пароль'
            return render_template('skin.html', error=error)
        else:
            error = 'Пользователь не найден'
            return render_template('skin.html', error=error)

        cur.close()
        conn.close()

    return render_template('skin.html')

@app.route('/skins/<string:filename>')
def get_image(filename):
    if os.path.exists(os.getcwd() + "/data/skins/" + filename):
        return send_from_directory(os.getcwd() + "/data/skins", path=filename, as_attachment=False)
    else:
        return send_from_directory(os.getcwd() + "/data/skins/default", path="floppa.png", as_attachment=False)

@app.route('/notfound')
def notfound():
    return render_template('notfound.html')

@app.errorhandler(404)
def handle_404_error(error):
    print(error)
    return render_template('notfound.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)


