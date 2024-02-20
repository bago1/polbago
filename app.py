import logging
from flask import Flask, request, render_template, session, redirect, url_for
from werkzeug.utils import secure_filename
import os
import random
from pymongo import MongoClient
import pandas as pd
import json
from database import db
from db import load_data
from flask_cors import CORS
logging.basicConfig(level=logging.DEBUG)
import daemon
from daemon import DaemonContext



app = Flask(__name__)
app.secret_key = 'your_secret_key'

verbs_collection = db['verbs']
used_verb_ids = []
@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

@app.route('/')
def index():
    data = load_data()
    print("\nlen of data", len(data))
    global used_verb_ids
    print("used_verb_ids size: ", len(used_verb_ids))
    verbs = list(verbs_collection.find({'_id': {'$nin': used_verb_ids}}))
    if verbs:
        cur_verb = random.choice(verbs)
        cur_verb['_id'] = str(cur_verb['_id'])
        random_conjugation = random.choice(cur_verb['conjugations'])
        print("infinitive_pol: ", cur_verb['infinitive_pol'])
        session['current_verb'] = {
            '_id': cur_verb['_id'],
            'infinitive_eng': cur_verb['infinitive_eng'],
            'infinitive_pol': cur_verb['infinitive_pol'],  # Ensure this line is present
            'conjugation_pol': random_conjugation['conjugation_pol']
        }

        question = f"Type the Polish form of '{random_conjugation['pronoun_eng']} {random_conjugation['conjugation_eng']}'"

        return render_template('random_verb.html', feedback=session.get('feedback', ''),
                               score=session.get('score', 0), question=question, verbs=verbs)

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
        used_verb_ids.append(session['current_verb']['_id'])
    else:
        session['feedback'] = f"Incorrect. The correct answer is {correct_answer}."

    return redirect(url_for('index'))

@app.route('/clear_results', methods=['POST'])
def clear_results():
    session.pop('score', None)
    session.pop('used_verb_ids', None)
    return redirect(url_for('index'))

@app.route('/clear_cache', methods=['POST'])
def clear_cache():
    global cached_data
    cached_data = None
    return redirect(url_for('index'))

@app.after_request
def log_response_info(response):
    app.logger.debug('Response status: %s', response.status)
    return response
def run_app():
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    with daemon.DaemonContext():
        run_app()