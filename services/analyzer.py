import re

# Skill synonyms/aliases mapping
SKILL_ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "node": "node.js",
    "nodejs": "node.js",
    "react.js": "react",
    "reactjs": "react",
    "vue.js": "vue",
    "vuejs": "vue",
    "angular.js": "angular",
    "angularjs": "angular",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "k8s": "kubernetes",
    "ml": "machine learning",
    "dl": "deep learning",
    "ai": "artificial intelligence",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "aws": "amazon web services",
    "gcp": "google cloud platform",
    "ci/cd": "ci/cd",
    "cicd": "ci/cd",
    "dotnet": ".net",
    "csharp": "c#",
    "cpp": "c++",
    "golang": "go",
    "tf": "terraform",
    "ui": "ui/ux",
    "ux": "ui/ux",
}

# Predefined skills database organized by category
PROGRAMMING_LANGUAGES = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "ruby", "php", "swift", "kotlin", "scala", "r programming", "matlab",
    "perl", "bash", "shell scripting", "powershell", "objective-c", "dart"
]

FRAMEWORKS_LIBRARIES = [
    "react", "angular", "vue", "node.js", "express", "django", "flask",
    "fastapi", "spring", "spring boot", ".net", "rails", "laravel",
    "next.js", "nuxt.js", "svelte", "jquery", "bootstrap", "tailwind",
    "material ui", "redux", "mobx", "graphql", "rest api"
]

DATABASES = [
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "oracle", "sqlite", "neo4j", "firebase",
    "snowflake", "bigquery", "couchdb", "mariadb"
]

CLOUD_DEVOPS = [
    "aws", "amazon web services", "azure", "gcp", "google cloud platform",
    "docker", "kubernetes", "jenkins", "terraform", "ansible", "ci/cd",
    "github actions", "gitlab ci", "circleci", "nginx", "apache",
    "linux", "unix", "devops", "microservices", "serverless"
]

DATA_AI_ML = [
    "machine learning", "deep learning", "artificial intelligence",
    "data analysis", "data science", "pandas", "numpy", "tensorflow",
    "pytorch", "keras", "scikit-learn", "natural language processing",
    "computer vision", "opencv", "hadoop", "spark", "airflow",
    "power bi", "tableau", "excel", "data visualization", "statistics"
]

TOOLS_PLATFORMS = [
    "git", "github", "gitlab", "bitbucket", "jira", "confluence",
    "slack", "figma", "adobe xd", "photoshop", "illustrator",
    "vs code", "intellij", "postman", "swagger", "jupyter"
]

SOFT_SKILLS = [
    "communication", "teamwork", "leadership", "problem solving",
    "time management", "critical thinking", "adaptability", "creativity",
    "collaboration", "attention to detail", "project management",
    "analytical skills", "interpersonal skills", "decision making",
    "conflict resolution", "presentation skills", "negotiation",
    "customer service", "mentoring", "strategic thinking",
    "public speaking", "technical writing", "research", "agile", "scrum"
]

ALL_SKILLS = (PROGRAMMING_LANGUAGES + FRAMEWORKS_LIBRARIES + DATABASES +
              CLOUD_DEVOPS + DATA_AI_ML + TOOLS_PLATFORMS + SOFT_SKILLS)

# Experience level keywords
EXPERIENCE_LEVELS = {
    'entry': ['entry level', 'junior', 'associate', 'intern', 'internship',
              'fresher', 'graduate', '0-1 years', '0-2 years', 'beginner'],
    'mid': ['mid level', 'mid-level', 'intermediate', '2-4 years', '3-5 years',
            '2+ years', '3+ years', '4+ years'],
    'senior': ['senior', 'lead', 'principal', 'staff', 'architect',
               '5+ years', '6+ years', '7+ years', '8+ years', '10+ years',
               'expert', 'advanced']
}

# Education keywords
EDUCATION_KEYWORDS = {
    'phd': ['phd', 'ph.d', 'doctorate', 'doctoral'],
    'masters': ['master', 'ms', 'm.s', 'msc', 'm.sc', 'mba', 'ma', 'm.a'],
    'bachelors': ['bachelor', 'bs', 'b.s', 'bsc', 'b.sc', 'ba', 'b.a', 'btech', 'b.tech', 'be', 'b.e'],
    'degree': ['degree', 'graduate', 'graduated', 'university', 'college']
}


def preprocess_text(text):
    """Preprocess text for skill extraction"""
    text = text.lower()
    text = re.sub(r'[/\\|,;:\-\(\)\[\]\{\}]', ' ', text)
    text = re.sub(r'[^\w\s\.\+\#]', ' ', text)
    text = ' '.join(text.split())
    return text


def normalize_skill(skill):
    """Normalize skill name using aliases"""
    skill_lower = skill.lower().strip()
    return SKILL_ALIASES.get(skill_lower, skill_lower)


def extract_skills(text, skill_list=None):
    """Extract skills from text using keyword matching with alias support"""
    if skill_list is None:
        skill_list = ALL_SKILLS

    text_processed = preprocess_text(text)
    found_skills = set()

    # Check for aliases in the text and map them
    words = text_processed.split()
    for word in words:
        normalized = normalize_skill(word)
        if normalized != word:
            text_processed = text_processed + ' ' + normalized

    for skill in skill_list:
        skill_lower = skill.lower()
        escaped_skill = re.escape(skill_lower)
        pattern = r'(?:^|[\s,;:\-\(\)\[\]])' + escaped_skill + r'(?:$|[\s,;:\-\(\)\[\]])'

        if re.search(pattern, ' ' + text_processed + ' '):
            found_skills.add(skill)

    return list(found_skills)


def get_skill_frequency(text, skills):
    """Count how many times each skill appears in the text"""
    text_processed = preprocess_text(text)
    frequency = {}

    for skill in skills:
        skill_lower = skill.lower()
        escaped_skill = re.escape(skill_lower)
        pattern = r'(?:^|[\s,;:\-\(\)\[\]])' + escaped_skill + r'(?:$|[\s,;:\-\(\)\[\]])'
        matches = re.findall(pattern, ' ' + text_processed + ' ')
        if matches:
            frequency[skill] = len(matches)

    return frequency


def detect_experience_level(text):
    """Detect required experience level from job description"""
    text_lower = text.lower()
    detected = []

    for level, keywords in EXPERIENCE_LEVELS.items():
        for keyword in keywords:
            if keyword in text_lower:
                detected.append(level)
                break

    if not detected:
        return 'not specified'
    elif 'senior' in detected:
        return 'senior'
    elif 'mid' in detected:
        return 'mid'
    else:
        return 'entry'


def extract_years_experience(text):
    """Extract years of experience requirement from text"""
    text_lower = text.lower()
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)?',
        r'(?:minimum|at least|min)\s*(\d+)\s*(?:years?|yrs?)',
        r'(\d+)\s*-\s*\d+\s*(?:years?|yrs?)',
    ]

    years = []
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        years.extend([int(m) for m in matches if m])

    return min(years) if years else None


def detect_education_requirement(text):
    """Detect education requirements from job description"""
    text_lower = text.lower()
    detected = []

    for level, keywords in EDUCATION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                detected.append(level)
                break

    return detected


def categorize_skills(skills):
    """Categorize skills into different categories"""
    categories = {
        'programming': [],
        'frameworks': [],
        'databases': [],
        'cloud_devops': [],
        'data_ai': [],
        'tools': [],
        'soft_skills': []
    }

    for skill in skills:
        skill_lower = skill.lower()
        if skill_lower in [s.lower() for s in PROGRAMMING_LANGUAGES]:
            categories['programming'].append(skill)
        elif skill_lower in [s.lower() for s in FRAMEWORKS_LIBRARIES]:
            categories['frameworks'].append(skill)
        elif skill_lower in [s.lower() for s in DATABASES]:
            categories['databases'].append(skill)
        elif skill_lower in [s.lower() for s in CLOUD_DEVOPS]:
            categories['cloud_devops'].append(skill)
        elif skill_lower in [s.lower() for s in DATA_AI_ML]:
            categories['data_ai'].append(skill)
        elif skill_lower in [s.lower() for s in TOOLS_PLATFORMS]:
            categories['tools'].append(skill)
        elif skill_lower in [s.lower() for s in SOFT_SKILLS]:
            categories['soft_skills'].append(skill)

    return categories


def calculate_match(resume_skills, jd_skills):
    """Calculate match score between resume and job description skills"""
    if not jd_skills:
        return 0.0, [], [], resume_skills

    resume_skills_set = set([s.lower() for s in resume_skills])
    jd_skills_set = set([s.lower() for s in jd_skills])

    matched = resume_skills_set & jd_skills_set
    missing = jd_skills_set - resume_skills_set
    extra = resume_skills_set - jd_skills_set

    score = (len(matched) / len(jd_skills_set)) * 100

    def get_original_case(skill_lower):
        for s in ALL_SKILLS:
            if s.lower() == skill_lower:
                return s
        return skill_lower

    matched_original = [get_original_case(s) for s in matched]
    missing_original = [get_original_case(s) for s in missing]
    extra_original = [get_original_case(s) for s in extra]

    return round(score, 1), matched_original, missing_original, extra_original


def analyze_resume(resume_text, job_description):
    """
    Comprehensive resume analysis

    Returns:
        dict: Analysis results including score, skills, and metadata
    """
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)

    score, matched, missing, extra = calculate_match(resume_skills, jd_skills)

    # Get skill frequency for JD to find high-priority skills
    jd_skill_freq = get_skill_frequency(job_description, jd_skills)

    # Categorize skills
    matched_categories = categorize_skills(matched)
    missing_categories = categorize_skills(missing)

    # Detect experience level and education from JD
    jd_experience_level = detect_experience_level(job_description)
    jd_years_required = extract_years_experience(job_description)
    jd_education = detect_education_requirement(job_description)

    # Detect from resume
    resume_experience_level = detect_experience_level(resume_text)
    resume_education = detect_education_requirement(resume_text)

    # Find high-priority missing skills (mentioned multiple times in JD)
    high_priority_missing = [
        skill for skill in missing
        if jd_skill_freq.get(skill, 0) >= 2
    ]

    return {
        'match_score': score,
        'matched_skills': sorted(matched),
        'missing_skills': sorted(missing),
        'extra_skills': sorted(extra),
        'high_priority_missing': sorted(high_priority_missing),
        'matched_categories': matched_categories,
        'missing_categories': missing_categories,
        'resume_skill_count': len(resume_skills),
        'jd_skill_count': len(jd_skills),
        'jd_experience_level': jd_experience_level,
        'jd_years_required': jd_years_required,
        'jd_education': jd_education,
        'resume_experience_level': resume_experience_level,
        'resume_education': resume_education
    }
