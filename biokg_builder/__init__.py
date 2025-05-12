"""
BioKG-Builder: AI-driven biomedical literature knowledge graph generator
"""

from .__version__ import __version__
from .core import BioKGBuilder
from .searcher import PubMedSearcher
from .analyzer import CausalAnalyzer
from .processor import EntityProcessor
from .visualizer import NetworkVisualizer
from .generator import ReportGenerator
from .config import Config

__all__ = [
    "BioKGBuilder",
    "PubMedSearcher",
    "CausalAnalyzer", 
    "EntityProcessor",
    "NetworkVisualizer",
    "ReportGenerator",
    "Config",
    "__version__"
]

# Convenience function for quickly building knowledge graphs
def build_knowledge_graph(keyword, email=None, api_key=None, **kwargs):
    """
    Convenience function for quickly building knowledge graphs
    
    Args:
        keyword: Search keyword
        email: PubMed email
        api_key: OpenAI API key
        **kwargs: Other parameters
        
    Returns:
        dict: Dictionary containing results
    """
    builder = BioKGBuilder(email=email, api_key=api_key)
    return builder.build_knowledge_graph(keyword, **kwargs)