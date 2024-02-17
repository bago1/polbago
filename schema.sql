DROP TABLE IF EXISTS verbs;
CREATE TABLE verbs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    infinitive_eng TEXT NOT NULL,
    infinitive_pol TEXT NOT NULL
);

DROP TABLE IF EXISTS english_conjugations;
CREATE TABLE english_conjugations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verb_id INTEGER,
    pronoun TEXT NOT NULL,
    conjugation TEXT NOT NULL,
    FOREIGN KEY (verb_id) REFERENCES verbs(id)
);

DROP TABLE IF EXISTS polish_conjugations;
CREATE TABLE polish_conjugations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verb_id INTEGER,
    pronoun TEXT NOT NULL,
    conjugation TEXT NOT NULL,
    FOREIGN KEY (verb_id) REFERENCES verbs(id)
);
