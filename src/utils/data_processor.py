"""
数据处理工具模块
"""

import pandas as pd
import os
from pathlib import Path
from typing import Optional, Tuple

def load_data(data_dir: str = 'data') -> Optional[pd.DataFrame]:
    """
    加载数据文件

    Args:
        data_dir: 数据目录路径

    Returns:
        加载的数据框，如果失败则返回None
    """
    data_path = Path(data_dir)
    csv_files = list(data_path.glob('*.csv'))

    if not csv_files:
        print(f"在 {data_dir} 目录中没有找到数据文件")
        return None

    # 选择最新的数据文件
    latest_file = max(csv_files, key=os.path.getmtime)
    print(f"加载数据文件: {latest_file}")

    try:
        df = pd.read_csv(latest_file, encoding='utf-8-sig')
        print(f"成功加载 {len(df)} 条记录")
        return df
    except Exception as e:
        print(f"加载数据失败: {e}")
        return None

def save_data(df: pd.DataFrame, filename: str, output_dir: str = 'data') -> str:
    """
    保存数据到CSV文件

    Args:
        df: 要保存的数据框
        filename: 文件名
        output_dir: 输出目录

    Returns:
        保存的文件路径
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    try:
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"数据已保存到: {filepath} (共{len(df)}条记录)")
        return filepath
    except Exception as e:
        print(f"保存数据失败: {e}")
        raise

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    清理数据，移除无效记录

    Args:
        df: 原始数据框

    Returns:
        清理后的数据框
    """
    if df is None or df.empty:
        return df

    # 移除完全重复的记录
    df_cleaned = df.drop_duplicates()

    # 移除关键字段为空的记录
    df_cleaned = df_cleaned.dropna(subset=['price', 'area'])

    # 过滤无效数据
    df_cleaned = df_cleaned[
        (df_cleaned['price'] > 0) &
        (df_cleaned['area'] > 0)
    ]

    print(f"数据清理完成: {len(df)} -> {len(df_cleaned)} 条记录")
    return df_cleaned

def get_data_info(df: pd.DataFrame) -> dict:
    """
    获取数据基本信息

    Args:
        df: 数据框

    Returns:
        数据信息字典
    """
    if df is None or df.empty:
        return {}

    info = {
        'total_records': len(df),
        'columns': list(df.columns),
        'price_stats': {
            'mean': df['price'].mean(),
            'median': df['price'].median(),
            'min': df['price'].min(),
            'max': df['price'].max()
        },
        'area_stats': {
            'mean': df['area'].mean(),
            'median': df['area'].median(),
            'min': df['area'].min(),
            'max': df['area'].max()
        }
    }

    return info