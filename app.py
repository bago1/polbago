from flask import Flask, request, render_template, session, redirect, url_for
from werkzeug.utils import secure_filename
import os
import random
from pymongo import MongoClient
import pandas as pd
from database import db

app = Flask(__name__)
app.secret_key = 'your_secret_key'

verbs_collection = db['verbs']


@app.route('/')
def index():
    used_verb_ids = session.get('used_verb_ids', [])
    print("used_verb_ids size: ", len(used_verb_ids))
    verbs = list(verbs_collection.find({'_id': {'$nin': used_verb_ids}}))
    if verbs:
        cur_verb = random.choice(verbs)
        cur_verb['_id'] = str(cur_verb['_id'])  # Ensure '_id' is set as a string
        random_conjugation = random.choice(cur_verb['conjugations'])

        session['current_verb'] = {
            '_id': cur_verb['_id'],  # Ensure '_id' is set in the session
            'infinitive_eng': cur_verb['infinitive_eng'],
            'conjugation_pol': random_conjugation['conjugation_pol']  # Store correct Polish form for answer validation
        }

        question = f"Type the Polish form of '{random_conjugation['pronoun_eng']} {random_conjugation['conjugation_eng']}'"

        return render_template('random_verb.html', feedback=session.get('feedback', ''),
                               score=session.get('score', 0), question=question, verbs=verbs)

    else:
        return render_template('random_verb.html',
                               feedback="No verbs found in the database. Please upload a file to add verbs.")


@app.route('/submit', methods=['POST'])
def submit_answer():
    if 'current_verb' not in session or not session['current_verb']:
        session['feedback'] = "There was an error with the current question. Please try again."
        return redirect(url_for('index'))

    user_answer = request.form['answer'].strip()
    correct_answer = session['current_verb']['conjugation_pol']

    if user_answer.lower() == correct_answer.lower():
        session['feedback'] = "Correct!"
        session['score'] = session.get('score', 0) + 1
        used_verb_ids = session.get('used_verb_ids', [])
        used_verb_ids.append(session['current_verb']['_id'])
        session['used_verb_ids'] = used_verb_ids
    else:
        session['feedback'] = f"Incorrect. The correct answer is {correct_answer}."

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
