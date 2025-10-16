"""
NLP Processing Module

This module provides natural language processing capabilities for resume text analysis,
including text preprocessing, keyword extraction, and skill matching.
"""

import re
import logging
from typing import List, Dict, Set, Tuple, Any
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from fuzzywuzzy import fuzz, process

logger = logging.getLogger(__name__)


class TextProcessor:
    """Handles text preprocessing and analysis."""
    
    def __init__(self, use_stemming=True, use_lemmatization=True):
        self.use_stemming = use_stemming
        self.use_lemmatization = use_lemmatization
        
        # Initialize NLTK components
        self._download_nltk_data()
        
        if use_stemming:
            self.stemmer = PorterStemmer()
        if use_lemmatization:
            self.lemmatizer = WordNetLemmatizer()
        
        # Load stopwords
        self.stop_words = set(stopwords.words('english'))
        
        # Technical skills database
        self.technical_skills = {
            'programming_languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c',
                'ruby', 'php', 'swift', 'kotlin', 'scala', 'go', 'rust', 'r',
                'matlab', 'perl', 'objective-c', 'dart', 'cobol', 'fortran'
            ],
            'web_technologies': [
                'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express',
                'django', 'flask', 'spring', 'asp.net', 'laravel', 'rails',
                'jquery', 'bootstrap', 'sass', 'less', 'webpack', 'babel'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'sqlite', 'oracle', 'redis',
                'cassandra', 'dynamodb', 'elasticsearch', 'neo4j', 'couchdb'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean',
                'linode', 'ibm cloud', 'oracle cloud'
            ],
            'tools_frameworks': [
                'docker', 'kubernetes', 'jenkins', 'git', 'svn', 'jira',
                'confluence', 'slack', 'terraform', 'ansible', 'puppet', 'chef'
            ],
            'data_science': [
                'machine learning', 'deep learning', 'artificial intelligence',
                'data science', 'pandas', 'numpy', 'scikit-learn', 'tensorflow',
                'pytorch', 'keras', 'matplotlib', 'seaborn', 'jupyter'
            ]
        }
    
    def _download_nltk_data(self):
        """Download required NLTK data."""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text (str): Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces and periods
        text = re.sub(r'[^\w\s\.]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def extract_keywords(self, text: str, top_k: int = 20) -> List[Tuple[str, float]]:
        """
        Extract important keywords using TF-IDF.
        
        Args:
            text (str): Text to extract keywords from
            top_k (int): Number of top keywords to return
            
        Returns:
            List of (keyword, score) tuples
        """
        if not text:
            return []
        
        # Clean text
        cleaned_text = self.clean_text(text)
        
        # Tokenize and remove stopwords
        tokens = word_tokenize(cleaned_text)
        tokens = [token for token in tokens if token not in self.stop_words and len(token) > 2]
        
        if not tokens:
            return []
        
        # Apply stemming/lemmatization
        processed_tokens = []
        for token in tokens:
            if self.use_stemming:
                token = self.stemmer.stem(token)
            if self.use_lemmatization:
                token = self.lemmatizer.lemmatize(token)
            processed_tokens.append(token)
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=top_k * 2,
            ngram_range=(1, 2),
            stop_words='english'
        )
        
        try:
            # Fit and transform the text
            tfidf_matrix = vectorizer.fit_transform([' '.join(processed_tokens)])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return keyword_scores[:top_k]
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def extract_skills(self, text: str, threshold: int = 80) -> Dict[str, List[str]]:
        """
        Extract technical skills from text using fuzzy matching.
        
        Args:
            text (str): Text to extract skills from
            threshold (int): Fuzzy matching threshold (0-100)
            
        Returns:
            Dict mapping skill categories to found skills
        """
        if not text:
            return {}
        
        text_lower = text.lower()
        found_skills = {}
        
        for category, skills_list in self.technical_skills.items():
            found_skills[category] = []
            
            for skill in skills_list:
                # Direct match
                if skill in text_lower:
                    found_skills[category].append(skill)
                else:
                    # Fuzzy match
                    words = text_lower.split()
                    for word in words:
                        if fuzz.ratio(skill, word) >= threshold:
                            found_skills[category].append(skill)
                            break
        
        # Remove empty categories
        found_skills = {k: v for k, v in found_skills.items() if v}
        
        return found_skills
    
    def extract_experience_years(self, text: str) -> int:
        """
        Extract years of experience from text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            int: Estimated years of experience
        """
        if not text:
            return 0
        
        text_lower = text.lower()
        
        # Patterns for experience
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*in',
            r'experience\s*:?\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:professional\s*)?(?:work\s*)?experience'
        ]
        
        years = []
        for pattern in experience_patterns:
            matches = re.findall(pattern, text_lower)
            years.extend([int(match) for match in matches])
        
        return max(years) if years else 0
    
    def extract_education_level(self, text: str) -> str:
        """
        Extract education level from text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Education level
        """
        if not text:
            return "unknown"
        
        text_lower = text.lower()
        
        education_keywords = {
            'phd': ['phd', 'ph.d', 'doctor of philosophy', 'doctorate'],
            'masters': ['masters', 'master', 'mba', 'ms', 'm.s', 'ma', 'm.a'],
            'bachelors': ['bachelors', 'bachelor', 'bs', 'b.s', 'ba', 'b.a', 'btech', 'be'],
            'associates': ['associates', 'associate', 'aa', 'as'],
            'high_school': ['high school', 'diploma', 'ged']
        }
        
        for level, keywords in education_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return level
        
        return "unknown"
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts.
        
        Args:
            text1 (str): First text
            text2 (str): Second text
            
        Returns:
            float: Similarity score (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0


class ResumeAnalyzer:
    """High-level analyzer for resume content."""
    
    def __init__(self):
        self.text_processor = TextProcessor()
    
    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of resume text.
        
        Args:
            resume_text (str): Resume text content
            
        Returns:
            Dict containing analysis results
        """
        analysis = {
            'keywords': self.text_processor.extract_keywords(resume_text),
            'skills': self.text_processor.extract_skills(resume_text),
            'experience_years': self.text_processor.extract_experience_years(resume_text),
            'education_level': self.text_processor.extract_education_level(resume_text),
            'word_count': len(resume_text.split()) if resume_text else 0,
            'character_count': len(resume_text) if resume_text else 0
        }
        
        # Calculate skill diversity score
        total_skills = sum(len(skills) for skills in analysis['skills'].values())
        skill_categories = len(analysis['skills'])
        analysis['skill_diversity_score'] = skill_categories * 0.3 + total_skills * 0.1
        
        return analysis