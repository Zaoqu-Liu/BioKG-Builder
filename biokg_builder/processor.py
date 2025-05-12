"""Entity Processing Module"""

import re
import os
import pandas as pd
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer, util
from .config import Config


class EntityProcessor:
    """Entity Processing Class"""
    
    def __init__(self, config: Config):
        self.config = config
        self.pattern = r'\(([^,]+),\s*([^\)]+)\)'
        self.model = None
    
    def _get_model(self):
        """Lazy load sentence embedding model"""
        if self.model is None and self.config.sentence_model_path:
            try:
                self.model = SentenceTransformer(self.config.sentence_model_path)
            except Exception as e:
                print(f"Cannot load model: {e}. Using simple string matching.")
        return self.model
    
    def extract_entities(self, df: pd.DataFrame, column: str = "Answer to Question 2") -> List[str]:
        """Extract all entities from causal relationships"""
        if column not in df.columns:
            return []
        
        entities = set()
        for value in df[column].fillna("").astype(str):
            for match in re.findall(self.pattern, value):
                entities.update([match[0].strip(), match[1].strip()])
        
        entities = [e for e in entities if e]
        print(f"Extracted {len(entities)} unique entities")
        return sorted(entities)
    
    def find_similar_entities(self, entities: List[str]) -> Dict[str, str]:
        """Find similar entities using embeddings or string matching"""
        if not entities:
            return {}
        
        model = self._get_model()
        if model:
            return self._find_similar_with_embeddings(entities, model)
        else:
            return self._find_similar_with_strings(entities)
    
    def _find_similar_with_embeddings(self, entities: List[str], model) -> Dict[str, str]:
        """Find similar entities using sentence embeddings"""
        print(f"Computing similarity for {len(entities)} entities...")
        embeddings = model.encode(entities)
        similar_phrases = {}
        
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                similarity = util.pytorch_cos_sim(embeddings[i], embeddings[j]).item()
                if similarity > self.config.similarity_threshold:
                    # Keep the shorter entity as standard
                    if len(entities[i]) <= len(entities[j]):
                        similar_phrases[entities[j]] = entities[i]
                    else:
                        similar_phrases[entities[i]] = entities[j]
        
        print(f"Found {len(similar_phrases)} similar entity pairs")
        return similar_phrases
    
    def _find_similar_with_strings(self, entities: List[str]) -> Dict[str, str]:
        """Simple string similarity matching"""
        similar_phrases = {}
        
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                if self._is_similar(entities[i], entities[j]):
                    if len(entities[i]) <= len(entities[j]):
                        similar_phrases[entities[j]] = entities[i]
                    else:
                        similar_phrases[entities[i]] = entities[j]
        
        return similar_phrases
    
    def _is_similar(self, s1: str, s2: str) -> bool:
        """Check if two strings are similar"""
        s1_lower, s2_lower = s1.lower(), s2.lower()
        
        # Check substring relationship
        if s1_lower in s2_lower or s2_lower in s1_lower:
            return True
        
        # Check common words
        words1, words2 = set(s1_lower.split()), set(s2_lower.split())
        common = len(words1.intersection(words2))
        total = len(words1.union(words2))
        
        return (common / total) > self.config.similarity_threshold if total > 0 else False
    
    def substitute_similar_entities(self, df: pd.DataFrame, similar_phrases: Dict[str, str],
                                  column: str = "Answer to Question 2") -> pd.DataFrame:
        """Replace similar entities in DataFrame"""
        if not similar_phrases:
            return df
        
        print(f"Replacing {len(similar_phrases)} similar entity pairs...")
        modified_df = df.copy()
        
        for index, row in modified_df.iterrows():
            cell_value = str(row[column])
            for similar, original in similar_phrases.items():
                cell_value = cell_value.replace(similar, original)
            modified_df.at[index, column] = cell_value
        
        print("Replacement completed")
        return modified_df
    
    def process_entities(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], Dict[str, str]]:
        """Complete entity processing workflow"""
        entities = self.extract_entities(df)
        similar_phrases = self.find_similar_entities(entities)
        processed_df = self.substitute_similar_entities(df, similar_phrases)
        final_entities = self.extract_entities(processed_df)
        
        return processed_df, final_entities, similar_phrases
    
    def save_processed_data(self, df: pd.DataFrame, keyword: str, output_dir: str = None) -> str:
        """Save processed data"""
        output_dir = output_dir or self.config.output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, self.config.processed_results_pattern.format(keyword=keyword))
        df.to_excel(output_file, index=False)
        print(f"Saved to: {output_file}")
        return output_file