import logging
import os
import random
import daemon
from flask import Flask, request, render_template, session, redirect, url_for
from database import db
from db import fetch_data_from_mongo
from daemon import DaemonContext
reports_collection = db.reports

current_dir = os.path.dirname(os.path.abspath(__file__))
# Set the path for the log file
log_file_path = os.path.join(current_dir, 'logfile.log')

# Configure the root logger
logging.basicConfig(level=logging.DEBUG, filename=log_file_path, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Get the root logger
logger = logging.getLogger()

# Since Flask uses its own logger, attach the file handler to Flask's logger to capture its logs as well
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
app = Flask(__name__)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)

app = Flask(__name__)
app.secret_key = 'your_secret_key'

verbs_collection = db['verbs3']
used_verb_ids = []
@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())


@app.route('/')
def index():
    global used_verb_ids
    verbs = list(verbs_collection.find({'_id': {'$nin': used_verb_ids}}))
    imperfective_verbs = [verb for verb in verbs if verb.get('infinite_pol_perfectiveness') == 'imperfective']

    if imperfective_verbs:
        cur_verb = random.choice(imperfective_verbs)
        cur_verb['_id'] = str(cur_verb['_id'])
        print('cur_verb: ', cur_verb['infinitive_pol'])

        # Select a random conjugation from the current verb to focus on
        current_conjugation = random.choice(cur_verb['conjugations'])
        target_pronoun_eng = current_conjugation['pronoun_eng']
        correct_option = current_conjugation['conjugation_pol']

        # Find matching conjugations from other verbs
        options = find_matching_conjugations(imperfective_verbs, cur_verb['_id'], target_pronoun_eng, correct_option)

        print('options: ', options)

        session['current_verb'] = {
            '_id': cur_verb['_id'],
            'infinitive_aze': cur_verb['infinitive_aze'],
            'infinitive_pol': cur_verb['infinitive_pol'],
            'conjugation_pol': correct_option
        }

        question = f"'{current_conjugation['pronoun_aze']} {current_conjugation['conjugation_aze']}'"

        return render_template('random_verb.html', feedback=session.get('feedback', ''),
                               score=session.get('score', 0), question=question, options=options)


def generate_options(cur_verb):
    correct_option = cur_verb['conjugation_pol']
    options = [correct_option]
    return options


def find_matching_conjugations(imperfective_verbs, excluded_verb_id, target_pronoun_eng, correct_conjugation):
    matching_options = []
    # Iterate over the verbs, excluding the current verb
    for verb in imperfective_verbs:
        if verb['_id'] == excluded_verb_id:
            continue  # Skip the current verb

        # Find the conjugation matching the target pronoun
        for conjugation in verb['conjugations']:
            if conjugation['pronoun_eng'] == target_pronoun_eng and conjugation['conjugation_pol'] != correct_conjugation:
                matching_options.append(conjugation['conjugation_pol'])

    # Ensure a diverse selection of options
    random.shuffle(matching_options)
    if len(matching_options) > 2:
        matching_options = matching_options[:2]

    # Add the correct option and ensure it's in the final list
    matching_options.append(correct_conjugation)
    random.shuffle(matching_options)  # Shuffle to mix the correct answer among the options

    return matching_options[:3]  # Return up to three options, including the correct one


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
    app.run(host='0.0.0.0', port=5000, use_reloader=False)


@app.route('/report_mistake', methods=['POST'])
def report_mistake():
    verb_id = request.form.get('verb_id')
    description = request.form.get('description')

    # Insert the report into the "reports" collection
    reports_collection.insert_one({
        'verb_id': verb_id,
        'description': description
    })

    # Redirect to a new page or back to the quiz, etc.
    return redirect(url_for('index'))  # Adjust as needed


if __name__ == '__main__':
    try:
        run_app()
    except Exception as e:
        logger.exception("Fatal error in main loop")

# if __name__ == '__main__':
#     CORS(app)
#     load_data()
#     app.run(host='0.0.0.0', port=5000)
