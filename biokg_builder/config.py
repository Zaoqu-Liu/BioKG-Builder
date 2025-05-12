"""Configuration Management Module"""

import os
import json
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class Config:
    """Configuration Class"""
    
    # PubMed Configuration
    email: str = field(default_factory=lambda: os.getenv('BIOKG_EMAIL', 'liuzaoqu@163.com'))
    
    # API Configuration
    api_key: str = field(default_factory=lambda: os.getenv('BIOKG_API_KEY', 'sk-94e47466066143a7a63f010653806ec3'))
    base_url: str = field(default_factory=lambda: os.getenv('BIOKG_BASE_URL', 'https://api.deepseek.com'))
    
    # Model Configuration - 确保模型名称正确
    llm_model: str = 'deepseek-chat'  # DeepSeek的正确模型名称
    sentence_model_path: Optional[str] = None  # Optional, will use default if not specified
    
    # Search Configuration
    max_results: int = 200
    
    # Processing Configuration
    similarity_threshold: float = 0.8
    chunk_size: int = 30000
    max_workers: int = 10  # For parallel processing
    use_parallel: bool = True  # Enable/disable parallel processing
    
    # Network Visualization Configuration
    network_height: str = "2160px"
    network_width: str = "100%"
    network_bgcolor: str = "#222222"
    network_font_color: str = "white"
    
    # Output Configuration
    output_dir: str = "output"
    
    # System Prompts
    causal_analysis_prompt: str = (
        "You are specialized for analyzing scientific paper abstracts, "
        "focusing on identifying specific entities related to biological studies, "
        "such as performance, species, genes, methods of genetic engineering, "
        "enzymes, proteins, and bioprocess conditions (e.g., growth conditions), "
        "and determining causal relationships between them. It outputs all possible "
        "combinations of causal relationships among identified entities in structured pairs. "
        "The output strictly follows the format: (Entity A, Entity B), with no additional text."
    )
    
    summary_prompt: str = "You are a professional biomedical research analyst."
    
    # File naming patterns
    search_results_pattern: str = "{keyword}_pubmed_search_results.xlsx"
    causal_results_pattern: str = "updated_{keyword}_causal.xlsx"
    processed_results_pattern: str = "processed_{keyword}.xlsx"
    full_network_pattern: str = "{keyword}_full_network.html"
    filtered_network_pattern: str = "{keyword}_filtered_{search_keyword}_network.html"
    report_pattern: str = "{keyword}_analysis_report"
    json_results_pattern: str = "{keyword}_results.json"
    
    @classmethod
    def from_file(cls, config_path: str) -> 'Config':
        """Load configuration from file"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return cls(**config_data)
    
    def to_file(self, config_path: str) -> None:
        """Save configuration to file"""
        config_data = self.__dict__
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
    
    def get_network_options(self) -> str:
        """Get network visualization options"""
        return f"""
        {{
          "physics": {{
            "barnesHut": {{
              "gravitationalConstant": -80000,
              "centralGravity": 0.5,
              "springLength": 75,
              "springConstant": 0.05,
              "damping": 0.09,
              "avoidOverlap": 0.5
            }},
            "maxVelocity": 100,
            "minVelocity": 0.1,
            "solver": "barnesHut",
            "timestep": 0.3,
            "stabilization": {{
                "enabled": true,
                "iterations": 500,
                "updateInterval": 10,
                "onlyDynamicEdges": false,
                "fit": true
            }}
          }},
          "nodes": {{
            "font": {{
              "size": 30,
              "color": "{self.network_font_color}"
            }}
          }}
        }}
        """