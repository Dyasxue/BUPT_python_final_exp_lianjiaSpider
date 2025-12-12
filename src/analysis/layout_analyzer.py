"""
北京租房市场户型分析脚本
分析一居、二居、三居房源的情况
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
from pathlib import Path
from ..utils.data_processor import load_data, clean_data

# 忽略警告信息
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")

def analyze_layout_statistics(df):
    """分析不同户型的统计信息"""
    if df is None or df.empty:
        return None

    print("\n" + "="*60)
    print("北京租房市场户型分析")
    print("="*60)

    # 过滤有效数据
    valid_data = df.dropna(subset=['price', 'area', 'bedrooms'])
    valid_data = valid_data[(valid_data['price'] > 0) & (valid_data['area'] > 0) & (valid_data['bedrooms'] > 0)]

    if valid_data.empty:
        print("没有有效的户型数据")
        return None

    # 计算单位面积租金
    valid_data['price_per_sqm'] = valid_data['price'] / valid_data['area']

    # 过滤主要户型（1-3居）
    main_layouts = valid_data[valid_data['bedrooms'].isin([1, 2, 3])].copy()

    if main_layouts.empty:
        print("没有1-3居室的房源数据")
        return None

    # 按户型分组统计
    layout_stats = {}
    for bedrooms in [1, 2, 3]:
        layout_data = main_layouts[main_layouts['bedrooms'] == bedrooms]
        if len(layout_data) > 0:
            layout_stats[f'{bedrooms}居'] = {
                '均价': layout_data['price'].mean(),
                '最高价': layout_data['price'].max(),
                '最低价': layout_data['price'].min(),
                '中位数': layout_data['price'].median(),
                '标准差': layout_data['price'].std(),
                '样本数': len(layout_data),
                '均面积': layout_data['area'].mean(),
                '均单位面积租金': layout_data['price_per_sqm'].mean(),
                '面积标准差': layout_data['area'].std(),
                '价格分位数': {
                    '25%': layout_data['price'].quantile(0.25),
                    '75%': layout_data['price'].quantile(0.75)
                }
            }

    return main_layouts, layout_stats

def print_layout_statistics(layout_stats):
    """打印户型统计信息"""
    print("\n各户型租金统计 (元/月):")
    print("-" * 80)

    for layout_name, stats in layout_stats.items():
        print(f"\n{layout_name}房源:")
        print(f"  - 均价: ¥{stats['均价']:.0f}")
        print(f"  - 最高价: ¥{stats['最高价']:.0f}")
        print(f"  - 最低价: ¥{stats['最低价']:.0f}")
        print(f"  - 中位数: ¥{stats['中位数']:.0f}")
        print(f"  - 标准差: ¥{stats['标准差']:.0f}")
        print(f"  - 样本数: {stats['样本数']} 套")
        print(f"  - 均面积: {stats['均面积']:.1f} ㎡")
        print(f"  - 均单位面积租金: ¥{stats['均单位面积租金']:.1f}/㎡")
        print(f"  - 面积标准差: {stats['面积标准差']:.2f} ㎡")

def create_layout_visualizations(df, layout_stats):
    """创建户型分析可视化图表"""
    # 创建图表目录
    charts_dir = Path('reports/charts')
    charts_dir.mkdir(parents=True, exist_ok=True)

    # 准备数据
    layouts = list(layout_stats.keys())
    prices = [layout_stats[layout]['均价'] for layout in layouts]
    sqm_prices = [layout_stats[layout]['均单位面积租金'] for layout in layouts]
    sample_counts = [layout_stats[layout]['样本数'] for layout in layouts]
    avg_areas = [layout_stats[layout]['均面积'] for layout in layouts]

    # 1. 户型综合分析图
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    # 户型月租金均价对比
    bars1 = ax1.bar(layouts, prices, color=['lightblue', 'lightgreen', 'lightcoral'], alpha=0.8, width=0.6)
    ax1.set_title('不同户型月租金均价对比', fontsize=14, fontweight='bold')
    ax1.set_ylabel('月租金 (元)', fontsize=12)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_ylim(0, max(prices) * 1.2)  # 设置y轴范围
    for bar, price in zip(bars1, prices):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(prices)*0.02,
                f'¥{price:.0f}', ha='center', va='bottom', fontweight='bold')

    # 户型单位面积租金均价对比
    bars2 = ax2.bar(layouts, sqm_prices, color=['lightblue', 'lightgreen', 'lightcoral'], alpha=0.8, width=0.6)
    ax2.set_title('不同户型单位面积租金均价对比', fontsize=14, fontweight='bold')
    ax2.set_ylabel('单位面积租金 (元/㎡)', fontsize=12)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim(0, max(sqm_prices) * 1.2)
    for bar, price in zip(bars2, sqm_prices):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(sqm_prices)*0.02,
                f'¥{price:.1f}', ha='center', va='bottom', fontweight='bold')

    # 户型样本数量分布
    bars3 = ax3.bar(layouts, sample_counts, color=['lightblue', 'lightgreen', 'lightcoral'], alpha=0.8, width=0.6)
    ax3.set_title('不同户型样本数量分布', fontsize=14, fontweight='bold')
    ax3.set_ylabel('样本数量', fontsize=12)
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.set_ylim(0, max(sample_counts) * 1.2)
    for bar, count in zip(bars3, sample_counts):
        ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(sample_counts)*0.02,
                f'{int(count)}', ha='center', va='bottom', fontweight='bold')

    # 户型平均面积对比
    bars4 = ax4.bar(layouts, avg_areas, color=['lightblue', 'lightgreen', 'lightcoral'], alpha=0.8, width=0.6)
    ax4.set_title('不同户型平均面积对比', fontsize=14, fontweight='bold')
    ax4.set_ylabel('平均面积 (㎡)', fontsize=12)
    ax4.grid(True, alpha=0.3, axis='y')
    ax4.set_ylim(0, max(avg_areas) * 1.2)
    for bar, area in zip(bars4, avg_areas):
        ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(avg_areas)*0.02,
                f'{area:.1f}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(charts_dir / 'layout_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. 户型箱线图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # 租金箱线图
    layout_data_rent = []
    layout_data_sqm = []
    labels = []
    for bedrooms in [1, 2, 3]:
        layout_df = df[df['bedrooms'] == bedrooms]
        if len(layout_df) > 0:
            layout_data_rent.append(layout_df['price'].values)
            layout_data_sqm.append(layout_df['price_per_sqm'].values)
            labels.append(f'{bedrooms}居')

    if layout_data_rent:
        bp1 = ax1.boxplot(layout_data_rent, labels=labels, patch_artist=True,
                         boxprops=dict(facecolor='lightblue', alpha=0.7),
                         medianprops=dict(color='red', linewidth=2),
                         whiskerprops=dict(color='blue', alpha=0.7),
                         capprops=dict(color='blue', alpha=0.7),
                         flierprops=dict(marker='o', markersize=3, alpha=0.5))
        ax1.set_title('不同户型租金分布箱线图', fontsize=14, fontweight='bold')
        ax1.set_ylabel('月租金 (元)', fontsize=12)
        ax1.grid(True, alpha=0.3, axis='y')

        # 添加均值点
        for i, layout in enumerate(layouts):
            mean_price = layout_stats[layout]['均价']
            ax1.scatter(i+1, mean_price, color='red', marker='D', s=50, zorder=3, label='均价' if i==0 else "")

        ax1.legend()

    if layout_data_sqm:
        bp2 = ax2.boxplot(layout_data_sqm, labels=labels, patch_artist=True,
                         boxprops=dict(facecolor='lightgreen', alpha=0.7),
                         medianprops=dict(color='red', linewidth=2),
                         whiskerprops=dict(color='green', alpha=0.7),
                         capprops=dict(color='green', alpha=0.7),
                         flierprops=dict(marker='o', markersize=3, alpha=0.5))
        ax2.set_title('不同户型单位面积租金分布箱线图', fontsize=14, fontweight='bold')
        ax2.set_ylabel('单位面积租金 (元/㎡)', fontsize=12)
        ax2.grid(True, alpha=0.3, axis='y')

        # 添加均值点
        for i, layout in enumerate(layouts):
            mean_sqm = layout_stats[layout]['均单位面积租金']
            ax2.scatter(i+1, mean_sqm, color='red', marker='D', s=50, zorder=3, label='均价' if i==0 else "")

        ax2.legend()

    plt.tight_layout()
    plt.savefig(charts_dir / 'layout_boxplot.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. 户型详细统计表
    fig, ax = plt.subplots(figsize=(16, 6))
    ax.axis('off')

    # 创建表格数据
    table_data = [
        ['户型', '均价(元)', '最高价(元)', '最低价(元)', '中位数(元)', '标准差(元)', '样本数', '均面积(㎡)', '面积标准差', '均单位面积租金(元/㎡)', '25%分位数', '75%分位数']
    ]

    for layout_name, stats in layout_stats.items():
        table_data.append([
            layout_name,
            f"¥{stats['均价']:.0f}",
            f"¥{stats['最高价']:.0f}",
            f"¥{stats['最低价']:.0f}",
            f"¥{stats['中位数']:.0f}",
            f"¥{stats['标准差']:.0f}",
            f"{stats['样本数']}",
            f"{stats['均面积']:.1f}",
            f"{stats['面积标准差']:.1f}",
            f"¥{stats['均单位面积租金']:.1f}",
            f"¥{stats['价格分位数']['25%']:.0f}",
            f"¥{stats['价格分位数']['75%']:.0f}"
        ])

    table = ax.table(cellText=table_data, loc='center', cellLoc='center',
                    colWidths=[0.08, 0.09, 0.09, 0.09, 0.09, 0.09, 0.07, 0.08, 0.08, 0.11, 0.08, 0.08])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.1, 1.4)

    # 设置表头样式
    for i in range(len(table_data[0])):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(color='white', weight='bold', fontsize=10)

    ax.set_title('北京租房市场户型详细统计表', fontsize=16, fontweight='bold', pad=20)

    plt.savefig(charts_dir / 'layout_statistics_table.png', dpi=300, bbox_inches='tight',
                bbox_extra_artists=[ax.title])
    plt.close()

    print("\n户型分析图表已生成:")
    print("- layout_analysis.png: 户型综合分析图表")
    print("- layout_boxplot.png: 户型箱线图")
    print("- layout_statistics_table.png: 户型详细统计表")

def generate_layout_report(df, layout_stats):
    """生成户型分析报告"""
    if df is None or not layout_stats:
        return

    report_dir = Path('reports')
    report_dir.mkdir(exist_ok=True)

    # 计算整体统计
    total_samples = sum(stats['样本数'] for stats in layout_stats.values())
    avg_price_1bed = layout_stats.get('1居', {}).get('均价', 0)
    avg_price_2bed = layout_stats.get('2居', {}).get('均价', 0)
    avg_price_3bed = layout_stats.get('3居', {}).get('均价', 0)

    price_diff_1to2 = avg_price_2bed - avg_price_1bed if avg_price_2bed > 0 and avg_price_1bed > 0 else 0
    price_diff_2to3 = avg_price_3bed - avg_price_2bed if avg_price_3bed > 0 and avg_price_2bed > 0 else 0

    report_content = f"""# 北京租房市场户型分析报告

## 数据概览
- 总样本数: {total_samples} 条记录 (1-3居室)
- 数据来源: 链家网北京地区租房数据
- 分析时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## 户型租金统计分析

### 各户型租金统计 (元/月)
| 户型 | 均价 | 最高价 | 最低价 | 中位数 | 标准差 | 样本数 |
|------|------|--------|--------|--------|--------|--------|
{chr(10).join([f'| {layout} | ¥{stats["均价"]:.0f} | ¥{stats["最高价"]:.0f} | ¥{stats["最低价"]:.0f} | ¥{stats["中位数"]:.0f} | ¥{stats["标准差"]:.0f} | {stats["样本数"]} |' for layout, stats in layout_stats.items()])}

### 各户型面积统计 (㎡)
| 户型 | 均面积 | 面积标准差 | 样本数 |
|------|--------|------------|--------|
{chr(10).join([f'| {layout} | {stats["均面积"]:.1f} | {stats["面积标准差"]:.1f} | {stats["样本数"]} |' for layout, stats in layout_stats.items()])}

### 各户型单位面积租金统计 (元/㎡)
| 户型 | 均价 | 样本数 |
|------|------|--------|
{chr(10).join([f'| {layout} | ¥{stats["均单位面积租金"]:.1f} | {stats["样本数"]} |' for layout, stats in layout_stats.items()])}

## 户型对比分析

### 价格差异分析
- **1居→2居价格涨幅**: ¥{price_diff_1to2:.0f} ({price_diff_1to2/avg_price_1bed*100:.1f}% 涨幅)
- **2居→3居价格涨幅**: ¥{price_diff_2to3:.0f} ({price_diff_2to3/avg_price_2bed*100:.1f}% 涨幅)
- **总体趋势**: 随着房间数量增加，租金呈阶梯式上涨

### 样本数量分布
{chr(10).join([f'- {layout}: {stats["样本数"]} 套 ({stats["样本数"]/total_samples*100:.1f}%)' for layout, stats in layout_stats.items()])}

## 分析结论

### 1. 户型价格特征
- **一居室**: 价格相对较低 (¥{avg_price_1bed:.0f}/月)，适合单身或年轻情侣
- **二居室**: 市场需求最大，价格适中 (¥{avg_price_2bed:.0f}/月)，性价比相对较高
- **三居室**: 价格最高 (¥{avg_price_3bed:.0f}/月)，主要面向家庭用户

### 2. 面积与价格关系
- 户型面积随房间数量增加而增大，符合居住需求
- 单位面积租金整体呈上升趋势，表明大户型房源的稀缺性和高需求

### 3. 市场洞察
- 二居室是北京租房市场的主力户型，占比较高
- 价格差异明显反映了不同人群的住房需求
- 大户型房源价格溢价明显，体现了市场供需关系

### 4. 投资建议
- **首次置业**: 建议选择二居室，平衡价格与实用性
- **家庭住房**: 三居室提供更舒适的居住环境，但租金成本较高
- **过渡住房**: 一居室适合短期居住或单身用户

## 图表说明

本报告包含以下图表：
- `layout_analysis.png`: 不同户型租金、单位面积租金、样本数量和平均面积的综合对比
- `layout_boxplot.png`: 不同户型的租金和单位面积租金分布箱线图
- `layout_statistics_table.png`: 包含完整统计数据的详细表格

---
*报告生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*
*数据来源: 链家网北京租房数据*
"""

    report_path = report_dir / 'layout_analysis_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"\n户型分析报告已生成: {report_path}")

def main():
    """主函数"""
    print("北京租房市场户型分析")
    print("=" * 30)

    # 加载数据
    df = load_data()
    if df is None:
        return

    # 分析户型统计数据
    result = analyze_layout_statistics(df)
    if result is None:
        return

    main_layouts, layout_stats = result

    # 打印统计信息
    print_layout_statistics(layout_stats)

    # 创建可视化
    create_layout_visualizations(main_layouts, layout_stats)

    # 生成报告
    generate_layout_report(main_layouts, layout_stats)

    print("\n户型分析完成！")
    print("结果文件保存在 reports/ 目录中")

if __name__ == "__main__":
    main()
