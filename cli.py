"""
Command Line Interface for Resume Ranker

This script provides a CLI interface for running resume ranking operations.
"""

import os
import sys
import argparse
import json
from typing import List, Dict, Any

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from resume_ranker.parser import ResumeParser, batch_parse_resumes
from resume_ranker.nlp_processor import ResumeAnalyzer
from resume_ranker.ranker import ResumeRanker, create_job_requirement_from_text


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description='AI Resume Ranker CLI')
    parser.add_argument('--resumes-dir', required=True, help='Directory containing resume files')
    parser.add_argument('--job-description', required=True, help='Path to job description file')
    parser.add_argument('--output', '-o', help='Output file for results (JSON format)')
    parser.add_argument('--top-n', type=int, default=10, help='Number of top resumes to show')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.resumes_dir):
        print(f"Error: Resume directory not found: {args.resumes_dir}")
        return 1
    
    if not os.path.exists(args.job_description):
        print(f"Error: Job description file not found: {args.job_description}")
        return 1
    
    # Read job description
    with open(args.job_description, 'r', encoding='utf-8') as f:
        job_text = f.read()
    
    job_title = os.path.splitext(os.path.basename(args.job_description))[0]
    
    if args.verbose:
        print(f"Processing job: {job_title}")
        print(f"Resume directory: {args.resumes_dir}")
    
    # Initialize components
    resume_parser = ResumeParser()
    resume_analyzer = ResumeAnalyzer()
    ranker = ResumeRanker()
    
    # Create job requirement
    job_req = create_job_requirement_from_text(job_text, job_title)
    
    # Parse resumes
    if args.verbose:
        print("Parsing resumes...")
    
    parsed_resumes = batch_parse_resumes(args.resumes_dir)
    
    if not parsed_resumes:
        print("No valid resumes found in directory.")
        return 1
    
    # Analyze resumes
    if args.verbose:
        print(f"Analyzing {len(parsed_resumes)} resumes...")
    
    analyzed_resumes = []
    for filename, resume_data in parsed_resumes.items():
        if 'error' in resume_data:
            print(f"Error parsing {filename}: {resume_data['error']}")
            continue
        
        try:
            analysis = resume_analyzer.analyze_resume(resume_data['text_content'])
            combined_data = {**resume_data, **analysis}
            analyzed_resumes.append(combined_data)
        except Exception as e:
            print(f"Error analyzing {filename}: {e}")
    
    if not analyzed_resumes:
        print("No resumes could be analyzed successfully.")
        return 1
    
    # Rank resumes
    if args.verbose:
        print("Ranking resumes...")
    
    ranked_resumes = ranker.rank_resumes(analyzed_resumes, job_req)
    
    # Prepare results
    results = {
        'job_title': job_req.title,
        'total_resumes_processed': len(analyzed_resumes),
        'rankings': []
    }
    
    # Display results
    print(f"\n{'='*60}")
    print(f"RESUME RANKING RESULTS: {job_title}")
    print(f"{'='*60}")
    print(f"Total resumes processed: {len(analyzed_resumes)}")
    print(f"Top {min(args.top_n, len(ranked_resumes))} candidates:\n")
    
    for i, (resume_data, scores) in enumerate(ranked_resumes[:args.top_n]):
        rank = i + 1
        filename = resume_data.get('file_name', 'Unknown')
        overall_score = scores['overall_score']
        
        print(f"{rank:2d}. {filename}")
        print(f"    Overall Score: {overall_score:.3f} ({overall_score*100:.1f}%)")
        print(f"    Skills: {scores['skills_score']:.3f} | "
              f"Experience: {scores['experience_score']:.3f} | "
              f"Education: {scores['education_score']:.3f} | "
              f"Keywords: {scores['keywords_score']:.3f}")
        
        if args.verbose:
            explanations = ranker.get_ranking_explanation(scores, job_req)
            print(f"    Summary: {explanations['overall']}")
        
        # Add to results
        result_entry = {
            'rank': rank,
            'filename': filename,
            'scores': scores,
            'experience_years': resume_data.get('experience_years', 0),
            'education_level': resume_data.get('education_level', 'unknown'),
            'top_skills': []
        }
        
        # Extract top skills
        for category, skills in resume_data.get('skills', {}).items():
            result_entry['top_skills'].extend(skills[:3])
        
        results['rankings'].append(result_entry)
        print()
    
    # Save results to file if specified
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {args.output}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())