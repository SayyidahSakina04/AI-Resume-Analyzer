# AI Resume Analyzer

A free, AI-powered web application that analyzes resumes against job descriptions and provides actionable feedback to improve your chances of landing interviews.

## Features

- **Match Score** - Get a percentage score showing how well your resume matches the job
- **Skills Gap Analysis** - See matched, missing, and extra skills
- **AI-Powered Insights** - Personalized feedback using Google Gemini AI
- **Improvement Suggestions** - Actionable tips to optimize your resume
- **ATS Optimization** - Tips to pass Applicant Tracking Systems
- **No Registration Required** - 100% free to use

## Screenshots

| Home | Results |
|------|---------|
| Upload resume & paste job description | Get detailed analysis with AI feedback |

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, Bootstrap 5, Jinja2
- **AI**: Google Gemini API
- **Database**: SQLite
- **PDF Parsing**: pypdf
- **DOCX Parsing**: python-docx

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/ai-resume-analyzer.git
cd ai-resume-analyzer
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
```

Get your free Gemini API key from: https://aistudio.google.com/apikey

### 5. Run the application

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Project Structure

```
ai-resume-analyzer/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
│
├── services/
│   ├── ai_analyzer.py     # Google Gemini AI integration
│   ├── analyzer.py        # Keyword matching & skill extraction
│   ├── parser.py          # PDF/DOCX text extraction
│   └── suggestions.py     # Rule-based suggestions
│
├── templates/             # HTML templates
├── static/css/            # Stylesheets
└── uploads/               # Uploaded resume files
```

## How It Works

1. **Upload Resume** - Upload your resume in PDF or DOCX format
2. **Paste Job Description** - Copy and paste the job posting
3. **Analysis** - The app extracts skills and compares them
4. **AI Feedback** - Google Gemini provides personalized suggestions
5. **Results** - View your match score, skill gaps, and improvement tips

## AI Features (with Gemini API)

When you configure the Gemini API key, you get:

- Overall impression of your resume fit
- Strengths and weaknesses analysis
- Personalized improvement suggestions
- Rewritten bullet point examples
- Interview likelihood prediction
- ATS compatibility score

## Without API Key

The app works without an API key using:

- Keyword-based skill matching
- Rule-based suggestions
- Experience level detection
- Resume section analysis

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | No | Google Gemini API key for AI features |
| `SECRET_KEY` | No | Flask secret key (auto-generated if not set) |

## Deployment

### PythonAnywhere (Free)

1. Upload files to PythonAnywhere
2. Set up virtual environment
3. Configure WSGI file
4. Add environment variables in `.env`

### Render (Free)

1. Connect GitHub repository
2. Set environment variables in dashboard
3. Deploy

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- Google Gemini for AI capabilities
- Bootstrap for UI components
- Flask community for the excellent framework
