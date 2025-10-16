"""
Test suite for Resume Ranker application.
"""

import unittest
import os
import sys
import tempfile

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from resume_ranker.parser import ResumeParser
from resume_ranker.nlp_processor import TextProcessor, ResumeAnalyzer
from resume_ranker.ranker import ResumeRanker, JobRequirement, create_job_requirement_from_text


class TestResumeParser(unittest.TestCase):
    """Test cases for ResumeParser class."""
    
    def setUp(self):
        self.parser = ResumeParser()
        self.test_dir = tempfile.mkdtemp()
    
    def test_validate_file_extension(self):
        """Test file extension validation."""
        # Create temporary test files
        valid_files = ['test.pdf', 'test.docx', 'test.txt']
        invalid_files = ['test.doc', 'test.rtf', 'test.jpg']
        
        for filename in valid_files:
            filepath = os.path.join(self.test_dir, filename)
            with open(filepath, 'w') as f:
                f.write('test content')
            self.assertTrue(self.parser.validate_file(filepath))
        
        for filename in invalid_files:
            filepath = os.path.join(self.test_dir, filename)
            with open(filepath, 'w') as f:
                f.write('test content')
            self.assertFalse(self.parser.validate_file(filepath))
    
    def test_parse_txt_file(self):
        """Test parsing of TXT files."""
        test_content = "John Doe\nSoftware Engineer\nPython, JavaScript, React"
        test_file = os.path.join(self.test_dir, 'test.txt')
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        result = self.parser.parse_resume(test_file)
        
        self.assertEqual(result['text_content'], test_content)
        self.assertEqual(result['file_extension'], '.txt')
        self.assertGreater(result['word_count'], 0)


class TestTextProcessor(unittest.TestCase):
    """Test cases for TextProcessor class."""
    
    def setUp(self):
        self.processor = TextProcessor()
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        dirty_text = "Hello, World! This is a TEST with @special #characters."
        clean_text = self.processor.clean_text(dirty_text)
        
        self.assertNotIn('@', clean_text)
        self.assertNotIn('#', clean_text)
        self.assertEqual(clean_text.lower(), clean_text)
    
    def test_extract_skills(self):
        """Test skill extraction from text."""
        text = "I have experience with Python, JavaScript, React, and AWS cloud services."
        skills = self.processor.extract_skills(text)
        
        self.assertIn('programming_languages', skills)
        self.assertIn('python', skills['programming_languages'])
        self.assertIn('javascript', skills['programming_languages'])
    
    def test_extract_experience_years(self):
        """Test experience extraction."""
        text1 = "I have 5 years of experience in software development."
        text2 = "Working for 3+ years in machine learning."
        text3 = "No experience mentioned here."
        
        self.assertEqual(self.processor.extract_experience_years(text1), 5)
        self.assertEqual(self.processor.extract_experience_years(text2), 3)
        self.assertEqual(self.processor.extract_experience_years(text3), 0)
    
    def test_extract_education_level(self):
        """Test education level extraction."""
        text1 = "I have a Master's degree in Computer Science."
        text2 = "PhD in Machine Learning from MIT."
        text3 = "Bachelor's in Software Engineering."
        text4 = "High school diploma."
        
        self.assertEqual(self.processor.extract_education_level(text1), 'masters')
        self.assertEqual(self.processor.extract_education_level(text2), 'phd')
        self.assertEqual(self.processor.extract_education_level(text3), 'bachelors')
        self.assertEqual(self.processor.extract_education_level(text4), 'high_school')


class TestResumeAnalyzer(unittest.TestCase):
    """Test cases for ResumeAnalyzer class."""
    
    def setUp(self):
        self.analyzer = ResumeAnalyzer()
    
    def test_analyze_resume(self):
        """Test complete resume analysis."""
        resume_text = """
        John Doe
        Senior Software Engineer
        
        I have 7 years of experience in software development using Python, JavaScript, and React.
        I hold a Master's degree in Computer Science and have worked with AWS cloud services.
        """
        
        analysis = self.analyzer.analyze_resume(resume_text)
        
        self.assertIn('keywords', analysis)
        self.assertIn('skills', analysis)
        self.assertIn('experience_years', analysis)
        self.assertIn('education_level', analysis)
        self.assertEqual(analysis['experience_years'], 7)
        self.assertEqual(analysis['education_level'], 'masters')


class TestResumeRanker(unittest.TestCase):
    """Test cases for ResumeRanker class."""
    
    def setUp(self):
        self.ranker = ResumeRanker()
        self.job_req = JobRequirement(
            title="Senior Developer",
            description="Looking for a senior developer with Python and AWS experience.",
            required_skills=['python', 'aws'],
            preferred_skills=['javascript', 'react'],
            min_experience_years=5,
            education_level='bachelors'
        )
    
    def test_score_resume(self):
        """Test resume scoring functionality."""
        resume_analysis = {
            'skills': {
                'programming_languages': ['python', 'javascript'],
                'cloud_platforms': ['aws']
            },
            'experience_years': 7,
            'education_level': 'masters',
            'keywords': [('python', 0.8), ('aws', 0.6)]
        }
        
        scores = self.ranker.score_resume(resume_analysis, self.job_req)
        
        self.assertIn('overall_score', scores)
        self.assertIn('skills_score', scores)
        self.assertIn('experience_score', scores)
        self.assertIn('education_score', scores)
        self.assertGreater(scores['overall_score'], 0)
    
    def test_rank_resumes(self):
        """Test resume ranking functionality."""
        resume1 = {
            'skills': {'programming_languages': ['python', 'javascript']},
            'experience_years': 7,
            'education_level': 'masters',
            'keywords': [('python', 0.8)]
        }
        
        resume2 = {
            'skills': {'programming_languages': ['java']},
            'experience_years': 2,
            'education_level': 'bachelors',
            'keywords': [('java', 0.5)]
        }
        
        ranked = self.ranker.rank_resumes([resume1, resume2], self.job_req)
        
        self.assertEqual(len(ranked), 2)
        # First resume should rank higher
        self.assertGreater(ranked[0][1]['overall_score'], ranked[1][1]['overall_score'])


class TestJobRequirementCreation(unittest.TestCase):
    """Test cases for job requirement creation."""
    
    def test_create_job_requirement_from_text(self):
        """Test creating job requirement from text."""
        job_text = """
        We are looking for a Senior Python Developer with 5+ years of experience.
        Required skills: Python, Django, PostgreSQL, AWS.
        Master's degree preferred.
        """
        
        job_req = create_job_requirement_from_text(job_text, "Senior Python Developer")
        
        self.assertEqual(job_req.title, "Senior Python Developer")
        self.assertEqual(job_req.description, job_text)
        self.assertGreaterEqual(job_req.min_experience_years, 5)


if __name__ == '__main__':
    unittest.main()