"""
AI-powered resume analysis using Google Gemini
"""

import os
import json
import google.generativeai as genai

# Configure Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')


def is_ai_available():
    """Check if AI analysis is available"""
    return bool(GEMINI_API_KEY)


def configure_gemini():
    """Configure the Gemini API"""
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        return True
    return False


def get_ai_analysis(resume_text, job_description, basic_analysis):
    """
    Get AI-powered analysis using Google Gemini

    Args:
        resume_text: Extracted text from resume
        job_description: Job description text
        basic_analysis: Results from basic keyword analysis

    Returns:
        dict: AI-generated insights
    """
    if not configure_gemini():
        return None

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""You are an expert career coach and resume analyst. Analyze this resume against the job description and provide actionable feedback.

RESUME:
{resume_text[:4000]}

JOB DESCRIPTION:
{job_description[:2000]}

BASIC ANALYSIS RESULTS:
- Match Score: {basic_analysis.get('match_score', 0)}%
- Matched Skills: {', '.join(basic_analysis.get('matched_skills', [])[:10])}
- Missing Skills: {', '.join(basic_analysis.get('missing_skills', [])[:10])}

Provide your analysis in the following JSON format (respond ONLY with valid JSON, no markdown):
{{
    "overall_impression": "2-3 sentence overall assessment of the resume fit",
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
    "missing_skills_analysis": "Explain which missing skills are critical vs nice-to-have",
    "experience_relevance": "How relevant is the candidate's experience to this role",
    "improvement_suggestions": [
        {{
            "area": "specific area to improve",
            "current": "what's wrong or missing",
            "suggestion": "specific actionable advice"
        }},
        {{
            "area": "another area",
            "current": "what's wrong",
            "suggestion": "how to fix it"
        }},
        {{
            "area": "third area",
            "current": "issue",
            "suggestion": "solution"
        }}
    ],
    "rewritten_bullets": [
        {{
            "original_context": "brief description of a weak point in resume",
            "improved": "rewritten version with metrics and action verbs"
        }}
    ],
    "keywords_to_add": ["keyword1", "keyword2", "keyword3"],
    "ats_score": 75,
    "interview_likelihood": "low/medium/high",
    "summary": "One paragraph summary of what the candidate should focus on"
}}
"""

        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Clean up response - remove markdown code blocks if present
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        response_text = response_text.strip()

        # Parse JSON response
        ai_result = json.loads(response_text)
        return ai_result

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return {
            "error": "Could not parse AI response",
            "overall_impression": "AI analysis encountered an error. Please try again.",
            "strengths": [],
            "weaknesses": [],
            "improvement_suggestions": [],
            "summary": "Analysis could not be completed."
        }
    except Exception as e:
        print(f"AI analysis error: {e}")
        return {
            "error": str(e),
            "overall_impression": "AI analysis is currently unavailable.",
            "strengths": [],
            "weaknesses": [],
            "improvement_suggestions": [],
            "summary": "Please check your API key and try again."
        }
