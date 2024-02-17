from flask import Flask, request, render_template, session, redirect, url_for
from werkzeug.utils import secure_filename
import os
import random
from pymongo import MongoClient
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

uri = "mongodb+srv://admin:admin@cluster0.fl7vscu.mongodb.net/db01?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client['lang']  # Use your actual database name
verbs_collection = db['verbs']

@app.route('/')
def index():
    verbs = list(verbs_collection.find({}))
    if verbs:
        curVerb = random.choice(verbs)
        # Convert ObjectId to string
        curVerb['_id'] = str(curVerb['_id'])
        session['current_verb'] = curVerb
        question = f"Type the Polish form of the following English verb: {curVerb['infinitive_eng']}"
        return render_template('random_verb.html', verb=curVerb['infinitive_eng'], feedback=session.get('feedback', ''),
                               score=session.get('score', 0), question=question, verbs=verbs)
    else:
        return render_template('random_verb.html', feedback="No verbs found in the database. Please upload a file to add verbs.")

@app.route('/submit', methods=['POST'])
def submit_answer():
    curVerb = session.get('current_verb')
    if not curVerb:
        session['feedback'] = "There was an error with the current question. Please try again."
        return redirect(url_for('index'))

    user_answer = request.form['answer'].strip()
    correct_answer = curVerb['conjugation_pol']  # Ensure your documents have this field or adjust accordingly

    if user_answer.lower() == correct_answer.lower():
        session['feedback'] = "Correct!"
        session['score'] = session.get('score', 0) + 1
    else:
        session['feedback'] = f"Incorrect. The correct answer is {correct_answer}."

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)


#
# @app.route('/upload', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         file = request.files.get('file')
#         if file and file.filename.endswith('.xlsx'):
#             filename = secure_filename(file.filename)
#             filepath = os.path.join('temporary_directory', filename)
#             os.makedirs('temporary_directory', exist_ok=True)
#             file.save(filepath)
#             process_excel_file(filepath)
#             session['feedback'] = "File uploaded successfully!"
#             return redirect(url_for('index'))
#     return render_template('upload.html')
#
# def process_excel_file(filepath):
#     df = pd.read_excel(filepath)
#     # Processing Excel file logic here, potentially adding verbs to MongoDB
#     # Example: verbs_collection.insert_one({})
