#!/usr/bin/env python3
"""
运行户型分析脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analysis.layout_analyzer import analyze_layout_statistics, generate_layout_report
from src.utils.data_processor import load_data

def main():
    """主函数"""
    print("开始执行户型分析...")
    try:
        # 加载数据
        df = load_data()
        if df is None:
            print("无法加载数据文件")
            return 1

        # 执行分析
        result = analyze_layout_statistics(df)
        if result:
            main_layouts, layout_stats = result
            print("户型分析完成！")
            print("生成报告...")
            generate_layout_report(main_layouts, layout_stats)
        else:
            print("分析失败")
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())