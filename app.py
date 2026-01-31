import os
import json
import sqlite3
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, g, session
from werkzeug.utils import secure_filename

from config import Config
from services.parser import extract_text, allowed_file
from services.analyzer import analyze_resume
from services.suggestions import generate_suggestions, get_score_category
from services.ai_analyzer import get_ai_analysis, is_ai_available

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Database helper functions
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('database.db')
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize the database with required tables"""
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            resume_filename TEXT NOT NULL,
            resume_text TEXT NOT NULL,
            job_description TEXT NOT NULL,
            match_score REAL,
            analysis_data TEXT,
            ai_analysis TEXT,
            suggestions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db.commit()


# Initialize database once at startup
with app.app_context():
    init_db()


@app.before_request
def before_request():
    # Ensure session has an ID for tracking analyses
    if 'session_id' not in session:
        session['session_id'] = os.urandom(16).hex()


# Context processor to make is_ai_available accessible in templates
@app.context_processor
def utility_processor():
    return dict(is_ai_available=is_ai_available())


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        # Check if file was uploaded
        if 'resume' not in request.files:
            flash('No file uploaded.', 'danger')
            return render_template('analyze.html')

        file = request.files['resume']
        job_description = request.form.get('job_description', '').strip()

        if file.filename == '':
            flash('No file selected.', 'danger')
            return render_template('analyze.html')

        if not job_description:
            flash('Please enter a job description.', 'danger')
            return render_template('analyze.html')

        if not allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
            flash('Invalid file type. Only PDF and DOCX files are allowed.', 'danger')
            return render_template('analyze.html')

        # Save file with secure filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Extract text from resume
            resume_text = extract_text(filepath)

            if not resume_text.strip():
                flash('Could not extract text from the resume. Please ensure it contains readable text.', 'danger')
                os.remove(filepath)
                return render_template('analyze.html')

            # Basic keyword analysis
            analysis = analyze_resume(resume_text, job_description)

            # AI-powered analysis (if API key is configured)
            ai_analysis = None
            if is_ai_available():
                ai_analysis = get_ai_analysis(resume_text, job_description, analysis)

            # Generate rule-based suggestions (as fallback/supplement)
            suggestions = generate_suggestions(resume_text, analysis)

            # Save to database
            db = get_db()
            cursor = db.execute('''
                INSERT INTO analyses
                (session_id, resume_filename, resume_text, job_description, match_score,
                 analysis_data, ai_analysis, suggestions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.get('session_id'),
                filename,
                resume_text,
                job_description,
                analysis['match_score'],
                json.dumps(analysis),
                json.dumps(ai_analysis) if ai_analysis else None,
                json.dumps(suggestions)
            ))
            db.commit()

            return redirect(url_for('results', analysis_id=cursor.lastrowid))

        except Exception as e:
            flash(f'Error processing resume: {str(e)}', 'danger')
            if os.path.exists(filepath):
                os.remove(filepath)
            return render_template('analyze.html')

    return render_template('analyze.html')


@app.route('/results/<int:analysis_id>')
def results(analysis_id):
    db = get_db()
    row = db.execute('''
        SELECT * FROM analyses WHERE id = ?
    ''', (analysis_id,)).fetchone()

    if not row:
        flash('Analysis not found.', 'danger')
        return redirect(url_for('analyze'))

    # Load the full analysis data from JSON
    analysis_data = json.loads(row['analysis_data'])

    # Load AI analysis if available
    ai_analysis = None
    if row['ai_analysis']:
        ai_analysis = json.loads(row['ai_analysis'])

    analysis = {
        'id': row['id'],
        'resume_filename': row['resume_filename'],
        'job_description': row['job_description'],
        'match_score': analysis_data.get('match_score', 0),
        'matched_skills': analysis_data.get('matched_skills', []),
        'missing_skills': analysis_data.get('missing_skills', []),
        'extra_skills': analysis_data.get('extra_skills', []),
        'high_priority_missing': analysis_data.get('high_priority_missing', []),
        'matched_categories': analysis_data.get('matched_categories', {}),
        'missing_categories': analysis_data.get('missing_categories', {}),
        'jd_experience_level': analysis_data.get('jd_experience_level', 'not specified'),
        'jd_years_required': analysis_data.get('jd_years_required'),
        'jd_education': analysis_data.get('jd_education', []),
        'resume_skill_count': analysis_data.get('resume_skill_count', 0),
        'jd_skill_count': analysis_data.get('jd_skill_count', 0),
        'suggestions': json.loads(row['suggestions']),
        'ai_analysis': ai_analysis,
        'created_at': row['created_at']
    }

    score_category, score_class = get_score_category(analysis['match_score'])
    analysis['score_category'] = score_category
    analysis['score_class'] = score_class

    return render_template('results.html', analysis=analysis)


@app.route('/history')
def history():
    db = get_db()
    # Show analyses from current session
    rows = db.execute('''
        SELECT id, resume_filename, match_score, created_at
        FROM analyses
        WHERE session_id = ?
        ORDER BY created_at DESC
        LIMIT 20
    ''', (session.get('session_id'),)).fetchall()

    analyses = []
    for row in rows:
        score_category, score_class = get_score_category(row['match_score'])
        analyses.append({
            'id': row['id'],
            'resume_filename': row['resume_filename'],
            'match_score': row['match_score'],
            'score_category': score_category,
            'score_class': score_class,
            'created_at': row['created_at']
        })

    return render_template('history.html', analyses=analyses)


if __name__ == '__main__':
    app.run(debug=True)
