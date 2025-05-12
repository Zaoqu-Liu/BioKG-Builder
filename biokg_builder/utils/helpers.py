"""辅助工具函数"""

import os
import re
import pandas as pd
from typing import List, Dict, Any, Optional


def validate_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
        
    Returns:
        bool: 是否有效
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_api_key(api_key: str) -> bool:
    """
    验证API密钥格式
    
    Args:
        api_key: API密钥
        
    Returns:
        bool: 是否有效
    """
    # 基本验证：检查是否为空或太短
    if not api_key or len(api_key) < 20:
        return False
    
    # 检查是否包含非法字符
    if not api_key.replace('-', '').replace('_', '').isalnum():
        return False
    
    return True


def create_output_directory(base_dir: str, keyword: str) -> str:
    """
    创建输出目录
    
    Args:
        base_dir: 基础目录
        keyword: 关键词
        
    Returns:
        str: 创建的目录路径
    """
    # 清理关键词，移除特殊字符
    clean_keyword = re.sub(r'[^\w\s-]', '', keyword).strip()
    clean_keyword = re.sub(r'[-\s]+', '-', clean_keyword)
    
    # 创建目录
    output_dir = os.path.join(base_dir, clean_keyword)
    os.makedirs(output_dir, exist_ok=True)
    
    return output_dir


def clean_text(text: str) -> str:
    """
    清理文本，移除多余的空白和特殊字符
    
    Args:
        text: 原始文本
        
    Returns:
        str: 清理后的文本
    """
    if not text:
        return ""
    
    # 移除多余的空白
    text = ' '.join(text.split())
    
    # 移除控制字符
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    return text.strip()


def merge_dataframes(df_list: List[pd.DataFrame], 
                    on: Optional[str] = None, 
                    how: str = 'outer') -> pd.DataFrame:
    """
    合并多个DataFrame
    
    Args:
        df_list: DataFrame列表
        on: 合并键
        how: 合并方式
        
    Returns:
        pd.DataFrame: 合并后的DataFrame
    """
    if not df_list:
        return pd.DataFrame()
    
    if len(df_list) == 1:
        return df_list[0]
    
    result = df_list[0]
    for df in df_list[1:]:
        if on:
            result = pd.merge(result, df, on=on, how=how)
        else:
            result = pd.concat([result, df], ignore_index=True)
    
    return result


def export_to_formats(df: pd.DataFrame, base_filename: str, 
                     formats: List[str] = None) -> Dict[str, str]:
    """
    将DataFrame导出为多种格式
    
    Args:
        df: 要导出的DataFrame
        base_filename: 基础文件名(不含扩展名)
        formats: 要导出的格式列表
        
    Returns:
        Dict[str, str]: {格式: 文件路径}字典
    """
    if formats is None:
        formats = ['excel', 'csv', 'json']
    
    exported_files = {}
    
    for fmt in formats:
        try:
            if fmt == 'excel':
                filepath = f"{base_filename}.xlsx"
                df.to_excel(filepath, index=False)
            elif fmt == 'csv':
                filepath = f"{base_filename}.csv"
                df.to_csv(filepath, index=False, encoding='utf-8')
            elif fmt == 'json':
                filepath = f"{base_filename}.json"
                df.to_json(filepath, orient='records', indent=2, force_ascii=False)
            elif fmt == 'html':
                filepath = f"{base_filename}.html"
                df.to_html(filepath, index=False)
            else:
                continue
            
            exported_files[fmt] = filepath
            print(f"导出 {fmt} 格式到: {filepath}")
            
        except Exception as e:
            print(f"导出 {fmt} 格式失败: {e}")
    
    return exported_files


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    计算两个文本的相似度（简单版本）
    
    Args:
        text1: 第一个文本
        text2: 第二个文本
        
    Returns:
        float: 相似度分数(0-1)
    """
    if not text1 or not text2:
        return 0.0
    
    # 转换为小写并分词
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    # 计算Jaccard相似度
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)


def format_time_elapsed(seconds: float) -> str:
    """
    格式化经过的时间
    
    Args:
        seconds: 秒数
        
    Returns:
        str: 格式化的时间字符串
    """
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断文本到指定长度
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 后缀
        
    Returns:
        str: 截断后的文本
    """
    if len(text) <= max_length:
        return text
    
    # 在单词边界截断
    truncated = text[:max_length - len(suffix)]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + suffix