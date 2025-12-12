"""
租金数据分析和可视化脚本
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path
from ..utils.data_processor import load_data, clean_data

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")

def analyze_rent_statistics(df):
    """分析租金统计信息"""
    if df is None or df.empty:
        return None

    print("\n" + "="*50)
    print("租金统计分析")
    print("="*50)

    # 过滤有效数据
    valid_data = df.dropna(subset=['price', 'area'])
    valid_data = valid_data[(valid_data['price'] > 0) & (valid_data['area'] > 0)]

    if valid_data.empty:
        print("没有有效的租金数据")
        return None

    # 计算单位面积租金
    valid_data['price_per_sqm'] = valid_data['price'] / valid_data['area']

    # 租金统计
    rent_stats = {
        '均价': valid_data['price'].mean(),
        '最高价': valid_data['price'].max(),
        '最低价': valid_data['price'].min(),
        '中位数': valid_data['price'].median(),
        '标准差': valid_data['price'].std(),
        '样本数': len(valid_data)
    }

    # 单位面积租金统计
    sqm_stats = {
        '均价': valid_data['price_per_sqm'].mean(),
        '最高价': valid_data['price_per_sqm'].max(),
        '最低价': valid_data['price_per_sqm'].min(),
        '中位数': valid_data['price_per_sqm'].median(),
        '标准差': valid_data['price_per_sqm'].std(),
        '样本数': len(valid_data)
    }

    print("\n租金统计 (元/月):")
    for key, value in rent_stats.items():
        if key == '样本数':
            print(f"  {key}: {int(value)}")
        else:
            print(f"  {key}: ¥{value:.0f}")

    print("\n单位面积租金统计 (元/㎡/月):")
    for key, value in sqm_stats.items():
        if key == '样本数':
            print(f"  {key}: {int(value)}")
        else:
            print(f"  {key}: ¥{value:.1f}")

    return valid_data, rent_stats, sqm_stats

def create_visualizations(df, rent_stats, sqm_stats):
    """创建可视化图表"""
    if df is None:
        return

    # 创建图表目录
    charts_dir = Path('reports/charts')
    charts_dir.mkdir(parents=True, exist_ok=True)

    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    # 1. 租金分布直方图
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

    # 租金直方图
    ax1.hist(df['price'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
    ax1.set_title('租金分布直方图', fontsize=14, fontweight='bold')
    ax1.set_xlabel('月租金 (元)')
    ax1.set_ylabel('房源数量')
    ax1.grid(True, alpha=0.3)

    # 添加统计线
    ax1.axvline(rent_stats['均价'], color='red', linestyle='--', linewidth=2, label=f"均价: ¥{rent_stats['均价']:.0f}")
    ax1.axvline(rent_stats['中位数'], color='green', linestyle='--', linewidth=2, label=f"中位数: ¥{rent_stats['中位数']:.0f}")
    ax1.legend()

    # 单位面积租金直方图
    ax2.hist(df['price_per_sqm'], bins=50, alpha=0.7, color='lightgreen', edgecolor='black')
    ax2.set_title('单位面积租金分布直方图', fontsize=14, fontweight='bold')
    ax2.set_xlabel('单位面积租金 (元/㎡)')
    ax2.set_ylabel('房源数量')
    ax2.grid(True, alpha=0.3)

    # 添加统计线
    ax2.axvline(sqm_stats['均价'], color='red', linestyle='--', linewidth=2, label=f"均价: ¥{sqm_stats['均价']:.1f}")
    ax2.axvline(sqm_stats['中位数'], color='green', linestyle='--', linewidth=2, label=f"中位数: ¥{sqm_stats['中位数']:.1f}")
    ax2.legend()

    # 租金箱线图
    ax3.boxplot(df['price'], vert=True, patch_artist=True,
                boxprops=dict(facecolor='lightblue'),
                medianprops=dict(color='red', linewidth=2))
    ax3.set_title('租金箱线图', fontsize=14, fontweight='bold')
    ax3.set_ylabel('月租金 (元)')
    ax3.grid(True, alpha=0.3)

    # 单位面积租金箱线图
    ax4.boxplot(df['price_per_sqm'], vert=True, patch_artist=True,
                boxprops=dict(facecolor='lightcoral'),
                medianprops=dict(color='red', linewidth=2))
    ax4.set_title('单位面积租金箱线图', fontsize=14, fontweight='bold')
    ax4.set_ylabel('单位面积租金 (元/㎡)')
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(charts_dir / 'rent_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. 创建统计表
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('off')

    # 创建表格数据
    table_data = [
        ['统计指标', '租金 (元/月)', '单位面积租金 (元/㎡/月)'],
        ['均价', f"¥{rent_stats['均价']:.0f}", f"¥{sqm_stats['均价']:.1f}"],
        ['最高价', f"¥{rent_stats['最高价']:.0f}", f"¥{sqm_stats['最高价']:.1f}"],
        ['最低价', f"¥{rent_stats['最低价']:.0f}", f"¥{sqm_stats['最低价']:.1f}"],
        ['中位数', f"¥{rent_stats['中位数']:.0f}", f"¥{sqm_stats['中位数']:.1f}"],
        ['标准差', f"¥{rent_stats['标准差']:.0f}", f"¥{sqm_stats['标准差']:.1f}"],
        ['样本数', f"{rent_stats['样本数']}", f"{sqm_stats['样本数']}"]
    ]

    table = ax.table(cellText=table_data, loc='center', cellLoc='center',
                    colWidths=[0.3, 0.35, 0.35])
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.5)

    # 设置表头样式
    for i in range(len(table_data[0])):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(color='white', weight='bold')

    ax.set_title('北京租房市场统计表', fontsize=16, fontweight='bold', pad=20)

    plt.savefig(charts_dir / 'rent_statistics_table.png', dpi=300, bbox_inches='tight',
                bbox_extra_artists=[ax.title])
    plt.close()

    # 3. 租金分位数分析
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # 租金分位数
    quantiles_rent = df['price'].quantile([0.25, 0.5, 0.75])
    ax1.bar(['25%分位数', '50%分位数(中位数)', '75%分位数'],
            [quantiles_rent[0.25], quantiles_rent[0.5], quantiles_rent[0.75]],
            color=['lightblue', 'lightgreen', 'lightcoral'])
    ax1.set_title('租金分位数分析', fontsize=14, fontweight='bold')
    ax1.set_ylabel('月租金 (元)')
    ax1.tick_params(axis='x', rotation=45)

    # 添加数值标签
    for i, v in enumerate([quantiles_rent[0.25], quantiles_rent[0.5], quantiles_rent[0.75]]):
        ax1.text(i, v + 50, f'¥{v:.0f}', ha='center', va='bottom')

    # 单位面积租金分位数
    quantiles_sqm = df['price_per_sqm'].quantile([0.25, 0.5, 0.75])
    ax2.bar(['25%分位数', '50%分位数(中位数)', '75%分位数'],
            [quantiles_sqm[0.25], quantiles_sqm[0.5], quantiles_sqm[0.75]],
            color=['lightblue', 'lightgreen', 'lightcoral'])
    ax2.set_title('单位面积租金分位数分析', fontsize=14, fontweight='bold')
    ax2.set_ylabel('单位面积租金 (元/㎡)')
    ax2.tick_params(axis='x', rotation=45)

    # 添加数值标签
    for i, v in enumerate([quantiles_sqm[0.25], quantiles_sqm[0.5], quantiles_sqm[0.75]]):
        ax2.text(i, v + 2, f'¥{v:.1f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(charts_dir / 'rent_quantiles.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("\n图表已生成:")
    print("- rent_analysis.png: 租金分布分析图表")
    print("- rent_statistics_table.png: 统计数据表格")
    print("- rent_quantiles.png: 分位数分析图表")

def generate_report(df, rent_stats, sqm_stats):
    """生成分析报告"""
    if df is None:
        return

    report_dir = Path('reports')
    report_dir.mkdir(exist_ok=True)

    report_content = f"""# 北京租房市场租金分析报告

## 数据概览
- 总样本数: {len(df)} 条记录
- 数据来源: 链家网北京地区租房数据
- 分析时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## 租金统计分析

### 月租金统计 (元/月)
- **均价**: ¥{rent_stats['均价']:.0f}
- **最高价**: ¥{rent_stats['最高价']:.0f}
- **最低价**: ¥{rent_stats['最低价']:.0f}
- **中位数**: ¥{rent_stats['中位数']:.0f}
- **标准差**: ¥{rent_stats['标准差']:.0f}
- **样本数**: {rent_stats['样本数']}

### 单位面积租金统计 (元/㎡/月)
- **均价**: ¥{sqm_stats['均价']:.1f}
- **最高价**: ¥{sqm_stats['最高价']:.1f}
- **最低价**: ¥{sqm_stats['最低价']:.1f}
- **中位数**: ¥{sqm_stats['中位数']:.1f}
- **标准差**: ¥{sqm_stats['标准差']:.1f}
- **样本数**: {sqm_stats['样本数']}

## 分析结论

1. **价格分布特征**:
   - 租金价格区间较大，从 ¥{rent_stats['最低价']:.0f} 到 ¥{rent_stats['最高价']:.0f}
   - 中位数 ¥{rent_stats['中位数']:.0f} 比均价 ¥{rent_stats['均价']:.0f} 略低，说明存在少量高价房源拉高了平均值

2. **单位面积租金分析**:
   - 平均每平方米每月 ¥{sqm_stats['均价']:.1f}
   - 价格相对稳定，中位数和均价相近

3. **市场洞察**:
   - 北京租房市场价格差异明显
   - 大部分房源集中在中等价格区间
   - 高端房源占比相对较少但对整体均价影响显著

## 图表说明

本报告包含以下图表：
- `rent_analysis.png`: 租金和单位面积租金的分布直方图和箱线图
- `rent_statistics_table.png`: 详细统计数据表格
- `rent_quantiles.png`: 25%、50%、75%分位数分析

---
*报告生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    report_path = report_dir / 'rent_analysis_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"\n分析报告已生成: {report_path}")

def main():
    """主函数"""
    print("北京租房市场租金分析")
    print("=" * 40)

    # 加载数据
    df = load_data()
    if df is None:
        return

    # 分析统计数据
    result = analyze_rent_statistics(df)
    if result is None:
        return

    valid_data, rent_stats, sqm_stats = result

    # 创建可视化
    create_visualizations(valid_data, rent_stats, sqm_stats)

    # 生成报告
    generate_report(valid_data, rent_stats, sqm_stats)

    print("\n分析完成！")
    print("结果文件保存在 reports/ 目录中")

if __name__ == "__main__":
    main()
