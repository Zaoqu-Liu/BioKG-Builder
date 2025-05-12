"""BioKG-Builder Command Line Interface"""

import argparse
import sys
import os
import json
from . import BioKGBuilder, __version__
from .config import Config
from .utils import validate_email, validate_api_key


def main():
    """Main command line function"""
    parser = argparse.ArgumentParser(
        description="BioKG-Builder: AI-driven biomedical knowledge graph generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  biokg-builder build --keyword BRCA1 --email your@email.com --api-key your-key
  biokg-builder build --keyword p53 --config config.json
  biokg-builder config --create --output config.json
  biokg-builder version
        """
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # build command
    build_parser = subparsers.add_parser('build', help='Build knowledge graph')
    build_parser.add_argument('--keyword', '-k', required=True, help='Search keyword')
    build_parser.add_argument('--email', '-e', help='PubMed email address')
    build_parser.add_argument('--api-key', '-a', help='OpenAI API key')
    build_parser.add_argument('--config', '-c', help='Configuration file path')
    build_parser.add_argument('--max-results', '-m', type=int, default=200, help='Maximum search results')
    build_parser.add_argument('--output-dir', '-o', default='output', help='Output directory')
    build_parser.add_argument('--exclude', nargs='+', help='Entities to exclude')
    build_parser.add_argument('--depth', type=int, default=1, help='Network search depth')
    
    # config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('--create', action='store_true', help='Create configuration file')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')
    config_parser.add_argument('--output', '-o', help='Output file path')
    config_parser.add_argument('--input', '-i', help='Input file path')
    
    # version command
    version_parser = subparsers.add_parser('version', help='Show version information')
    
    # search command
    search_parser = subparsers.add_parser('search', help='Search PubMed only')
    search_parser.add_argument('--keyword', '-k', required=True, help='Search keyword')
    search_parser.add_argument('--email', '-e', help='PubMed email address')
    search_parser.add_argument('--max-results', '-m', type=int, default=200, help='Maximum search results')
    search_parser.add_argument('--output', '-o', help='Output file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Process commands
    if args.command == 'version':
        print(f"BioKG-Builder v{__version__}")
        return
    
    elif args.command == 'config':
        handle_config_command(args)
    
    elif args.command == 'build':
        handle_build_command(args)
    
    elif args.command == 'search':
        handle_search_command(args)


def handle_config_command(args):
    """Handle config command"""
    if args.create:
        # Create configuration file
        config = Config()
        
        # Interactive configuration
        print("Creating BioKG-Builder configuration file")
        
        email = input("PubMed email address: ").strip()
        if email and validate_email(email):
            config.email = email
        else:
            print("Warning: Invalid email address")
        
        api_key = input("OpenAI API key: ").strip()
        if api_key and validate_api_key(api_key):
            config.api_key = api_key
        else:
            print("Warning: Invalid API key")
        
        base_url = input(f"API base URL (default: {config.base_url}): ").strip()
        if base_url:
            config.base_url = base_url
        
        max_results = input(f"Maximum search results (default: {config.max_results}): ").strip()
        if max_results.isdigit():
            config.max_results = int(max_results)
        
        output_path = args.output or "config.json"
        config.to_file(output_path)
        print(f"Configuration file saved to: {output_path}")
    
    elif args.show:
        # Show configuration
        config_path = args.input or "config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            print("Current configuration:")
            print(json.dumps(config_data, indent=2, ensure_ascii=False))
        else:
            print(f"Configuration file does not exist: {config_path}")


def handle_build_command(args):
    """Handle build command"""
    # Determine configuration source
    if args.config and os.path.exists(args.config):
        builder = BioKGBuilder(config_path=args.config)
    else:
        # Create from command line arguments
        email = args.email or os.getenv('BIOKG_EMAIL')
        api_key = args.api_key or os.getenv('BIOKG_API_KEY')
        
        if not email or not api_key:
            print("Error: Email and API key required")
            print("Provide via command line arguments, environment variables, or configuration file")
            sys.exit(1)
        
        if not validate_email(email):
            print("Error: Invalid email address")
            sys.exit(1)
        
        if not validate_api_key(api_key):
            print("Error: Invalid API key")
            sys.exit(1)
        
        builder = BioKGBuilder(email=email, api_key=api_key)
    
    # Set output directory
    builder.config.output_dir = args.output_dir
    
    # Build knowledge graph
    print(f"Starting to build knowledge graph for '{args.keyword}'...")
    
    try:
        results = builder.build_knowledge_graph(
            keyword=args.keyword,
            max_results=args.max_results,
            exclude_entities=args.exclude,
            depth=args.depth
        )
        
        print("\nBuild successful!")
        print(f"Summary:")
        print(f"  - Articles: {results.get('statistics', {}).get('total_articles', 0)}")
        print(f"  - Entities: {results.get('statistics', {}).get('total_entities', 0)}")
        print(f"  - Output directory: {args.output_dir}")
        
        # Save result summary
        summary_path = os.path.join(args.output_dir, f"{args.keyword}_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(results.get('statistics', {}), f, indent=2, ensure_ascii=False)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def handle_search_command(args):
    """Handle search command"""
    email = args.email or os.getenv('BIOKG_EMAIL')
    
    if not email:
        print("Error: PubMed email address required")
        sys.exit(1)
    
    if not validate_email(email):
        print("Error: Invalid email address")
        sys.exit(1)
    
    # Create configuration
    config = Config()
    config.email = email
    
    # Create searcher
    from .searcher import PubMedSearcher
    searcher = PubMedSearcher(config)
    
    print(f"Searching for '{args.keyword}' related articles...")
    
    try:
        # Execute search
        id_list = searcher.search_pubmed(args.keyword, args.max_results)
        articles = searcher.fetch_details(id_list)
        
        print(f"Found {len(articles)} articles")
        
        # Save results
        import pandas as pd
        df = pd.DataFrame(articles)
        
        output_path = args.output or f"{args.keyword}_search_results.xlsx"
        df.to_excel(output_path, index=False)
        print(f"Results saved to: {output_path}")
        
        # Show first few articles
        print("\nFirst 5 articles:")
        for i, article in enumerate(articles[:5], 1):
            print(f"\n{i}. {article.get('Title', 'No title')}")
            print(f"   Journal: {article.get('Journal', 'Unknown')}")
            print(f"   Date: {article.get('PubDate', 'Unknown')}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()