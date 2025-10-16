"""
Flask Web Application for Resume Ranker

This module provides a web interface for uploading resumes and job descriptions,
and displaying ranking results.
"""

import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import sys

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from resume_ranker.parser import ResumeParser, batch_parse_resumes
from resume_ranker.nlp_processor import ResumeAnalyzer
from resume_ranker.ranker import ResumeRanker, create_job_requirement_from_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize components
resume_parser = ResumeParser()
resume_analyzer = ResumeAnalyzer()
resume_ranker = ResumeRanker()


def allowed_file(filename):
    """Check if uploaded file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page with upload forms."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads and process ranking."""
    try:
        # Check if job description is provided
        job_description = request.form.get('job_description', '').strip()
        if not job_description:
            flash('Please provide a job description.', 'error')
            return redirect(url_for('index'))
        
        # Check if files are uploaded
        if 'resume_files' not in request.files:
            flash('Please select resume files to upload.', 'error')
            return redirect(url_for('index'))
        
        files = request.files.getlist('resume_files')
        if not files or all(file.filename == '' for file in files):
            flash('Please select at least one resume file.', 'error')
            return redirect(url_for('index'))
        
        # Process uploaded files
        uploaded_files = []
        for file in files:
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_files.append(filepath)
            else:
                flash(f'File {file.filename} has an unsupported format.', 'warning')
        
        if not uploaded_files:
            flash('No valid files were uploaded.', 'error')
            return redirect(url_for('index'))
        
        # Process resumes and job description
        results = process_ranking(uploaded_files, job_description)
        
        # Clean up uploaded files
        for filepath in uploaded_files:
            try:
                os.remove(filepath)
            except OSError:
                pass
        
        return render_template('results.html', **results)
        
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        flash('An error occurred while processing your request.', 'error')
        return redirect(url_for('index'))


def process_ranking(resume_files, job_description):
    """Process resume ranking and return results."""
    # Create job requirement from description
    job_req = create_job_requirement_from_text(job_description, "Uploaded Job")
    
    # Parse and analyze resumes
    analyzed_resumes = []
    for file_path in resume_files:
        try:
            # Parse resume
            parsed_resume = resume_parser.parse_resume(file_path)
            
            # Analyze resume content
            analysis = resume_analyzer.analyze_resume(parsed_resume['text_content'])
            
            # Combine parsed and analyzed data
            combined_data = {**parsed_resume, **analysis}
            analyzed_resumes.append(combined_data)
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            # Add error entry
            analyzed_resumes.append({
                'file_name': os.path.basename(file_path),
                'error': str(e)
            })
    
    # Rank resumes
    ranked_resumes = resume_ranker.rank_resumes(analyzed_resumes, job_req)
    
    # Prepare results for template
    results = {
        'job_title': job_req.title,
        'job_description': job_req.description[:500] + "..." if len(job_req.description) > 500 else job_req.description,
        'total_resumes': len(ranked_resumes),
        'ranked_resumes': []
    }
    
    for i, (resume_data, scores) in enumerate(ranked_resumes):
        if 'error' in resume_data:
            # Handle error case
            resume_result = {
                'rank': i + 1,
                'file_name': resume_data.get('file_name', 'Unknown'),
                'error': resume_data['error'],
                'overall_score': 0.0
            }
        else:
            # Get explanations for scores
            explanations = resume_ranker.get_ranking_explanation(scores, job_req)
            
            # Get top skills for display
            skills_summary = []
            for category, skills in resume_data.get('skills', {}).items():
                skills_summary.extend(skills[:3])  # Top 3 skills per category
            
            resume_result = {
                'rank': i + 1,
                'file_name': resume_data.get('file_name', 'Unknown'),
                'overall_score': round(scores['overall_score'], 3),
                'skills_score': round(scores['skills_score'], 3),
                'experience_score': round(scores['experience_score'], 3),
                'education_score': round(scores['education_score'], 3),
                'keywords_score': round(scores['keywords_score'], 3),
                'experience_years': resume_data.get('experience_years', 0),
                'education_level': resume_data.get('education_level', 'Unknown'),
                'top_skills': skills_summary[:8],  # Top 8 skills for display
                'explanations': explanations,
                'word_count': resume_data.get('word_count', 0)
            }
        
        results['ranked_resumes'].append(resume_result)
    
    return results


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for resume analysis."""
    try:
        data = request.get_json()
        
        if not data or 'job_description' not in data or 'resume_text' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        job_description = data['job_description']
        resume_text = data['resume_text']
        
        # Create job requirement
        job_req = create_job_requirement_from_text(job_description)
        
        # Analyze resume
        analysis = resume_analyzer.analyze_resume(resume_text)
        
        # Score resume
        scores = resume_ranker.score_resume(analysis, job_req)
        
        # Get explanations
        explanations = resume_ranker.get_ranking_explanation(scores, job_req)
        
        return jsonify({
            'scores': scores,
            'explanations': explanations,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    flash('File is too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)