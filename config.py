# Resume Ranker Configuration

# Application settings
DEBUG = True
SECRET_KEY = 'your-secret-key-here-change-in-production'

# File upload settings
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

# Resume processing settings
MIN_SCORE_THRESHOLD = 0.1
MAX_RESUMES_PER_BATCH = 50

# NLP Settings
SPACY_MODEL = 'en_core_web_sm'
USE_STEMMING = True
USE_LEMMATIZATION = True

# Scoring weights
SKILLS_WEIGHT = 0.4
EXPERIENCE_WEIGHT = 0.3
EDUCATION_WEIGHT = 0.2
KEYWORDS_WEIGHT = 0.1

# Common technical skills for matching
TECHNICAL_SKILLS = [
    'python', 'java', 'javascript', 'c++', 'c#', 'html', 'css', 'sql',
    'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
    'machine learning', 'data science', 'artificial intelligence',
    'aws', 'azure', 'docker', 'kubernetes', 'git', 'linux', 'windows'
]

# Experience level mapping
EXPERIENCE_LEVELS = {
    'entry': 0,
    'junior': 1,
    'mid': 3,
    'senior': 5,
    'lead': 8,
    'principal': 10
}