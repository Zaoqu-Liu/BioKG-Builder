# BioKG-Builder

BioKG-Builder is an AI-driven biomedical literature knowledge graph generator that helps researchers analyze and visualize relationships between biological entities from PubMed literature.

## Features

- **Automated Literature Search**: Search PubMed database for relevant articles
- **AI-Powered Analysis**: Use LLM to identify causal relationships between biological entities
- **Entity Recognition**: Extract and deduplicate biological entities (genes, proteins, diseases, etc.)
- **Knowledge Graph Visualization**: Create interactive network visualizations using Pyvis
- **Intelligent Filtering**: Focus on specific entities of interest
- **Automated Reporting**: Generate comprehensive analysis reports using AI

## Installation

```bash
git clone https://github.com/Zaoqu-Liu/biokg-builder.git
cd biokg-builder
pip install -e .
```

## Quick Start

```python
from biokg_builder import BioKGBuilder

# Initialize BioKGBuilder
builder = BioKGBuilder(
    email="your.email@example.com",        # Replace with your email
    api_key="your-api-key",         # Replace with your LLM API Key
    base_url="https://api.deepseek.com",   # Optional: custom API endpoint
    use_parallel=True                      # Enable parallel processing
)

# Build a knowledge graph for a specific keyword
results = builder.build_knowledge_graph("THBS2")

# View results
print(f"Construction completed with {len(results['entities'])} biological entities found.")
print(f"Generated files: {results['files']}")
```

## Output Files

The tool generates several files:

1. **Excel Files**: 
   - `{keyword}_pubmed_search_results.xlsx`: Raw PubMed search results
   - `modified_updated_{keyword}_causal.xlsx`: Processed causal relationships

2. **HTML Visualizations**:
   - `{keyword}_entity_network.html`: Complete knowledge graph
   - `filtered_entity_{keyword}_network.html`: Filtered subgraph

3. **Reports**: AI-generated summary of findings


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use BioKG-Builder in your research, please cite:

```bibtex
@software{biokg_builder,
  title={BioKG-Builder: AI-driven biomedical literature knowledge graph generator},
  author={Zaoqu Liu},
  year={2025},
  url={https://github.com/Zaoqu-Liu/biokg-builder}
}
```

## Acknowledgments

- BioPython team for PubMed access tools
- OpenAI for language models
- Pyvis developers for network visualization

## Contact

- Author: Zaoqu Liu
- Email: liuzaoqu@163.com
- GitHub: [@Zaoqu-Liu](https://github.com/Zaoqu-Liu)
- Issues: [GitHub Issues](https://github.com/Zaoqu-Liu/biokg-builder/issues)
