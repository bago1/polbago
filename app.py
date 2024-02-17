from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from werkzeug.utils import secure_filename
import sqlite3
import pandas as pd
import random
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize the database (Assuming init_db function is defined in db.py)
with app.app_context():
    from db import get_db, init_db
    init_db(app)

@app.route('/')
def index():
    all_verbs = fetch_all_verbs()

    if 'score' not in session:
        session['score'] = 0
        session['feedback'] = None

    if 'correct_answer' not in session:
        # Placeholder for setting the first question if not set
        session['correct_answer'] = "nazywam się"

    question = "What's the next question?"  # Placeholder for actual question selection logic
    return render_template('random_verb.html', verbs=all_verbs, feedback=session.get('feedback'), score=session['score'])

@app.route('/add_verb', methods=['POST'])
def add_verb():
    verb_data = request.json
    db = get_db()
    db.execute('INSERT INTO verbs (infinitive, english_1, polish_1) VALUES (?, ?, ?)',
               [verb_data['infinitive'], verb_data['english_1'], verb_data['polish_1']])
    db.commit()
    return jsonify({"message": "Verb added successfully!"}), 201

@app.route('/get_verb/<infinitive>')
def get_verb(infinitive):
    db = get_db()
    verb = db.execute('SELECT * FROM verbs WHERE infinitive = ?', (infinitive,)).fetchone()
    if verb:
        return jsonify(dict(verb))
    return jsonify({"message": "Verb not found"}), 404

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and file.filename.endswith('.xlsx'):
        filename = secure_filename(file.filename)
        filepath = os.path.join('temporary_directory', filename)
        file.save(filepath)
        process_excel_file(filepath)
        return redirect(url_for('index'))
    return redirect(url_for('index'))

def process_excel_file(filepath):
    df = pd.read_excel(filepath)
    db = get_db()
    for _, row in df.iterrows():
        # Assuming your Excel columns are named 'Infinitive', 'English_1', 'Polish_1', etc.
        db.execute('INSERT INTO verbs (infinitive, english_1, polish_1, english_2, polish_2, english_3, polish_3, english_4, polish_4, english_5, polish_5, english_6, polish_6) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (row['Infinitive'], row.get('English_1', ''), row.get('Polish_1', ''), row.get('English_2', ''), row.get('Polish_2', ''), row.get('English_3', ''), row.get('Polish_3', ''), row.get('English_4', ''), row.get('Polish_4', ''), row.get('English_5', ''), row.get('Polish_5', ''), row.get('English_6', ''), row.get('Polish_6', '')))
    db.commit()

def fetch_all_verbs():
    db = get_db()
    cursor = db.execute('SELECT * FROM verbs')
    verbs = cursor.fetchall()
    return verbs
if __name__ == '__main__':
    app.run(debug=True)
