import os
from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'
verbs = [
    {
        "infinitive": "nazywać się",
        "questions": [
            {"english": "I am called", "polish": "nazywam się"},
            {"english": "You are called", "polish": "nazywasz się"},
            {"english": "He/She/It is called", "polish": "nazywa się"},
            {"english": "We are called", "polish": "nazywamy się"},
            {"english": "You (plural) are called", "polish": "nazywacie się"},
            {"english": "They are called", "polish": "nazywają się"}
        ]
    },
]

@app.route('/', methods=['GET', 'POST'])
def show_random_verb():
    if 'score' not in session:
        session['score'] = 0  # Initialize score
        session['feedback'] = None  # Initialize feedback

    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.xlsx'):
            filename = secure_filename(file.filename)
            directory = 'temporary_directory'
            if not os.path.exists(directory):
                os.makedirs(directory)  # Create the directory if it does not exist
            filepath = os.path.join(directory, filename)
            file.save(filepath)
            process_excel_file(filepath)
            session['feedback'] = "File uploaded successfully!"

        user_answer = request.form.get('answer', '').strip().lower()
        correct_answer = session.get('correct_answer', '').strip().lower()

        if user_answer and user_answer == correct_answer:
            session['score'] += 1
            session['feedback'] = 'Correct!'
        elif user_answer:
            session['feedback'] = f"Incorrect! The correct answer was: {session['correct_answer']}"

    random_verb = random.choice(verbs)
    question_item = random.choice(random_verb['questions'])
    session['correct_answer'] = question_item['polish']

    question = f"{question_item['english']} (in Polish)?"
    return render_template('random_verb.html', question=question, feedback=session.get('feedback'), score=session['score'], infinitive=random_verb['infinitive'])

def process_excel_file(filepath):
    df = pd.read_excel(filepath)
    for _, row in df.iterrows():
        verb = {
            "infinitive": row['Infinitive'],
            "questions": []
        }
        for i in range(1, 7):
            verb['questions'].append({"english": row[f'English {i}'], "polish": row[f'Polish {i}']})
        verbs.append(verb)

if __name__ == '__main__':
    app.run(debug=True)
