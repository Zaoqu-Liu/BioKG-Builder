"""PubMed Literature Search Module"""

from typing import List, Dict, Any
import pandas as pd
from Bio import Entrez
from .config import Config


class PubMedSearcher:
    """PubMed Literature Search Class"""
    
    def __init__(self, config: Config):
        """
        Initialize searcher
        
        Args:
            config: Configuration object
        """
        self.config = config
        Entrez.email = config.email
    
    def search_pubmed(self, keyword: str, max_results: int = None) -> List[str]:
        """
        Search PubMed database
        
        Args:
            keyword: Search keyword
            max_results: Maximum number of results
            
        Returns:
            List[str]: List of PubMed IDs
        """
        if max_results is None:
            max_results = self.config.max_results
            
        search_term = f"{keyword}[Abstract]"
        
        with Entrez.esearch(db="pubmed", term=search_term, retmax=max_results) as handle:
            record = Entrez.read(handle)
        
        return record["IdList"]
    
    def fetch_details(self, id_list: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch article details
        
        Args:
            id_list: List of PubMed IDs
            
        Returns:
            List[Dict]: List of article information
        """
        if not id_list:
            return []
            
        ids = ','.join(id_list)
        
        with Entrez.efetch(db="pubmed", id=ids, retmode="xml") as handle:
            records = Entrez.read(handle)
        
        articles = []
        for pubmed_article in records.get('PubmedArticle', []):
            article = {}
            article_data = pubmed_article['MedlineCitation']['Article']
            
            # Extract title
            article['Title'] = article_data.get('ArticleTitle', '')
            
            # Extract abstract
            abstract_text = article_data.get('Abstract', {}).get('AbstractText', [])
            if isinstance(abstract_text, list):
                abstract_text = ' '.join(str(text) for text in abstract_text)
            article['Abstract'] = abstract_text
            
            # Extract journal
            article['Journal'] = article_data.get('Journal', {}).get('Title', '')
            
            # Extract author information
            authors = []
            author_list = article_data.get('AuthorList', [])
            for author in author_list:
                last_name = author.get('LastName', '')
                fore_name = author.get('ForeName', '')
                if last_name or fore_name:
                    authors.append(f"{fore_name} {last_name}".strip())
            article['Authors'] = '; '.join(authors)
            
            # Extract publication date
            pub_date = article_data.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})
            year = pub_date.get('Year', '')
            month = pub_date.get('Month', '')
            article['PubDate'] = f"{year}-{month}" if month else year
            
            # Extract PMID
            article['PMID'] = pubmed_article['MedlineCitation'].get('PMID', '')
            
            articles.append(article)
        
        return articles
    
    def search_and_save(self, keyword: str, output_dir: str = None) -> tuple:
        """
        Search and save results to Excel
        
        Args:
            keyword: Search keyword
            output_dir: Output directory
            
        Returns:
            tuple: (DataFrame, file path)
        """
        if output_dir is None:
            output_dir = self.config.output_dir
            
        # Search literature
        id_list = self.search_pubmed(keyword)
        
        if not id_list:
            print(f"No articles found for '{keyword}'")
            return pd.DataFrame(), None
            
        # Get detailed information
        articles = self.fetch_details(id_list)
        
        # Convert to DataFrame
        df = pd.DataFrame(articles)
        
        # Save to Excel
        import os
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"{keyword}_pubmed_search_results.xlsx")
        df.to_excel(filename, index=False)
        
        print(f"Found {len(articles)} articles, saved to {filename}")
        return df, filename