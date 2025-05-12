"""Causal Relationship Analysis Module"""

import pandas as pd
import os
from typing import Dict, Any
from openai import OpenAI
from .config import Config
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


class CausalAnalyzer:
    """Causal Relationship Analysis Class"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(api_key=config.api_key, base_url=config.base_url)
        self.lock = threading.Lock()
        self.completed_count = 0
    
    def analyze_abstract(self, abstract: str) -> str:
        """Analyze causal relationships in a single abstract"""
        if not abstract or pd.isna(abstract):
            return ""
        
        messages = [
            {"role": "system", "content": self.config.causal_analysis_prompt},
            {"role": "user", "content": str(abstract)}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.llm_model,
                messages=messages,
                max_tokens=2000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error analyzing abstract: {e}")
            return ""
    
    def analyze_single_row(self, index: int, row: pd.Series, total_rows: int) -> tuple:
        """Analyze a single row"""
        abstract = row['Abstract']
        
        if pd.isna(abstract) or not abstract:
            result = ""
        else:
            result = self.analyze_abstract(abstract)
        
        # Update progress
        with self.lock:
            self.completed_count += 1
            progress = (self.completed_count / total_rows) * 100
            print(f"Row {index+1}/{total_rows}: {result[:50]}..." if result else f"Row {index+1}/{total_rows}: No results")
            print(f"Progress: {progress:.2f}%\n")
        
        return index, result
    
    def batch_analyze(self, df: pd.DataFrame, start_row: int = 0) -> pd.DataFrame:
        """Batch analyze article abstracts with optional parallel processing"""
        if 'Answer to Question 2' not in df.columns:
            df['Answer to Question 2'] = ""
        
        rows_to_process = [(i, row) for i, row in df.iterrows() if i >= start_row]
        total_rows = len(rows_to_process)
        
        if total_rows == 0:
            return df
        
        # Check if parallel processing is enabled
        if self.config.use_parallel:
            return self._batch_analyze_parallel(df, rows_to_process, total_rows)
        else:
            return self._batch_analyze_sequential(df, rows_to_process, total_rows)
    
    def _batch_analyze_parallel(self, df: pd.DataFrame, rows_to_process: list, total_rows: int) -> pd.DataFrame:
        """Parallel batch analysis"""
        self.completed_count = 0
        
        print(f"Analyzing {total_rows} abstracts with {self.config.max_workers} workers (parallel mode)...")
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = {
                executor.submit(self.analyze_single_row, i, row, total_rows): i 
                for i, row in rows_to_process
            }
            
            for future in as_completed(futures):
                try:
                    index, result = future.result()
                    df.at[index, 'Answer to Question 2'] = result
                except Exception as e:
                    index = futures[future]
                    print(f"Error processing row {index+1}: {e}")
                    df.at[index, 'Answer to Question 2'] = ""
        
        return df
    
    def _batch_analyze_sequential(self, df: pd.DataFrame, rows_to_process: list, total_rows: int) -> pd.DataFrame:
        """Sequential batch analysis"""
        print(f"Analyzing {total_rows} abstracts (sequential mode)...")
        
        for i, (index, row) in enumerate(rows_to_process):
            result = self.analyze_abstract(row['Abstract'])
            df.at[index, 'Answer to Question 2'] = result
            
            progress = ((i + 1) / total_rows) * 100
            print(f"Row {index+1}/{total_rows}: {result[:50]}..." if result else f"Row {index+1}/{total_rows}: No results")
            print(f"Progress: {progress:.2f}%\n")
        
        return df
    
    def save_results(self, df: pd.DataFrame, keyword: str, output_dir: str = None) -> str:
        """Save analysis results"""
        output_dir = output_dir or self.config.output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, self.config.causal_results_pattern.format(keyword=keyword))
        df.to_excel(output_file, index=False)
        print(f"Results saved to: {output_file}")
        return output_file
    
    def get_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get analysis statistics"""
        column = 'Answer to Question 2'
        if column not in df.columns:
            return {"error": f"Column '{column}' does not exist"}
        
        total = len(df)
        analyzed = len(df[df[column].notna() & (df[column] != "")])
        
        return {
            "total_articles": total,
            "analyzed_articles": analyzed,
            "empty_results": total - analyzed,
            "success_rate": (analyzed / total * 100) if total > 0 else 0
        }