"""
Resume Ranking Algorithm

This module implements the core ranking algorithm to score and rank resumes
based on job requirements and various criteria.
"""

import logging
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from .nlp_processor import ResumeAnalyzer, TextProcessor

logger = logging.getLogger(__name__)


class JobRequirement:
    """Represents a job requirement with skills, experience, and other criteria."""
    
    def __init__(self, 
                 title: str,
                 description: str,
                 required_skills: List[str] = None,
                 preferred_skills: List[str] = None,
                 min_experience_years: int = 0,
                 education_level: str = "bachelors",
                 keywords: List[str] = None):
        self.title = title
        self.description = description
        self.required_skills = required_skills or []
        self.preferred_skills = preferred_skills or []
        self.min_experience_years = min_experience_years
        self.education_level = education_level
        self.keywords = keywords or []


class ResumeRanker:
    """Main class for ranking resumes against job requirements."""
    
    def __init__(self, 
                 skills_weight: float = 0.4,
                 experience_weight: float = 0.3,
                 education_weight: float = 0.2,
                 keywords_weight: float = 0.1):
        """
        Initialize the ranker with scoring weights.
        
        Args:
            skills_weight: Weight for skills matching score
            experience_weight: Weight for experience score
            education_weight: Weight for education score
            keywords_weight: Weight for keyword matching score
        """
        self.skills_weight = skills_weight
        self.experience_weight = experience_weight
        self.education_weight = education_weight
        self.keywords_weight = keywords_weight
        
        # Validate weights sum to 1
        total_weight = sum([skills_weight, experience_weight, education_weight, keywords_weight])
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Weights don't sum to 1.0 (sum={total_weight}). Normalizing...")
            self.skills_weight /= total_weight
            self.experience_weight /= total_weight
            self.education_weight /= total_weight
            self.keywords_weight /= total_weight
        
        self.analyzer = ResumeAnalyzer()
        self.text_processor = TextProcessor()
    
    def score_resume(self, resume_analysis: Dict[str, Any], job_req: JobRequirement) -> Dict[str, float]:
        """
        Score a single resume against job requirements.
        
        Args:
            resume_analysis: Analyzed resume data from ResumeAnalyzer
            job_req: Job requirement object
            
        Returns:
            Dict containing detailed scores and overall score
        """
        scores = {}
        
        # Calculate individual component scores
        scores['skills_score'] = self._calculate_skills_score(resume_analysis, job_req)
        scores['experience_score'] = self._calculate_experience_score(resume_analysis, job_req)
        scores['education_score'] = self._calculate_education_score(resume_analysis, job_req)
        scores['keywords_score'] = self._calculate_keywords_score(resume_analysis, job_req)
        
        # Calculate weighted overall score
        scores['overall_score'] = (
            scores['skills_score'] * self.skills_weight +
            scores['experience_score'] * self.experience_weight +
            scores['education_score'] * self.education_weight +
            scores['keywords_score'] * self.keywords_weight
        )
        
        return scores
    
    def _calculate_skills_score(self, resume_analysis: Dict[str, Any], job_req: JobRequirement) -> float:
        """Calculate skills matching score."""
        resume_skills = resume_analysis.get('skills', {})
        
        # Flatten all resume skills
        all_resume_skills = []
        for skill_list in resume_skills.values():
            all_resume_skills.extend([skill.lower() for skill in skill_list])
        
        if not all_resume_skills:
            return 0.0
        
        # Required skills matching
        required_matches = 0
        for skill in job_req.required_skills:
            if skill.lower() in all_resume_skills:
                required_matches += 1
        
        required_score = required_matches / len(job_req.required_skills) if job_req.required_skills else 0
        
        # Preferred skills matching (bonus)
        preferred_matches = 0
        for skill in job_req.preferred_skills:
            if skill.lower() in all_resume_skills:
                preferred_matches += 1
        
        preferred_score = preferred_matches / len(job_req.preferred_skills) if job_req.preferred_skills else 0
        
        # Combine scores (required skills are more important)
        skills_score = required_score * 0.8 + preferred_score * 0.2
        
        return min(skills_score, 1.0)
    
    def _calculate_experience_score(self, resume_analysis: Dict[str, Any], job_req: JobRequirement) -> float:
        """Calculate experience score."""
        resume_years = resume_analysis.get('experience_years', 0)
        required_years = job_req.min_experience_years
        
        if required_years == 0:
            return 1.0  # No experience requirement
        
        if resume_years >= required_years:
            # Bonus for extra experience, but cap at 1.0
            extra_years = resume_years - required_years
            bonus = min(extra_years * 0.1, 0.3)  # Max 30% bonus
            return min(1.0 + bonus, 1.0)
        else:
            # Penalty for insufficient experience
            return resume_years / required_years
    
    def _calculate_education_score(self, resume_analysis: Dict[str, Any], job_req: JobRequirement) -> float:
        """Calculate education score."""
        education_hierarchy = {
            'high_school': 1,
            'associates': 2,
            'bachelors': 3,
            'masters': 4,
            'phd': 5,
            'unknown': 0
        }
        
        resume_education = resume_analysis.get('education_level', 'unknown')
        required_education = job_req.education_level
        
        resume_level = education_hierarchy.get(resume_education, 0)
        required_level = education_hierarchy.get(required_education, 3)
        
        if resume_level >= required_level:
            return 1.0
        elif resume_level == 0:  # Unknown education
            return 0.5  # Neutral score
        else:
            return resume_level / required_level
    
    def _calculate_keywords_score(self, resume_analysis: Dict[str, Any], job_req: JobRequirement) -> float:
        """Calculate keyword matching score using TF-IDF similarity."""
        resume_keywords = [kw[0] for kw in resume_analysis.get('keywords', [])]
        job_keywords = job_req.keywords
        
        if not resume_keywords or not job_keywords:
            return 0.0
        
        # Create text from keywords
        resume_text = ' '.join(resume_keywords)
        job_text = ' '.join(job_keywords)
        
        # Calculate similarity
        similarity = self.text_processor.calculate_text_similarity(resume_text, job_text)
        return similarity
    
    def rank_resumes(self, resumes_data: List[Dict[str, Any]], job_req: JobRequirement) -> List[Tuple[Dict[str, Any], Dict[str, float]]]:
        """
        Rank multiple resumes against job requirements.
        
        Args:
            resumes_data: List of analyzed resume data
            job_req: Job requirement object
            
        Returns:
            List of (resume_data, scores) tuples sorted by overall score (descending)
        """
        scored_resumes = []
        
        for resume_data in resumes_data:
            try:
                scores = self.score_resume(resume_data, job_req)
                scored_resumes.append((resume_data, scores))
            except Exception as e:
                logger.error(f"Error scoring resume: {e}")
                # Add with zero score to maintain data
                zero_scores = {
                    'skills_score': 0.0,
                    'experience_score': 0.0,
                    'education_score': 0.0,
                    'keywords_score': 0.0,
                    'overall_score': 0.0
                }
                scored_resumes.append((resume_data, zero_scores))
        
        # Sort by overall score (descending)
        scored_resumes.sort(key=lambda x: x[1]['overall_score'], reverse=True)
        
        return scored_resumes
    
    def get_ranking_explanation(self, scores: Dict[str, float], job_req: JobRequirement) -> Dict[str, str]:
        """
        Generate human-readable explanation of ranking scores.
        
        Args:
            scores: Scoring results
            job_req: Job requirement object
            
        Returns:
            Dict with explanations for each score component
        """
        explanations = {}
        
        # Skills explanation
        skills_score = scores['skills_score']
        if skills_score >= 0.8:
            explanations['skills'] = "Excellent skills match - meets most requirements"
        elif skills_score >= 0.6:
            explanations['skills'] = "Good skills match - meets some key requirements"
        elif skills_score >= 0.4:
            explanations['skills'] = "Moderate skills match - some relevant skills"
        else:
            explanations['skills'] = "Limited skills match - few matching skills"
        
        # Experience explanation
        exp_score = scores['experience_score']
        if exp_score >= 1.0:
            explanations['experience'] = "Meets or exceeds experience requirements"
        elif exp_score >= 0.7:
            explanations['experience'] = "Good experience level, close to requirements"
        elif exp_score >= 0.5:
            explanations['experience'] = "Some experience, but below requirements"
        else:
            explanations['experience'] = "Limited experience for this role"
        
        # Education explanation
        edu_score = scores['education_score']
        if edu_score >= 1.0:
            explanations['education'] = "Meets education requirements"
        elif edu_score >= 0.7:
            explanations['education'] = "Education level close to requirements"
        else:
            explanations['education'] = "Education level below requirements"
        
        # Keywords explanation
        kw_score = scores['keywords_score']
        if kw_score >= 0.7:
            explanations['keywords'] = "Strong keyword match with job description"
        elif kw_score >= 0.4:
            explanations['keywords'] = "Moderate keyword match"
        else:
            explanations['keywords'] = "Limited keyword match"
        
        # Overall explanation
        overall_score = scores['overall_score']
        if overall_score >= 0.8:
            explanations['overall'] = "Excellent candidate - highly recommended"
        elif overall_score >= 0.6:
            explanations['overall'] = "Good candidate - recommended for consideration"
        elif overall_score >= 0.4:
            explanations['overall'] = "Moderate candidate - may be worth reviewing"
        else:
            explanations['overall'] = "Poor match - not recommended"
        
        return explanations


def create_job_requirement_from_text(job_description: str, title: str = "Job Opening") -> JobRequirement:
    """
    Create a JobRequirement object from a job description text.
    
    Args:
        job_description: Raw job description text
        title: Job title
        
    Returns:
        JobRequirement object
    """
    analyzer = ResumeAnalyzer()
    text_processor = TextProcessor()
    
    # Extract skills from job description
    skills_analysis = text_processor.extract_skills(job_description)
    all_skills = []
    for skill_list in skills_analysis.values():
        all_skills.extend(skill_list)
    
    # Extract keywords
    keywords = [kw[0] for kw in text_processor.extract_keywords(job_description, top_k=15)]
    
    # Estimate experience requirements
    min_experience = text_processor.extract_experience_years(job_description)
    
    # Estimate education requirements
    education_level = text_processor.extract_education_level(job_description)
    
    # Split skills into required (most common) and preferred
    required_skills = all_skills[:len(all_skills)//2] if all_skills else []
    preferred_skills = all_skills[len(all_skills)//2:] if all_skills else []
    
    return JobRequirement(
        title=title,
        description=job_description,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        min_experience_years=min_experience,
        education_level=education_level,
        keywords=keywords
    )