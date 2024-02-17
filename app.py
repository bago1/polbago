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
    verbs = list(verbs_collection.find({}))
    if verbs:
        curVerb = random.choice(verbs)
        curVerb['_id'] = str(curVerb['_id'])
        randomConjugation = random.choice(curVerb['conjugations'])

        session['current_verb'] = {
            'infinitive_eng': curVerb['infinitive_eng'],
            'conjugation_pol': randomConjugation['conjugation_pol']  # Store correct Polish form for answer validation
        }

        question = f"Type the Polish form of '{randomConjugation['pronoun_eng']} {randomConjugation['conjugation_eng']}'"

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
    else:
        session['feedback'] = f"Incorrect. The correct answer is {correct_answer}."

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
