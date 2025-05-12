"""BioKG-Builder Core Module"""

import os
from typing import Dict, Any, List, Optional
from .config import Config
from .searcher import PubMedSearcher
from .analyzer import CausalAnalyzer
from .processor import EntityProcessor
from .visualizer import NetworkVisualizer
from .generator import ReportGenerator


class BioKGBuilder:
    """BioKG Builder Main Class"""
    
    def __init__(self, email: str = None, api_key: str = None, 
                 base_url: str = None, config_path: str = None, 
                 use_parallel: bool = None):
        """
        Initialize BioKG Builder
        
        Args:
            email: PubMed email
            api_key: API key
            base_url: API base URL
            config_path: Configuration file path
            use_parallel: Enable/disable parallel processing
        """
        # Load or create configuration
        if config_path and os.path.exists(config_path):
            self.config = Config.from_file(config_path)
        else:
            self.config = Config()
        
        # Override with provided parameters
        if email:
            self.config.email = email
        if api_key:
            self.config.api_key = api_key
        if base_url:
            self.config.base_url = base_url
        if use_parallel is not None:
            self.config.use_parallel = use_parallel
        
        # Initialize components
        self.searcher = PubMedSearcher(self.config)
        self.analyzer = CausalAnalyzer(self.config)
        self.processor = EntityProcessor(self.config)
        self.visualizer = NetworkVisualizer(self.config)
        self.generator = ReportGenerator(self.config)
    
    def build_knowledge_graph(self, keyword: str, max_results: int = None,
                            exclude_entities: List[str] = None,
                            depth: int = 1, use_parallel: bool = None) -> Dict[str, Any]:
        """
        Build knowledge graph from PubMed literature
        
        Args:
            keyword: Search keyword
            max_results: Maximum search results
            exclude_entities: Entities to exclude
            depth: Network search depth
            use_parallel: Override parallel processing setting
        """
        print(f"\n=== Building knowledge graph for '{keyword}' ===\n")
        
        # Override parallel setting if specified
        if use_parallel is not None:
            original_parallel = self.config.use_parallel
            self.config.use_parallel = use_parallel
        
        results = {'keyword': keyword, 'files': {}, 'statistics': {}}
        
        try:
            # 1. Search PubMed
            print("Step 1: Searching PubMed...")
            df, search_file = self.searcher.search_and_save(keyword, max_results)
            results['files']['search_results'] = search_file
            results['statistics']['total_articles'] = len(df)
            
            if df.empty:
                print("No articles found")
                return results
            
            # 2. Analyze causal relationships
            print("\nStep 2: Analyzing causal relationships...")
            df = self.analyzer.batch_analyze(df)
            causal_file = self.analyzer.save_results(df, keyword)
            results['files']['causal_analysis'] = causal_file
            
            # 3. Process entities
            print("\nStep 3: Processing entities...")
            processed_df, entities, similar_phrases = self.processor.process_entities(df)
            processed_file = self.processor.save_processed_data(processed_df, keyword)
            results['files']['processed_data'] = processed_file
            
            results['entities'] = entities
            results['statistics']['total_entities'] = len(entities)
            results['statistics']['unique_entities'] = len(entities) - len(similar_phrases)
            
            # 4. Create visualizations
            print("\nStep 4: Creating visualizations...")
            full_network_file = self.visualizer.create_full_network(processed_df, keyword)
            results['files']['full_network'] = full_network_file
            
            filtered_network_file, node_names = self.visualizer.create_filtered_network(
                processed_df, keyword, keyword, depth, exclude_entities
            )
            results['files']['filtered_network'] = filtered_network_file
            results['node_names'] = node_names
            
            # Analyze network structure
            network_stats = self.visualizer.analyze_network_structure(processed_df)
            results['statistics']['network_stats'] = network_stats
            
            # 5. Generate report
            print("\nStep 5: Generating report...")
            ai_summary = self.generator.generate_summary(node_names, keyword)
            results['ai_summary'] = ai_summary
            
            report_data = {
                'total_articles': len(df),
                'total_entities': len(entities),
                'unique_entities': len(entities) - len(similar_phrases),
                'network_stats': network_stats,
                'ai_summary': ai_summary
            }
            
            report_file = self.generator.generate_full_report(report_data, keyword)
            results['files']['report'] = report_file
            
            json_file = self.generator.save_results_json(results, keyword)
            results['files']['json_results'] = json_file
            
            print(f"\n=== Completed: '{keyword}' ===")
            for file_type, file_path in results['files'].items():
                print(f"  {file_type}: {file_path}")
            
            return results
            
        except Exception as e:
            print(f"\nError: {e}")
            results['error'] = str(e)
            return results
        
        finally:
            # Restore original parallel setting if it was overridden
            if use_parallel is not None:
                self.config.use_parallel = original_parallel