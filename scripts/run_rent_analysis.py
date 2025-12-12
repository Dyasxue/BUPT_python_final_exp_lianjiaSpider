#!/usr/bin/env python3
"""
运行租金分析脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analysis.rent_analyzer import analyze_rent_statistics, generate_report
from src.utils.data_processor import load_data

def main():
    """主函数"""
    print("开始执行租金分析...")
    try:
        # 加载数据
        df = load_data()
        if df is None:
            print("无法加载数据文件")
            return 1

        # 执行分析
        result = analyze_rent_statistics(df)
        if result:
            valid_data, rent_stats, sqm_stats = result
            print("租金分析完成！")
            print("生成报告...")
            generate_report(valid_data, rent_stats, sqm_stats)
        else:
            print("分析失败")
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())