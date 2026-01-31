"""
Enhanced rule-based suggestion engine for resume improvement
"""

import re

# Action verbs by category
ACTION_VERBS = {
    'leadership': ["led", "managed", "directed", "supervised", "coordinated", "oversaw"],
    'achievement': ["achieved", "accomplished", "exceeded", "delivered", "completed"],
    'creation': ["created", "designed", "developed", "built", "implemented", "launched"],
    'improvement': ["improved", "enhanced", "optimized", "streamlined", "reduced", "increased"],
    'technical': ["engineered", "architected", "automated", "integrated", "deployed", "configured"],
    'analysis': ["analyzed", "evaluated", "assessed", "researched", "investigated", "identified"]
}

ALL_ACTION_VERBS = [verb for verbs in ACTION_VERBS.values() for verb in verbs]

# Important resume sections
IMPORTANT_SECTIONS = ["experience", "education", "skills", "projects", "summary", "objective"]


def check_action_verbs(resume_text):
    """Check which action verbs are used in the resume"""
    text_lower = resume_text.lower()
    found = {category: [] for category in ACTION_VERBS}

    for category, verbs in ACTION_VERBS.items():
        for verb in verbs:
            if verb in text_lower:
                found[category].append(verb)

    total_found = sum(len(v) for v in found.values())
    return found, total_found


def check_quantifiable_achievements(resume_text):
    """Check for numbers/metrics in resume"""
    patterns = [
        r'\d+%',           # Percentages
        r'\$[\d,]+',       # Dollar amounts
        r'\d+\+',          # X+ format
        r'\d{2,}',         # Numbers with 2+ digits
        r'#\d+',           # Rankings
    ]

    metrics = []
    for pattern in patterns:
        matches = re.findall(pattern, resume_text)
        metrics.extend(matches)

    return len(metrics), metrics[:10]  # Return count and first 10 examples


def check_resume_length(resume_text):
    """Analyze resume length"""
    word_count = len(resume_text.split())
    line_count = len(resume_text.split('\n'))
    return word_count, line_count


def check_sections(resume_text):
    """Check for important resume sections"""
    text_lower = resume_text.lower()
    found = [s for s in IMPORTANT_SECTIONS if s in text_lower]
    missing = [s for s in IMPORTANT_SECTIONS if s not in text_lower]
    return found, missing


def check_contact_info(resume_text):
    """Check for contact information"""
    checks = {
        'email': bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text)),
        'phone': bool(re.search(r'[\+]?[\d\s\-\(\)]{10,}', resume_text)),
        'linkedin': 'linkedin' in resume_text.lower(),
        'github': 'github' in resume_text.lower(),
        'portfolio': any(word in resume_text.lower() for word in ['portfolio', 'website', 'blog'])
    }
    return checks


def check_keyword_stuffing(resume_text, skills):
    """Check if skills are naturally integrated or just listed"""
    text_lower = resume_text.lower()

    # Check if skills appear in context (near action verbs) vs just listed
    contextual_skills = 0
    for skill in skills:
        skill_lower = skill.lower()
        # Look for skill near action verbs (within 50 characters)
        for verb in ALL_ACTION_VERBS:
            pattern = f'{verb}.{{0,50}}{re.escape(skill_lower)}|{re.escape(skill_lower)}.{{0,50}}{verb}'
            if re.search(pattern, text_lower):
                contextual_skills += 1
                break

    return contextual_skills, len(skills)


def generate_suggestions(resume_text, analysis_results):
    """
    Generate comprehensive improvement suggestions

    Args:
        resume_text: The extracted resume text
        analysis_results: Dict from analyze_resume()

    Returns:
        list: List of suggestion dictionaries
    """
    suggestions = []

    match_score = analysis_results.get('match_score', 0)
    missing_skills = analysis_results.get('missing_skills', [])
    high_priority_missing = analysis_results.get('high_priority_missing', [])
    matched_skills = analysis_results.get('matched_skills', [])
    missing_categories = analysis_results.get('missing_categories', {})
    jd_experience_level = analysis_results.get('jd_experience_level', 'not specified')
    jd_years_required = analysis_results.get('jd_years_required')
    jd_education = analysis_results.get('jd_education', [])

    # 1. Overall Match Score Feedback
    if match_score >= 80:
        suggestions.append({
            'type': 'success',
            'category': 'Match Score',
            'message': f'Excellent match ({match_score}%)! Your skills align very well with this job. Focus on tailoring your experience descriptions to highlight relevant achievements.'
        })
    elif match_score >= 60:
        suggestions.append({
            'type': 'info',
            'category': 'Match Score',
            'message': f'Good match ({match_score}%)! You have a solid foundation. Adding a few more relevant skills could push your application to the top.'
        })
    elif match_score >= 40:
        suggestions.append({
            'type': 'warning',
            'category': 'Match Score',
            'message': f'Moderate match ({match_score}%). Consider emphasizing transferable skills and any relevant projects or coursework.'
        })
    else:
        suggestions.append({
            'type': 'danger',
            'category': 'Match Score',
            'message': f'Low match ({match_score}%). This role may require skills you haven\'t highlighted. Consider if you have relevant experience that isn\'t reflected in your resume.'
        })

    # 2. High Priority Missing Skills
    if high_priority_missing:
        suggestions.append({
            'type': 'danger',
            'category': 'Critical Skills Gap',
            'message': f'These skills are mentioned multiple times in the job description and are likely essential: {", ".join(high_priority_missing[:5])}'
        })

    # 3. Category-specific missing skills
    if missing_categories.get('programming'):
        suggestions.append({
            'type': 'warning',
            'category': 'Programming Languages',
            'message': f'Missing programming languages: {", ".join(missing_categories["programming"][:4])}. If you have experience with similar languages, highlight your ability to learn quickly.'
        })

    if missing_categories.get('frameworks'):
        suggestions.append({
            'type': 'warning',
            'category': 'Frameworks',
            'message': f'Missing frameworks/libraries: {", ".join(missing_categories["frameworks"][:4])}. Consider adding relevant projects to demonstrate these skills.'
        })

    if missing_categories.get('cloud_devops'):
        suggestions.append({
            'type': 'info',
            'category': 'Cloud/DevOps',
            'message': f'Missing cloud/DevOps skills: {", ".join(missing_categories["cloud_devops"][:4])}. Free tier accounts on AWS/Azure can help you gain hands-on experience.'
        })

    # 4. Experience Level Match
    if jd_experience_level != 'not specified':
        suggestions.append({
            'type': 'info',
            'category': 'Experience Level',
            'message': f'This appears to be a {jd_experience_level}-level position. {"Highlight your growth and quick learning ability." if jd_experience_level == "senior" else "Your enthusiasm and recent projects can compensate for less experience."}'
        })

    if jd_years_required:
        suggestions.append({
            'type': 'info',
            'category': 'Years Required',
            'message': f'The job requires approximately {jd_years_required}+ years of experience. Include all relevant experience including internships, freelance work, and significant personal projects.'
        })

    # 5. Action Verbs Check
    verb_categories, total_verbs = check_action_verbs(resume_text)
    if total_verbs < 5:
        suggestions.append({
            'type': 'warning',
            'category': 'Action Verbs',
            'message': 'Your resume lacks strong action verbs. Start bullet points with words like: Led, Developed, Implemented, Achieved, Optimized, Delivered.'
        })
    elif total_verbs < 10:
        weak_categories = [cat for cat, verbs in verb_categories.items() if not verbs]
        if weak_categories:
            suggestions.append({
                'type': 'info',
                'category': 'Action Verbs',
                'message': f'Consider adding more {", ".join(weak_categories[:2])} action verbs to showcase different aspects of your experience.'
            })

    # 6. Quantifiable Achievements
    metric_count, metrics = check_quantifiable_achievements(resume_text)
    if metric_count == 0:
        suggestions.append({
            'type': 'warning',
            'category': 'Quantifiable Results',
            'message': 'No metrics found! Add numbers to demonstrate impact: "Increased sales by 25%", "Reduced load time by 40%", "Managed team of 5", "Processed 10K+ records daily".'
        })
    elif metric_count < 4:
        suggestions.append({
            'type': 'info',
            'category': 'Quantifiable Results',
            'message': f'Found {metric_count} metrics. Try to add more quantifiable achievements to each role - aim for at least 2-3 per position.'
        })

    # 7. Resume Length
    word_count, _ = check_resume_length(resume_text)
    if word_count < 200:
        suggestions.append({
            'type': 'warning',
            'category': 'Content Length',
            'message': f'Your resume seems too short ({word_count} words). Add more details about your responsibilities, achievements, and projects.'
        })
    elif word_count > 1200:
        suggestions.append({
            'type': 'info',
            'category': 'Content Length',
            'message': f'Your resume is quite long ({word_count} words). For most roles, keep it to 1-2 pages. Prioritize the most relevant information.'
        })

    # 8. Sections Check
    found_sections, missing_sections = check_sections(resume_text)
    critical_missing = [s for s in missing_sections if s in ['experience', 'education', 'skills']]
    if critical_missing:
        suggestions.append({
            'type': 'danger',
            'category': 'Resume Structure',
            'message': f'Missing critical sections: {", ".join(critical_missing).title()}. These are essential for most job applications.'
        })

    # 9. Contact Information
    contact_info = check_contact_info(resume_text)
    if not contact_info['email']:
        suggestions.append({
            'type': 'danger',
            'category': 'Contact Info',
            'message': 'No email address detected! Make sure your contact information is clearly visible at the top of your resume.'
        })
    if not contact_info['linkedin'] and not contact_info['github']:
        suggestions.append({
            'type': 'info',
            'category': 'Online Presence',
            'message': 'Consider adding LinkedIn or GitHub profiles to showcase your professional network and code samples.'
        })

    # 10. Skills in Context
    if matched_skills:
        contextual, total = check_keyword_stuffing(resume_text, matched_skills)
        if total > 0 and contextual / total < 0.3:
            suggestions.append({
                'type': 'info',
                'category': 'Skills Integration',
                'message': 'Your skills appear to be listed but not demonstrated in context. Show how you used each skill in your experience descriptions.'
            })

    # 11. ATS Tips
    suggestions.append({
        'type': 'info',
        'category': 'ATS Optimization',
        'message': 'For ATS compatibility: Use standard section headings, avoid tables/graphics, save as PDF, and include exact keywords from the job description.'
    })

    # 12. Education Match (if specified in JD)
    if 'masters' in jd_education or 'phd' in jd_education:
        resume_edu = analysis_results.get('resume_education', [])
        if 'masters' in jd_education and 'masters' not in resume_edu and 'phd' not in resume_edu:
            suggestions.append({
                'type': 'info',
                'category': 'Education',
                'message': 'This position may prefer advanced degrees. Emphasize relevant coursework, certifications, and hands-on project experience.'
            })

    return suggestions


def get_score_category(score):
    """Get category label and CSS class for match score"""
    if score >= 80:
        return 'Excellent', 'success'
    elif score >= 60:
        return 'Good', 'info'
    elif score >= 40:
        return 'Fair', 'warning'
    else:
        return 'Needs Work', 'danger'
