from flask import Flask, request, jsonify, render_template, session, redirect, url_for, g
from werkzeug.utils import secure_filename
import sqlite3
import pandas as pd
import os
import random  # Add this import statement


app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'verbs.db'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with open('schema.sql', mode='r') as f:
            db.executescript(f.read())
        db.commit()

@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

@app.route('/')
def index():
    all_verbs = fetch_all_verbs()
    print("All verbs: ")
    print(all_verbs)
    session['question'] = "Type the Polish form of the following English verb:"

    if all_verbs:
        session['current_verb'] = random.choice(all_verbs)
        return render_template('random_verb.html', verb=session['current_verb'], feedback=session.get('feedback', ''), score=session.get('score', 0), question=session.get('question', ''), verbs=all_verbs)
    else:
        return render_template('random_verb.html', feedback="No verbs found in the database. Please upload a file to add verbs.")

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    print("Request method: ")
    print(request.method)


    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.xlsx'):
            filename = secure_filename(file.filename)
            filepath = os.path.join('temporary_directory', filename)
            if not os.path.exists('temporary_directory'):
                os.makedirs('temporary_directory')
            file.save(filepath)
            process_excel_file(filepath)
            session['feedback'] = "File uploaded successfully!"
            return redirect(url_for('index'))
    return render_template('upload.html')

def process_excel_file(filepath):
    df = pd.read_excel(filepath)
    db = get_db()
    for _, row in df.iterrows():
        db.execute('''INSERT INTO verbs (infinitive, english_1, polish_1, english_2, polish_2, english_3, polish_3, english_4, polish_4, english_5, polish_5, english_6, polish_6)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (row['Infinitive'], row.get('English_1', ''), row.get('Polish_1', ''),
                    row.get('English_2', ''), row.get('Polish_2', ''), row.get('English_3', ''),
                    row.get('Polish_3', ''), row.get('English_4', ''), row.get('Polish_4', ''),
                    row.get('English_5', ''), row.get('Polish_5', ''), row.get('English_6', ''), row.get('Polish_6', '')))
    db.commit()

@app.route('/submit', methods=['POST'])
def submit_answer():
    user_answer = request.form['answer']
    correct_answer = session.get('current_verb')['polish_1']  # Assuming Polish translation is stored in 'polish_1' column
    if user_answer.lower() == correct_answer.lower():
        session['feedback'] = "Correct!"
        session['score'] += 1
    else:
        session['feedback'] = f"Incorrect. The correct answer is {correct_answer}."
    return redirect(url_for('index'))

def fetch_all_verbs():
    db = get_db()
    cursor = db.execute('SELECT * FROM verbs')
    verbs = [dict(row) for row in cursor.fetchall()]
    return verbs

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
