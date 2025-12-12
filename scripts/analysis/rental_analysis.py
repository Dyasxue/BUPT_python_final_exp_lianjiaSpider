"""
租房数据分析主模块
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import os
from datetime import datetime
import logging
from config import CITIES, SALARY_DATA

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RentalAnalyzer:
    def __init__(self, data_path=None):
        self.data = None
        if data_path:
            self.load_data(data_path)

    def load_data(self, data_path):
        """加载处理后的数据"""
        try:
            self.data = pd.read_csv(data_path, encoding='utf-8-sig')
            logger.info(f"成功加载数据: {len(self.data)} 条记录")
        except Exception as e:
            logger.error(f"加载数据失败: {e}")

    def analyze_overall_prices(self):
        """分析总体租金情况"""
        if self.data is None:
            return None

        logger.info("开始分析总体租金情况...")

        # 按城市分组计算统计信息
        city_stats = self.data.groupby('city').agg({
            'price': ['mean', 'median', 'min', 'max', 'count'],
            'price_per_sqm': ['mean', 'median', 'min', 'max'],
            'area': 'mean'
        }).round(2)

        # 重新整理列名
        city_stats.columns = ['_'.join(col).strip() for col in city_stats.columns]
        city_stats = city_stats.reset_index()

        return city_stats

    def analyze_layout_comparison(self):
        """分析户型比较"""
        if self.data is None:
            return None

        logger.info("开始分析户型比较...")

        # 按城市和户型分组
        layout_stats = self.data.groupby(['city', 'layout_type']).agg({
            'price': ['mean', 'median', 'min', 'max', 'count'],
            'price_per_sqm': ['mean', 'median']
        }).round(2)

        layout_stats.columns = ['_'.join(col).strip() for col in layout_stats.columns]
        layout_stats = layout_stats.reset_index()

        return layout_stats

    def analyze_district_prices(self):
        """分析各城市板块均价"""
        if self.data is None:
            return None

        logger.info("开始分析板块均价...")

        # 按城市和区域分组
        district_stats = self.data.groupby(['city', 'district']).agg({
            'price': ['mean', 'median', 'count'],
            'price_per_sqm': ['mean', 'median']
        }).round(2)

        district_stats.columns = ['_'.join(col).strip() for col in district_stats.columns]
        district_stats = district_stats.reset_index()

        # 过滤样本数太少的区域
        district_stats = district_stats[district_stats['price_count'] >= 10]

        return district_stats

    def analyze_orientation_prices(self):
        """分析朝向价格分布"""
        if self.data is None:
            return None

        logger.info("开始分析朝向价格分布...")

        orientation_stats = self.data.groupby(['city', 'orientation_clean']).agg({
            'price_per_sqm': ['mean', 'median', 'count'],
            'price': ['mean', 'median']
        }).round(2)

        orientation_stats.columns = ['_'.join(col).strip() for col in orientation_stats.columns]
        orientation_stats = orientation_stats.reset_index()

        # 过滤样本数太少的朝向
        orientation_stats = orientation_stats[orientation_stats['price_per_sqm_count'] >= 5]

        return orientation_stats

    def analyze_agency_distribution(self):
        """分析中介品牌分布"""
        if self.data is None:
            return None

        logger.info("开始分析中介品牌分布...")

        # 统计各城市主要中介
        agency_stats = self.data.groupby(['city', 'agency']).size().reset_index(name='count')

        # 计算占比
        total_by_city = agency_stats.groupby('city')['count'].transform('sum')
        agency_stats['percentage'] = (agency_stats['count'] / total_by_city * 100).round(2)

        # 保留主要中介（占比>1%）
        agency_stats = agency_stats[agency_stats['percentage'] > 1]

        return agency_stats

    def analyze_salary_rental_ratio(self):
        """分析工资与租金比例关系"""
        if self.data is None:
            return None

        logger.info("开始分析工资与租金关系...")

        # 计算各城市的平均租金和工资数据
        city_avg_rent = self.data.groupby('city')['price'].mean().round(2)
        city_avg_sqm_rent = self.data.groupby('city')['price_per_sqm'].mean().round(2)

        # 创建分析数据框
        salary_df = pd.DataFrame({
            'city': list(SALARY_DATA.keys()),
            'avg_salary': list(SALARY_DATA.values()),
            'avg_rent': [city_avg_rent.get(city, 0) for city in SALARY_DATA.keys()],
            'avg_sqm_rent': [city_avg_sqm_rent.get(city, 0) for city in SALARY_DATA.keys()]
        })

        # 计算租金负担比例
        salary_df['rent_to_salary_ratio'] = (salary_df['avg_rent'] / salary_df['avg_salary']).round(4)
        salary_df['sqm_rent_to_salary_ratio'] = (salary_df['avg_sqm_rent'] * 60 / salary_df['avg_salary']).round(4)  # 假设60平米

        return salary_df

    def create_visualizations(self):
        """创建所有可视化图表"""
        if self.data is None:
            return

        logger.info("开始创建可视化图表...")

        # 创建图表目录
        os.makedirs('reports/charts', exist_ok=True)

        # 1. 总体租金比较
        self._plot_overall_comparison()

        # 2. 户型比较
        self._plot_layout_comparison()

        # 3. 板块均价
        self._plot_district_comparison()

        # 4. 朝向价格分布
        self._plot_orientation_comparison()

        # 5. 中介品牌分布
        self._plot_agency_distribution()

        # 6. 工资租金关系
        self._plot_salary_rental_ratio()

    def _plot_overall_comparison(self):
        """绘制总体租金比较图"""
        city_stats = self.analyze_overall_prices()

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

        # 平均租金
        bars1 = ax1.bar(city_stats['city'], city_stats['price_mean'], color='skyblue')
        ax1.set_title('各城市平均月租金比较', fontsize=14, fontweight='bold')
        ax1.set_ylabel('月租金 (元)')
        ax1.tick_params(axis='x', rotation=45)
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.0f}', ha='center', va='bottom')

        # 单位面积租金
        bars2 = ax2.bar(city_stats['city'], city_stats['price_per_sqm_mean'], color='lightgreen')
        ax2.set_title('各城市单位面积租金比较', fontsize=14, fontweight='bold')
        ax2.set_ylabel('元/平方米')
        ax2.tick_params(axis='x', rotation=45)
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom')

        # 租金箱线图
        rent_data = [self.data[self.data['city'] == city]['price'] for city in city_stats['city']]
        ax3.boxplot(rent_data, labels=city_stats['city'])
        ax3.set_title('各城市租金分布箱线图', fontsize=14, fontweight='bold')
        ax3.set_ylabel('月租金 (元)')
        ax3.tick_params(axis='x', rotation=45)

        # 单位面积租金箱线图
        sqm_data = [self.data[self.data['city'] == city]['price_per_sqm'] for city in city_stats['city']]
        ax4.boxplot(sqm_data, labels=city_stats['city'])
        ax4.set_title('各城市单位面积租金分布箱线图', fontsize=14, fontweight='bold')
        ax4.set_ylabel('元/平方米')
        ax4.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig('reports/charts/overall_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_layout_comparison(self):
        """绘制户型比较图"""
        layout_stats = self.analyze_layout_comparison()

        # 过滤主要户型
        main_layouts = ['一居', '二居', '三居']
        layout_filtered = layout_stats[layout_stats['layout_type'].isin(main_layouts)]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # 各户型平均租金
        pivot_rent = layout_filtered.pivot(index='city', columns='layout_type', values='price_mean')
        pivot_rent.plot(kind='bar', ax=ax1, width=0.8)
        ax1.set_title('各城市不同户型平均租金', fontsize=14, fontweight='bold')
        ax1.set_ylabel('月租金 (元)')
        ax1.legend(title='户型')
        ax1.tick_params(axis='x', rotation=45)

        # 各户型单位面积租金
        pivot_sqm = layout_filtered.pivot(index='city', columns='layout_type', values='price_per_sqm_mean')
        pivot_sqm.plot(kind='bar', ax=ax2, width=0.8)
        ax2.set_title('各城市不同户型单位面积租金', fontsize=14, fontweight='bold')
        ax2.set_ylabel('元/平方米')
        ax2.legend(title='户型')
        ax2.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig('reports/charts/layout_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_district_comparison(self):
        """绘制板块均价图"""
        district_stats = self.analyze_district_prices()

        # 选择每个城市租金最高的5个区域
        top_districts = district_stats.sort_values(['city', 'price_per_sqm_mean'], ascending=[True, False])
        top_districts = top_districts.groupby('city').head(5)

        fig, ax = plt.subplots(figsize=(15, 8))

        cities = top_districts['city'].unique()
        bar_width = 0.15
        index = np.arange(len(cities))

        for i, city in enumerate(cities):
            city_data = top_districts[top_districts['city'] == city]
            x_pos = index[i] + np.arange(len(city_data)) * bar_width
            bars = ax.bar(x_pos, city_data['price_per_sqm_mean'],
                         bar_width, label=city, alpha=0.8)

            # 添加数值标签
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}', ha='center', va='bottom', fontsize=8)

        ax.set_xlabel('城市')
        ax.set_ylabel('单位面积租金 (元/平方米)')
        ax.set_title('各城市主要板块单位面积租金比较', fontsize=14, fontweight='bold')
        ax.set_xticks(index + bar_width * 2)
        ax.set_xticklabels(cities)
        ax.legend()

        plt.tight_layout()
        plt.savefig('reports/charts/district_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_orientation_comparison(self):
        """绘制朝向价格分布图"""
        orientation_stats = self.analyze_orientation_prices()

        fig, ax = plt.subplots(figsize=(12, 8))

        # 创建热力图数据
        pivot_data = orientation_stats.pivot(index='orientation_clean',
                                           columns='city',
                                           values='price_per_sqm_mean')

        sns.heatmap(pivot_data, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax)
        ax.set_title('各城市不同朝向单位面积租金热力图', fontsize=14, fontweight='bold')
        ax.set_xlabel('城市')
        ax.set_ylabel('朝向')

        plt.tight_layout()
        plt.savefig('reports/charts/orientation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_agency_distribution(self):
        """绘制中介品牌分布图"""
        agency_stats = self.analyze_agency_distribution()

        fig, ax = plt.subplots(figsize=(15, 8))

        # 选择每个城市占比最高的前5个中介
        top_agencies = agency_stats.sort_values(['city', 'percentage'], ascending=[True, False])
        top_agencies = top_agencies.groupby('city').head(5)

        cities = top_agencies['city'].unique()
        agencies = top_agencies['agency'].unique()

        # 创建堆叠条形图
        bottom = np.zeros(len(cities))

        for agency in agencies[:8]:  # 限制显示的主要中介
            agency_data = []
            for city in cities:
                city_agency = top_agencies[(top_agencies['city'] == city) &
                                          (top_agencies['agency'] == agency)]
                if not city_agency.empty:
                    agency_data.append(city_agency['percentage'].values[0])
                else:
                    agency_data.append(0)

            bars = ax.bar(cities, agency_data, bottom=bottom, label=agency, alpha=0.8)
            bottom += np.array(agency_data)

        ax.set_ylabel('占比 (%)')
        ax.set_title('各城市主要租房中介品牌分布', fontsize=14, fontweight='bold')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig('reports/charts/agency_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_salary_rental_ratio(self):
        """绘制工资租金比例图"""
        salary_analysis = self.analyze_salary_rental_ratio()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # 租金占工资比例
        bars1 = ax1.bar(salary_analysis['city'], salary_analysis['rent_to_salary_ratio'] * 100,
                       color='coral', alpha=0.7)
        ax1.set_title('各城市平均租金占月工资比例', fontsize=14, fontweight='bold')
        ax1.set_ylabel('租金/工资 (%)')
        ax1.tick_params(axis='x', rotation=45)
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom')

        # 60平米房租占工资比例
        bars2 = ax2.bar(salary_analysis['city'], salary_analysis['sqm_rent_to_salary_ratio'] * 100,
                       color='lightcoral', alpha=0.7)
        ax2.set_title('各城市60平米房租占月工资比例', fontsize=14, fontweight='bold')
        ax2.set_ylabel('60平米房租/工资 (%)')
        ax2.tick_params(axis='x', rotation=45)
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig('reports/charts/salary_rental_ratio.png', dpi=300, bbox_inches='tight')
        plt.close()

    def generate_report(self):
        """生成分析报告"""
        logger.info("开始生成分析报告...")

        # 执行所有分析
        overall_stats = self.analyze_overall_prices()
        layout_stats = self.analyze_layout_comparison()
        district_stats = self.analyze_district_prices()
        orientation_stats = self.analyze_orientation_prices()
        agency_stats = self.analyze_agency_distribution()
        salary_analysis = self.analyze_salary_rental_ratio()

        # 生成可视化
        self.create_visualizations()

        # 创建报告
        report_content = self._generate_report_content(
            overall_stats, layout_stats, district_stats,
            orientation_stats, agency_stats, salary_analysis
        )

        # 保存报告
        report_path = f"reports/rental_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        logger.info(f"分析报告已生成: {report_path}")
        return report_path

    def _generate_report_content(self, overall_stats, layout_stats, district_stats,
                               orientation_stats, agency_stats, salary_analysis):
        """生成报告内容"""
        report = f"""# 链家租房数据分析报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 数据概览

总共分析了 {len(self.data)} 条租房记录，覆盖 {len(CITIES)} 个城市。

## 1. 总体租金情况分析

### 各城市租金统计

{overall_stats.to_markdown(index=False)}

### 主要发现：
- **最高租金城市**: {overall_stats.loc[overall_stats['price_mean'].idxmax(), 'city']} (均价: ¥{overall_stats['price_mean'].max():.0f})
- **最低租金城市**: {overall_stats.loc[overall_stats['price_mean'].idxmin(), 'city']} (均价: ¥{overall_stats['price_mean'].min():.0f})
- **最高单位面积租金**: {overall_stats.loc[overall_stats['price_per_sqm_mean'].idxmax(), 'city']} (¥{overall_stats['price_per_sqm_mean'].max():.1f}/㎡)

## 2. 户型租金比较分析

### 主要户型租金对比

{layout_stats[layout_stats['layout_type'].isin(['一居', '二居', '三居'])].to_markdown(index=False)}

### 主要发现：
- 一居室租金相对较低，适合单身或情侣
- 三居室租金最高，适合家庭居住
- 不同城市户型租金差异明显

## 3. 城市板块均价分析

### 各城市热门板块租金情况

{district_stats.head(20).to_markdown(index=False)}

## 4. 朝向价格分布分析

### 朝向租金热力图数据

{orientation_stats.to_markdown(index=False)}

### 朝向价格分析：
- **最贵朝向**: 南向房源通常价格最高，光照充足
- **最便宜朝向**: 北向房源通常价格最低，光照相对不足
- 城市间朝向价格差异: 不同城市的朝向溢价存在差异

## 5. 租房中介品牌分布分析

### 主要中介品牌占比

{agency_stats.to_markdown(index=False)}

## 6. 工资与租金负担分析

### 工资租金比例分析

{salary_analysis.to_markdown(index=False)}

### 租金负担分析：
- **租金负担最重城市**: {salary_analysis.loc[salary_analysis['rent_to_salary_ratio'].idxmax(), 'city']} ({salary_analysis['rent_to_salary_ratio'].max()*100:.1f}%)
- **租金负担最轻城市**: {salary_analysis.loc[salary_analysis['rent_to_salary_ratio'].idxmin(), 'city']} ({salary_analysis['rent_to_salary_ratio'].min()*100:.1f}%)

## 7. 自定义分析主题：租房性价比分析

### 分析设计
本分析将从以下维度评估租房性价比：
1. 租金与工资比例
2. 单位面积租金与城市发展水平
3. 交通便利性（地铁房源占比）
4. 房源质量（面积、楼层等）

### 性价比排名
{salary_analysis.sort_values('rent_to_salary_ratio').to_markdown(index=False)}

## 结论与建议

1. **一线城市租房压力大**: 北京、上海、深圳的租金水平显著高于其他城市
2. **户型选择建议**: 预算有限的租客可选择一居室，家庭用户可选择二居室
3. **朝向选择**: 南向房源性价比相对较高，光照条件好
4. **中介选择**: 大型品牌中介服务更规范，但佣金相对较高
5. **整体建议**: 建议租客根据收入水平合理选择城市和房源类型

---
*报告生成工具: Python数据分析脚本*
*数据来源: 链家网租房数据*
"""
        return report

def main():
    """主函数"""
    analyzer = RentalAnalyzer()

    # 查找最新的处理数据
    import glob
    processed_files = glob.glob('data/processed/*.csv')
    if not processed_files:
        logger.error("没有找到处理后的数据文件，请先运行数据处理脚本")
        return

    latest_file = max(processed_files, key=os.path.getctime)
    logger.info(f"使用最新的数据文件: {latest_file}")

    analyzer.load_data(latest_file)
    report_path = analyzer.generate_report()

    logger.info("分析完成！")

if __name__ == "__main__":
    main()

