"""Network Visualization Module"""

import re
import os
import pandas as pd
import networkx as nx
from typing import List, Tuple
from pyvis.network import Network
from .config import Config


class NetworkVisualizer:
    """Network Visualization Class"""
    
    def __init__(self, config: Config):
        self.config = config
        self.pattern = r'\(([^,]+),\s*([^\)]+)\)'
    
    def create_full_network(self, df: pd.DataFrame, keyword: str) -> str:
        """Create complete knowledge graph"""
        net = Network(
            height=self.config.network_height,
            width=self.config.network_width,
            bgcolor=self.config.network_bgcolor,
            font_color=self.config.network_font_color
        )
        
        unique_nodes = set()
        edge_count = 0
        
        for _, row in df.iterrows():
            value = str(row.get('Answer to Question 2', ''))
            source = str(row.get('Title', 'Unknown'))
            
            for match in re.findall(self.pattern, value):
                entity_a, entity_b = match[0].strip(), match[1].strip()
                if entity_a and entity_b:
                    net.add_node(entity_a, label=entity_a)
                    net.add_node(entity_b, label=entity_b)
                    net.add_edge(entity_a, entity_b, title=source)
                    unique_nodes.update([entity_a, entity_b])
                    edge_count += 1
        
        net.set_options(self.config.get_network_options())
        
        os.makedirs(self.config.output_dir, exist_ok=True)
        filename = os.path.join(self.config.output_dir, 
                               self.config.full_network_pattern.format(keyword=keyword))
        net.write_html(filename)
        
        print(f"Created full network: {len(unique_nodes)} nodes, {edge_count} edges")
        return filename
    
    def create_filtered_network(self, df: pd.DataFrame, keyword: str, 
                              search_keyword: str, depth: int = 1,
                              exclude_entities: List[str] = None) -> Tuple[str, List[str]]:
        """Create filtered knowledge graph"""
        exclude_entities = exclude_entities or []
        
        # Build NetworkX graph
        G = nx.Graph()
        
        for _, row in df.iterrows():
            value = str(row.get('Answer to Question 2', ''))
            source = str(row.get('Title', 'Unknown'))
            
            for match in re.findall(self.pattern, value):
                entity_a, entity_b = match[0].strip(), match[1].strip()
                
                # Check exclusions
                if (entity_a and entity_b and
                    not any(exc in entity_a for exc in exclude_entities) and 
                    not any(exc in entity_b for exc in exclude_entities)):
                    
                    G.add_node(entity_a, label=entity_a)
                    G.add_node(entity_b, label=entity_b)
                    G.add_edge(entity_a, entity_b, title=source)
        
        # Find related nodes
        filtered_graph = self._search_network(G, search_keyword, depth)
        
        if not filtered_graph.nodes():
            print(f"No nodes found for '{search_keyword}'")
            return "", []
        
        # Create Pyvis network
        net = Network(
            height=self.config.network_height,
            width=self.config.network_width,
            bgcolor=self.config.network_bgcolor,
            font_color=self.config.network_font_color
        )
        net.from_nx(filtered_graph)
        net.set_options(self.config.get_network_options())
        
        os.makedirs(self.config.output_dir, exist_ok=True)
        filename = os.path.join(self.config.output_dir,
                               self.config.filtered_network_pattern.format(
                                   keyword=keyword, search_keyword=search_keyword))
        net.write_html(filename)
        
        node_names = list(filtered_graph.nodes())
        print(f"Created filtered network: {len(node_names)} nodes")
        return filename, node_names
    
    def _search_network(self, graph: nx.Graph, keyword: str, depth: int = 1) -> nx.Graph:
        """Search related nodes in the network"""
        keyword_lower = keyword.lower()
        
        # Find nodes containing the keyword
        nodes_of_interest = {
            n for n, attr in graph.nodes(data=True) 
            if keyword_lower in attr.get('label', '').lower()
        }
        
        if not nodes_of_interest:
            return nx.Graph()
        
        # Expand search to specified depth
        for _ in range(depth):
            new_nodes = set()
            for node in nodes_of_interest:
                if node in graph:
                    new_nodes.update(graph.neighbors(node))
            nodes_of_interest.update(new_nodes)
        
        return graph.subgraph(nodes_of_interest)
    
    def analyze_network_structure(self, df: pd.DataFrame) -> dict:
        """Analyze network structure"""
        G = nx.Graph()
        
        for _, row in df.iterrows():
            value = str(row.get('Answer to Question 2', ''))
            for match in re.findall(self.pattern, value):
                entity_a, entity_b = match[0].strip(), match[1].strip()
                if entity_a and entity_b:
                    G.add_edge(entity_a, entity_b)
        
        if not G.nodes():
            return {"error": "Empty graph"}
        
        # Calculate basic statistics
        degree_centrality = nx.degree_centrality(G)
        top_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "node_count": G.number_of_nodes(),
            "edge_count": G.number_of_edges(),
            "average_degree": sum(dict(G.degree()).values()) / G.number_of_nodes(),
            "density": nx.density(G),
            "connected_components": nx.number_connected_components(G),
            "top_10_nodes_by_degree": top_nodes
        }