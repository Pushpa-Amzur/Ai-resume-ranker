# AI Resume Ranker - Workflow Explanation

This document provides a detailed explanation of how the AI Resume Ranker system works, from file upload to final ranking results.

## Table of Contents

1. [System Overview](#system-overview)
2. [Data Flow](#data-flow)
3. [Component Workflow](#component-workflow)
4. [Detailed Process Flow](#detailed-process-flow)
5. [Scoring Algorithm](#scoring-algorithm)
6. [Decision Points](#decision-points)
7. [Error Handling](#error-handling)

---

## System Overview

The AI Resume Ranker is a multi-stage pipeline that processes resumes and job descriptions to produce ranked candidate lists. The system uses Natural Language Processing (NLP), machine learning techniques, and custom scoring algorithms.

```
┌─────────────────┐
│  User Input     │
│  - Job Desc     │
│  - Resumes      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  File Parsing   │
│  - PDF/DOCX/TXT │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  NLP Analysis   │
│  - Skills       │
│  - Experience   │
│  - Education    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Scoring &      │
│  Ranking        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Results        │
│  Display        │
└─────────────────┘
```

---

## Data Flow

### 1. Input Stage

**User Inputs:**
- **Job Description**: Text describing the role, requirements, and qualifications
- **Resume Files**: Multiple files in PDF, DOCX, or TXT format

**Processing:**
- Files are validated for format and size (max 16MB)
- Secure filenames are generated to prevent security issues
- Files are temporarily stored in the uploads directory

### 2. Parsing Stage

**Job Description Processing:**
```
Job Description Text
        │
        ▼
┌───────────────────┐
│ Text Extraction   │
│ - Clean text      │
│ - Extract skills  │
│ - Find keywords   │
│ - Detect exp req  │
│ - Find edu level  │
└─────────┬─────────┘
          │
          ▼
    JobRequirement
      Object
```

**Resume Processing:**
```
Resume File (PDF/DOCX/TXT)
        │
        ▼
┌───────────────────┐
│ Format Detection  │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Text Extraction   │
│ - PDF: pdfplumber │
│ - DOCX: python-   │
│   docx            │
│ - TXT: direct read│
└─────────┬─────────┘
          │
          ▼
    Clean Text
```

### 3. Analysis Stage

**NLP Processing Pipeline:**

```
Resume Text
    │
    ▼
┌─────────────────────────┐
│ Text Preprocessing      │
│ - Lowercase conversion  │
│ - Special char removal  │
│ - Whitespace cleanup    │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Tokenization            │
│ - Word tokenization     │
│ - Sentence tokenization │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Stop Word Removal       │
│ - Remove common words   │
│ - Keep technical terms  │
└──────────┬──────────────┘
           │
           ├────────────────────────┬────────────────────┬──────────────────┐
           │                        │                    │                  │
           ▼                        ▼                    ▼                  ▼
┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐  ┌──────────────┐
│ Skill Extraction │  │ Experience       │  │ Education       │  │ Keyword      │
│ - Pattern match  │  │ Extraction       │  │ Detection       │  │ Extraction   │
│ - Fuzzy match    │  │ - Regex patterns │  │ - Level mapping │  │ - TF-IDF     │
│ - Category map   │  │ - Year counting  │  │ - Hierarchy     │  │ - Top terms  │
└──────────────────┘  └──────────────────┘  └─────────────────┘  └──────────────┘
           │                        │                    │                  │
           └────────────────────────┴────────────────────┴──────────────────┘
                                    │
                                    ▼
                            Resume Analysis
                               Object
```

### 4. Scoring Stage

**Multi-Dimensional Scoring:**

```
Resume Analysis + Job Requirements
            │
            ▼
    ┌───────────────┐
    │ Score Resume  │
    └───────┬───────┘
            │
            ├──────────────────┬──────────────────┬──────────────────┬──────────────────┐
            │                  │                  │                  │                  │
            ▼                  ▼                  ▼                  ▼                  ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Skills Score │  │ Experience   │  │ Education    │  │ Keywords     │  │ Overall      │
    │ (40% weight) │  │ Score        │  │ Score        │  │ Score        │  │ Score        │
    │              │  │ (30% weight) │  │ (20% weight) │  │ (10% weight) │  │ (weighted    │
    │ - Required   │  │              │  │              │  │              │  │  average)    │
    │ - Preferred  │  │ - Min years  │  │ - Level      │  │ - Similarity │  │              │
    └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

### 5. Ranking Stage

```
Multiple Scored Resumes
        │
        ▼
┌───────────────────┐
│ Sort by Overall   │
│ Score (Descending)│
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Assign Ranks      │
│ - Rank 1, 2, 3... │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Generate          │
│ Explanations      │
└─────────┬─────────┘
          │
          ▼
    Ranked Results
```

---

## Component Workflow

### ResumeParser Component

**Purpose**: Extract text content from various file formats

**Workflow:**
1. **Input Validation**
   - Check file exists
   - Validate file extension (.pdf, .docx, .txt)
   - Check file size (max 16MB)

2. **Format-Specific Parsing**
   - **PDF Files**:
     - Primary: pdfplumber (better for complex layouts)
     - Fallback: PyPDF2 (if pdfplumber fails)
     - Extract text from all pages
   - **DOCX Files**:
     - Extract paragraph text
     - Extract table content
     - Combine all text sections
   - **TXT Files**:
     - Direct file read with UTF-8 encoding
     - Fallback to Latin-1 if UTF-8 fails

3. **Output Generation**
   ```python
   {
       'file_path': 'path/to/resume.pdf',
       'file_name': 'resume.pdf',
       'file_extension': '.pdf',
       'text_content': 'extracted text...',
       'word_count': 450,
       'character_count': 2500
   }
   ```

### TextProcessor Component

**Purpose**: Clean and preprocess text data

**Workflow:**
1. **Text Cleaning**
   ```
   Raw Text → Lowercase → Remove Special Chars → Clean Whitespace → Clean Text
   ```

2. **Tokenization**
   - Sentence tokenization using NLTK punkt
   - Word tokenization for individual terms
   - Stop word filtering

3. **Feature Extraction**
   - **Skills**: Pattern matching + fuzzy matching against skill database
   - **Experience**: Regex patterns for "X years of experience"
   - **Education**: Keyword matching for degree levels
   - **Keywords**: TF-IDF vectorization for top terms

### ResumeAnalyzer Component

**Purpose**: High-level analysis orchestrator

**Workflow:**
```python
def analyze_resume(resume_text):
    # 1. Extract keywords using TF-IDF
    keywords = extract_keywords(resume_text, top_k=20)
    
    # 2. Identify technical skills
    skills = extract_skills(resume_text)
    # Returns: {
    #   'programming_languages': ['python', 'java'],
    #   'web_technologies': ['react', 'node.js'],
    #   'databases': ['postgresql', 'mongodb']
    # }
    
    # 3. Parse experience
    experience_years = extract_experience_years(resume_text)
    
    # 4. Detect education level
    education_level = extract_education_level(resume_text)
    # Returns: 'bachelors', 'masters', 'phd', etc.
    
    # 5. Calculate metrics
    skill_diversity = calculate_skill_diversity(skills)
    
    return analysis_object
```

### ResumeRanker Component

**Purpose**: Score and rank resumes against job requirements

**Workflow:**

1. **Job Requirement Creation**
   ```python
   job_req = create_job_requirement_from_text(job_description)
   # Extracts:
   # - Required skills
   # - Preferred skills
   # - Minimum experience
   # - Education level
   # - Important keywords
   ```

2. **Individual Resume Scoring**
   ```python
   for each resume:
       skills_score = calculate_skills_match()
       experience_score = calculate_experience_match()
       education_score = calculate_education_match()
       keywords_score = calculate_keyword_similarity()
       
       overall_score = (
           skills_score * 0.4 +
           experience_score * 0.3 +
           education_score * 0.2 +
           keywords_score * 0.1
       )
   ```

3. **Ranking**
   ```python
   # Sort all resumes by overall_score (descending)
   ranked_resumes = sorted(scored_resumes, 
                          key=lambda x: x['overall_score'], 
                          reverse=True)
   
   # Assign ranks
   for i, resume in enumerate(ranked_resumes):
       resume['rank'] = i + 1
   ```

---

## Detailed Process Flow

### Web Application Flow

```
1. User Access
   └─> GET / → Render index.html (upload form)

2. File Upload
   └─> POST /upload
       ├─> Validate job description (required)
       ├─> Validate resume files (format, size)
       ├─> Save files temporarily
       └─> Process ranking
           ├─> Parse each resume
           ├─> Analyze resume content
           ├─> Create job requirement from description
           ├─> Score each resume
           ├─> Rank resumes
           ├─> Generate explanations
           └─> Clean up temporary files

3. Display Results
   └─> Render results.html
       ├─> Show job summary
       ├─> Display ranked resumes
       ├─> Show score breakdowns
       ├─> Display skills and analysis
       └─> Provide export option

4. Export Results
   └─> JavaScript function generates CSV
       └─> Download to user's computer
```

### Command Line Interface Flow

```
1. Parse Arguments
   └─> --resumes-dir, --job-description, --output, --top-n, --verbose

2. Validate Inputs
   ├─> Check resume directory exists
   └─> Check job description file exists

3. Read Job Description
   └─> Load text from file

4. Batch Parse Resumes
   └─> Parse all files in directory
       ├─> Skip invalid files
       └─> Log errors

5. Analyze Resumes
   └─> Process each parsed resume
       └─> Extract features

6. Rank Resumes
   └─> Score and sort

7. Output Results
   ├─> Print to console
   └─> Save to JSON file (if --output specified)
```

---

## Scoring Algorithm

### Skills Score Calculation

```python
def calculate_skills_score(resume_skills, job_requirements):
    # Flatten resume skills
    all_resume_skills = flatten_skills(resume_skills)
    
    # Required skills matching (80% of score)
    required_matches = count_matches(all_resume_skills, 
                                     job_requirements.required_skills)
    required_score = required_matches / len(job_requirements.required_skills)
    
    # Preferred skills matching (20% of score)
    preferred_matches = count_matches(all_resume_skills,
                                      job_requirements.preferred_skills)
    preferred_score = preferred_matches / len(job_requirements.preferred_skills)
    
    # Combined score
    skills_score = (required_score * 0.8) + (preferred_score * 0.2)
    
    return min(skills_score, 1.0)
```

**Example:**
- Job requires: ['python', 'sql', 'aws']
- Job prefers: ['docker', 'kubernetes']
- Resume has: ['python', 'sql', 'docker']

```
Required matches: 2/3 = 0.67
Preferred matches: 1/2 = 0.50
Skills score: (0.67 * 0.8) + (0.50 * 0.2) = 0.536 + 0.10 = 0.636
```

### Experience Score Calculation

```python
def calculate_experience_score(resume_years, required_years):
    if required_years == 0:
        return 1.0  # No requirement
    
    if resume_years >= required_years:
        # Bonus for extra experience (max 30% bonus)
        extra_years = resume_years - required_years
        bonus = min(extra_years * 0.1, 0.3)
        return min(1.0 + bonus, 1.0)
    else:
        # Proportional penalty
        return resume_years / required_years
```

**Example:**
- Job requires: 5 years
- Candidate has: 7 years

```
extra_years = 7 - 5 = 2
bonus = min(2 * 0.1, 0.3) = 0.2
score = min(1.0 + 0.2, 1.0) = 1.0
```

### Education Score Calculation

```python
education_hierarchy = {
    'high_school': 1,
    'associates': 2,
    'bachelors': 3,
    'masters': 4,
    'phd': 5
}

def calculate_education_score(resume_education, required_education):
    resume_level = education_hierarchy[resume_education]
    required_level = education_hierarchy[required_education]
    
    if resume_level >= required_level:
        return 1.0  # Meets or exceeds requirement
    else:
        return resume_level / required_level  # Proportional
```

### Keywords Score Calculation

```python
def calculate_keywords_score(resume_keywords, job_keywords):
    # Create text from keywords
    resume_text = ' '.join([kw[0] for kw in resume_keywords])
    job_text = ' '.join(job_keywords)
    
    # TF-IDF vectorization
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_text])
    
    # Cosine similarity
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    return similarity
```

### Overall Score Calculation

```python
overall_score = (
    skills_score * 0.4 +        # 40% weight
    experience_score * 0.3 +    # 30% weight
    education_score * 0.2 +     # 20% weight
    keywords_score * 0.1        # 10% weight
)
```

---

## Decision Points

### File Format Selection

```
Is file extension supported?
├─ YES: Continue
└─ NO: Reject file

Is file size < 16MB?
├─ YES: Continue
└─ NO: Reject file

File extension = .pdf?
├─ YES: Try pdfplumber → PyPDF2 fallback
├─ NO: File extension = .docx?
│       ├─ YES: Use python-docx
│       └─ NO: File extension = .txt?
│               ├─ YES: Direct read
│               └─ NO: Reject
```

### Skill Matching Strategy

```
For each skill in skill_database:
    Is skill exactly in resume text?
    ├─ YES: Add to found_skills
    └─ NO: Try fuzzy matching
            Fuzzy match score >= 80?
            ├─ YES: Add to found_skills
            └─ NO: Skip
```

### Experience Year Extraction

```
Search for patterns:
1. "X years of experience"
2. "X years in"
3. "Experience: X years"
4. "X+ years experience"

Found multiple matches?
├─ YES: Return maximum value
└─ NO: Return single value or 0
```

### Score Interpretation

```
Overall Score >= 0.8?
├─ YES: "Excellent candidate - highly recommended"
└─ NO: Overall Score >= 0.6?
        ├─ YES: "Good candidate - recommended for consideration"
        └─ NO: Overall Score >= 0.4?
                ├─ YES: "Moderate candidate - may be worth reviewing"
                └─ NO: "Poor match - not recommended"
```

---

## Error Handling

### File Parsing Errors

```python
try:
    parsed_resume = parse_resume(file_path)
except FileNotFoundError:
    log_error("File not found")
    return {'error': 'File not found'}
except ValueError as e:
    log_error(f"Invalid format: {e}")
    return {'error': 'Unsupported file format'}
except Exception as e:
    log_error(f"Parsing error: {e}")
    return {'error': 'Failed to parse resume'}
```

### Analysis Errors

```python
try:
    analysis = analyze_resume(text)
except Exception as e:
    log_error(f"Analysis failed: {e}")
    # Return default/empty analysis
    return {
        'keywords': [],
        'skills': {},
        'experience_years': 0,
        'education_level': 'unknown'
    }
```

### Scoring Errors

```python
try:
    scores = score_resume(resume_data, job_req)
except Exception as e:
    log_error(f"Scoring error: {e}")
    # Return zero scores
    return {
        'skills_score': 0.0,
        'experience_score': 0.0,
        'education_score': 0.0,
        'keywords_score': 0.0,
        'overall_score': 0.0
    }
```

### Web Application Error Flow

```
Upload Error?
├─> Flash error message to user
└─> Redirect to index page

Processing Error?
├─> Log error details
├─> Continue with remaining resumes
└─> Mark resume with error in results

Display Error?
├─> Show error message on results page
└─> Provide option to retry
```

---

## Performance Considerations

### Optimization Strategies

1. **Batch Processing**
   - Process multiple resumes concurrently
   - Use multiprocessing for CPU-intensive tasks

2. **Caching**
   - Cache parsed resumes for repeated analysis
   - Store job requirement objects for multiple runs

3. **Lazy Loading**
   - Load NLTK data only when needed
   - Initialize models on first use

4. **Memory Management**
   - Clean up temporary files immediately
   - Limit batch size (max 50 resumes)
   - Stream large files instead of loading entirely

### Scalability

```
Small Scale (< 10 resumes):
└─> Synchronous processing (current implementation)

Medium Scale (10-100 resumes):
└─> Add multiprocessing for parsing and analysis

Large Scale (100+ resumes):
└─> Consider:
    ├─> Background job queue (Celery)
    ├─> Database for storing results
    └─> Distributed processing
```

---

## Example Complete Workflow

**Scenario**: Ranking 3 resumes for a Senior ML Engineer position

```
Step 1: Job Description Input
─────────────────────────────
Text: "Senior ML Engineer with 5+ years experience.
       Required: Python, TensorFlow, AWS.
       Preferred: Docker, Kubernetes.
       Master's degree required."

Step 2: Job Requirement Extraction
─────────────────────────────────
JobRequirement {
    title: "Senior ML Engineer"
    required_skills: ['python', 'tensorflow', 'aws']
    preferred_skills: ['docker', 'kubernetes']
    min_experience_years: 5
    education_level: 'masters'
    keywords: ['machine', 'learning', 'engineer', 'tensorflow', ...]
}

Step 3: Resume Parsing
────────────────────────
Resume 1: sarah_johnson_data_scientist.txt
    ├─> Extracted 450 words
    └─> Parse successful

Resume 2: john_doe_senior_engineer.txt
    ├─> Extracted 520 words
    └─> Parse successful

Resume 3: michael_chen_fullstack.txt
    ├─> Extracted 380 words
    └─> Parse successful

Step 4: Resume Analysis
─────────────────────────
Resume 1 Analysis:
    skills: {
        'programming_languages': ['python', 'r', 'sql'],
        'machine_learning': ['tensorflow', 'pytorch', 'sklearn'],
        'cloud_platforms': ['aws', 'gcp']
    }
    experience_years: 5
    education_level: 'masters'
    keywords: [('machine', 0.85), ('learning', 0.82), ...]

Resume 2 Analysis:
    skills: {
        'programming_languages': ['python', 'javascript', 'java'],
        'machine_learning': ['tensorflow', 'pytorch'],
        'cloud_platforms': ['aws', 'azure']
    }
    experience_years: 8
    education_level: 'masters'
    keywords: [('software', 0.78), ('engineer', 0.75), ...]

Resume 3 Analysis:
    skills: {
        'programming_languages': ['javascript', 'python'],
        'web_technologies': ['react', 'node.js']
    }
    experience_years: 3
    education_level: 'bachelors'
    keywords: [('web', 0.65), ('developer', 0.60), ...]

Step 5: Scoring
─────────────────
Resume 1 Scores:
    skills_score: 0.90 (has python, tensorflow, aws + docker)
    experience_score: 1.00 (5 years = required 5 years)
    education_score: 1.00 (masters = required masters)
    keywords_score: 0.75 (good ML keyword match)
    overall_score: 0.92

Resume 2 Scores:
    skills_score: 0.80 (has python, tensorflow, aws, docker)
    experience_score: 1.00 (8 years > 5 years)
    education_score: 1.00 (masters = required masters)
    keywords_score: 0.65 (moderate ML keyword match)
    overall_score: 0.86

Resume 3 Scores:
    skills_score: 0.40 (has python only)
    experience_score: 0.60 (3 years < 5 years)
    education_score: 0.75 (bachelors < masters)
    keywords_score: 0.25 (low ML keyword match)
    overall_score: 0.48

Step 6: Ranking
─────────────────
Rank 1: sarah_johnson_data_scientist.txt (92%)
Rank 2: john_doe_senior_engineer.txt (86%)
Rank 3: michael_chen_fullstack.txt (48%)

Step 7: Display Results
─────────────────────────
Show ranked list with:
- Individual scores and breakdowns
- Skill matches
- Experience and education levels
- Explanations for each score
- Export option
```

---

## Integration Points

### Web Application Integration

```python
# Flask route
@app.route('/upload', methods=['POST'])
def upload_files():
    # 1. Receive files and job description
    # 2. Call processing pipeline
    results = process_ranking(resume_files, job_description)
    # 3. Render results template
    return render_template('results.html', **results)
```

### API Integration

```python
# RESTful API endpoint
@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.get_json()
    # Process and return JSON response
    return jsonify({
        'scores': {...},
        'explanations': {...}
    })
```

### CLI Integration

```bash
# Command line usage
python cli.py \
    --resumes-dir ./resumes \
    --job-description job.txt \
    --output results.json \
    --top-n 10
```

---

## Future Enhancements

1. **Machine Learning Improvements**
   - Train custom NER models for skill extraction
   - Use BERT for semantic similarity
   - Implement active learning for score refinement

2. **Feature Additions**
   - Support for more file formats (RTF, ODT)
   - Cover letter analysis
   - LinkedIn profile integration
   - Automated candidate communication

3. **Performance Optimization**
   - Implement caching layer (Redis)
   - Add asynchronous processing (Celery)
   - Database integration for result persistence

4. **User Experience**
   - Real-time progress updates
   - Interactive score adjustments
   - Collaborative ranking features
   - Mobile application

---

## Troubleshooting Guide

### Common Issues

**Issue**: PDF parsing fails
- **Solution**: Try PyPDF2 fallback, check if PDF is text-based (not scanned image)

**Issue**: Skills not detected
- **Solution**: Check skill database coverage, adjust fuzzy matching threshold

**Issue**: Incorrect experience years
- **Solution**: Verify regex patterns match resume format

**Issue**: Low keyword scores
- **Solution**: Ensure job description is detailed with relevant terms

---

## Conclusion

The AI Resume Ranker provides a comprehensive, automated solution for resume screening and ranking. By combining multiple NLP techniques, customizable scoring algorithms, and user-friendly interfaces, it streamlines the candidate evaluation process while maintaining flexibility and transparency.

For more information, refer to:
- [README.md](README.md) - Project overview and setup
- [Source Code](src/) - Implementation details
- [Tests](tests/) - Usage examples and validation
