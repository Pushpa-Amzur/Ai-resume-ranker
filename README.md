# AI Resume Ranker

An intelligent resume ranking system that uses natural language processing and machine learning to automatically score and rank resumes based on job requirements.

## Features

- **Smart Resume Parsing**: Supports PDF, DOCX, and TXT formats
- **AI-Powered Analysis**: Uses NLP to extract skills, experience, education, and keywords
- **Multi-Dimensional Scoring**: Evaluates candidates based on skills match, experience level, education, and keyword relevance
- **Web Interface**: User-friendly Flask web application for easy upload and results viewing
- **Command Line Interface**: Batch processing capabilities for large-scale resume analysis
- **Detailed Explanations**: Provides human-readable explanations for ranking decisions
- **Export Results**: Download ranking results in CSV format

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone or download this repository:
```bash
git clone <repository-url>
cd "ai resume ranker"
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download required NLTK data:
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

5. (Optional) Download spaCy model for enhanced NLP:
```bash
python -m spacy download en_core_web_sm
```

### Running the Web Application

1. Start the Flask development server:
```bash
cd web
python app.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. Upload a job description and resume files to get started!

### Using the Command Line Interface

```bash
python cli.py --resumes-dir "data/sample_resumes" --job-description "data/job_descriptions/senior_ml_engineer.txt" --output results.json --top-n 5 --verbose
```

## Project Structure

```
ai resume ranker/
│
├── src/resume_ranker/          # Core library modules
│   ├── __init__.py
│   ├── parser.py               # Resume file parsing
│   ├── nlp_processor.py        # NLP and text analysis
│   └── ranker.py               # Ranking algorithm
│
├── web/                        # Flask web application
│   ├── app.py                  # Main Flask app
│   ├── templates/              # HTML templates
│   │   ├── index.html          # Upload page
│   │   └── results.html        # Results display
│   └── static/                 # CSS, JS, images
│
├── data/                       # Sample data
│   ├── sample_resumes/         # Example resume files
│   └── job_descriptions/       # Example job descriptions
│
├── tests/                      # Unit tests
│   └── test_resume_ranker.py
│
├── requirements.txt            # Python dependencies
├── config.py                   # Configuration settings
├── cli.py                      # Command line interface
└── README.md                   # This file
```

## How It Works

### 1. Resume Parsing
The system supports multiple file formats and extracts clean text content:
- **PDF**: Uses pdfplumber and PyPDF2 for robust text extraction
- **DOCX**: Extracts text from Word documents including tables
- **TXT**: Direct text file processing

### 2. NLP Processing
Advanced natural language processing analyzes resume content:
- **Text Cleaning**: Removes special characters and normalizes text
- **Skill Extraction**: Identifies technical skills using predefined databases and fuzzy matching
- **Experience Extraction**: Parses years of experience using regex patterns
- **Education Detection**: Identifies education levels (High School, Bachelor's, Master's, PhD)
- **Keyword Analysis**: Extracts important keywords using TF-IDF

### 3. Scoring Algorithm
Multi-dimensional scoring system evaluates candidates:

- **Skills Score (40%)**: Matches required and preferred skills
- **Experience Score (30%)**: Compares years of experience to requirements
- **Education Score (20%)**: Evaluates education level against requirements
- **Keywords Score (10%)**: Measures similarity to job description keywords

### 4. Ranking and Explanation
Resumes are ranked by overall score with detailed explanations:
- Individual component scores and explanations
- Overall recommendation (Excellent, Good, Moderate, Poor)
- Skill diversity and keyword match analysis

## API Documentation

### Web API Endpoints

#### POST /upload
Upload resumes and job description for analysis.

**Parameters:**
- `job_description` (form field): Job description text
- `resume_files` (files): Multiple resume files

**Response:** HTML results page with rankings

#### POST /api/analyze
Programmatic API for resume analysis.

**Request Body:**
```json
{
  "job_description": "Job description text...",
  "resume_text": "Resume content text..."
}
```

**Response:**
```json
{
  "scores": {
    "overall_score": 0.75,
    "skills_score": 0.8,
    "experience_score": 0.7,
    "education_score": 0.9,
    "keywords_score": 0.6
  },
  "explanations": {
    "overall": "Good candidate - recommended for consideration",
    "skills": "Good skills match - meets some key requirements",
    "experience": "Good experience level, close to requirements",
    "education": "Meets education requirements"
  },
  "analysis": {
    "skills": {...},
    "experience_years": 5,
    "education_level": "masters",
    "keywords": [...]
  }
}
```

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Configuration

Modify `config.py` to customize scoring weights and behavior:

```python
# Scoring weights (must sum to 1.0)
SKILLS_WEIGHT = 0.4
EXPERIENCE_WEIGHT = 0.3
EDUCATION_WEIGHT = 0.2
KEYWORDS_WEIGHT = 0.1

# File upload settings
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

# Processing settings
MIN_SCORE_THRESHOLD = 0.1
MAX_RESUMES_PER_BATCH = 50
```

## Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Or run individual test files:

```bash
python -m unittest tests.test_resume_ranker -v
```

## Examples

### Sample Job Description
```
Senior Machine Learning Engineer

We are seeking a skilled ML Engineer with 5+ years of experience.
Required skills: Python, TensorFlow, AWS, SQL
Preferred skills: Docker, Kubernetes, MLOps
Master's degree in Computer Science or related field required.
```

### Expected Output
```
RESUME RANKING RESULTS: Senior ML Engineer
============================================================
Total resumes processed: 3

 1. sarah_johnson_data_scientist.txt
    Overall Score: 0.842 (84.2%)
    Skills: 0.900 | Experience: 0.800 | Education: 1.000 | Keywords: 0.750

 2. john_doe_senior_engineer.txt
    Overall Score: 0.756 (75.6%)
    Skills: 0.750 | Experience: 1.000 | Education: 1.000 | Keywords: 0.650

 3. michael_chen_fullstack.txt
    Overall Score: 0.423 (42.3%)
    Skills: 0.400 | Experience: 0.600 | Education: 0.800 | Keywords: 0.200
```

## Deployment

### Production Deployment

1. **Environment Setup**:
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
```

2. **Web Server**: Use Gunicorn for production:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 web.app:app
```

3. **Docker Deployment**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "web/app.py"]
```

### Cloud Deployment Options

- **AWS**: Deploy using Elastic Beanstalk or ECS
- **Google Cloud**: Use App Engine or Cloud Run
- **Azure**: Deploy with App Service or Container Instances
- **Heroku**: Simple deployment with git push

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support:
- Create an issue in the repository
- Check the documentation and examples
- Review the test cases for usage patterns

## Roadmap

- [ ] Support for more file formats (RTF, ODT)
- [ ] Integration with ATS systems
- [ ] Advanced ML models for better skill extraction
- [ ] Multi-language support
- [ ] Real-time collaborative ranking
- [ ] Integration with job boards APIs
- [ ] Advanced analytics and reporting
- [ ] Mobile-responsive design improvements#   A i - r e s u m e - r a n k e r  
 