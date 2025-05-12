"""Report Generation Module"""

from typing import List, Dict, Any
from openai import OpenAI
from .config import Config
import os
import json
from datetime import datetime


class ReportGenerator:
    """Report Generation Class"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(api_key=config.api_key, base_url=config.base_url)
    
    def generate_summary(self, node_names: List[str], keyword: str) -> str:
        """Generate AI summary of entities"""
        if not node_names:
            return "No relevant nodes found."
        
        # Prepare entity list
        entities_text = ", ".join(node_names[:self.config.chunk_size])
        if len(node_names) > self.config.chunk_size:
            entities_text += "..."
        
        prompt = (
            f"List of biomedical entities related to '{keyword}':\n"
            f"{entities_text}\n\n"
            f"Please categorize these entities and write a brief summary including: "
            f"key findings, entity categories, and research significance."
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.llm_model,
                messages=[
                    {"role": "system", "content": self.config.summary_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Failed to generate summary."
    
    def generate_full_report(self, results: Dict[str, Any], keyword: str) -> str:
        """Generate analysis report"""
        report_content = f"""# {keyword} Knowledge Graph Analysis Report

## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
- Articles retrieved: {results.get('total_articles', 0)}
- Total entities: {results.get('total_entities', 0)}
- Unique entities: {results.get('unique_entities', 0)}

## Network Analysis
- Nodes: {results.get('network_stats', {}).get('node_count', 0)}
- Edges: {results.get('network_stats', {}).get('edge_count', 0)}
- Density: {results.get('network_stats', {}).get('density', 0):.4f}

## Top Entities
"""
        # Add top entities
        for i, (entity, score) in enumerate(results.get('network_stats', {}).get('top_10_nodes_by_degree', [])[:5], 1):
            report_content += f"{i}. {entity} (score: {score:.4f})\n"
        
        report_content += f"\n## AI Summary\n{results.get('ai_summary', 'None')}\n"
        
        # Save report
        output_dir = self.config.output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        report_path = os.path.join(output_dir, f"{self.config.report_pattern.format(keyword=keyword)}.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"Report saved to: {report_path}")
        return report_path
    
    def save_results_json(self, results: Dict[str, Any], keyword: str) -> str:
        """Save results as JSON"""
        output_dir = self.config.output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        json_path = os.path.join(output_dir, self.config.json_results_pattern.format(keyword=keyword))
        
        # Convert to serializable format
        serializable = self._make_serializable(results)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2)
        
        return json_path
    
    def _make_serializable(self, obj: Any) -> Any:
        """Convert object to JSON-serializable format"""
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_serializable(item) for item in obj]
        else:
            return str(obj)