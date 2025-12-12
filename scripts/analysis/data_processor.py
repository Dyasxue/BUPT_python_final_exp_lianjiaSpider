"""
数据处理和预处理模块
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
import logging
from config import DATA_FIELDS, ORIENTATION_MAPPING, CITIES

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        self.data = None

    def load_raw_data(self):
        """加载所有原始数据"""
        import os
        import glob

        all_data = []
        raw_files = glob.glob('data/raw/*.csv')

        for file_path in raw_files:
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                city_code = os.path.basename(file_path).split('_')[0]
                df['city_code'] = city_code
                all_data.append(df)
                logger.info(f"加载文件: {file_path}, 记录数: {len(df)}")
            except Exception as e:
                logger.error(f"加载文件失败 {file_path}: {e}")

        if all_data:
            self.data = pd.concat(all_data, ignore_index=True)
            logger.info(f"总共加载 {len(self.data)} 条记录")
        else:
            logger.warning("没有找到任何数据文件")
            self.data = pd.DataFrame(columns=DATA_FIELDS)

    def clean_price_data(self):
        """清理价格数据"""
        if self.data is None:
            return

        # 移除价格为0或异常的记录
        self.data = self.data[self.data['price'] > 0]
        self.data = self.data[self.data['price'] < 100000]  # 移除异常高价

        # 清理单位面积租金
        self.data['price_per_sqm'] = pd.to_numeric(self.data['price_per_sqm'], errors='coerce')
        self.data = self.data[self.data['price_per_sqm'] > 0]
        self.data = self.data[self.data['price_per_sqm'] < 1000]  # 移除异常值

        # 清理面积数据
        self.data['area'] = pd.to_numeric(self.data['area'], errors='coerce')
        self.data = self.data[(self.data['area'] > 10) & (self.data['area'] < 1000)]

        logger.info(f"价格数据清理后剩余 {len(self.data)} 条记录")

    def clean_layout_data(self):
        """清理户型数据"""
        if self.data is None:
            return

        # 转换数据类型
        self.data['bedrooms'] = pd.to_numeric(self.data['bedrooms'], errors='coerce').fillna(0).astype(int)
        self.data['living_rooms'] = pd.to_numeric(self.data['living_rooms'], errors='coerce').fillna(0).astype(int)
        self.data['bathrooms'] = pd.to_numeric(self.data['bathrooms'], errors='coerce').fillna(0).astype(int)

        # 过滤合理的户型
        self.data = self.data[
            (self.data['bedrooms'] >= 0) & (self.data['bedrooms'] <= 10) &
            (self.data['living_rooms'] >= 0) & (self.data['living_rooms'] <= 5) &
            (self.data['bathrooms'] >= 0) & (self.data['bathrooms'] <= 5)
        ]

        # 创建户型分类
        self.data['layout_type'] = self.data.apply(self._classify_layout, axis=1)

    def _classify_layout(self, row):
        """分类户型"""
        bedrooms = row['bedrooms']
        if bedrooms == 1:
            return '一居'
        elif bedrooms == 2:
            return '二居'
        elif bedrooms == 3:
            return '三居'
        elif bedrooms >= 4:
            return '四居及以上'
        else:
            return '其他'

    def clean_orientation_data(self):
        """清理朝向数据"""
        if self.data is None:
            return

        # 标准化朝向
        self.data['orientation_clean'] = self.data['orientation'].apply(self._standardize_orientation)

        # 过滤有效朝向
        valid_orientations = ['东', '南', '西', '北', '东南', '西南', '东北', '西北', '南北']
        self.data = self.data[self.data['orientation_clean'].isin(valid_orientations)]

    def _standardize_orientation(self, orientation):
        """标准化朝向"""
        if pd.isna(orientation) or not orientation:
            return '未知'

        # 移除空格和特殊字符
        orientation = re.sub(r'\s+', '', str(orientation))

        # 映射到标准朝向
        for key, value in ORIENTATION_MAPPING.items():
            if key in orientation:
                return key

        return '其他'

    def clean_location_data(self):
        """清理位置数据"""
        if self.data is None:
            return

        # 清理区域信息
        self.data['district'] = self.data['district'].fillna('未知')

        # 清理地铁信息
        self.data['subway'] = self.data['subway'].fillna(False)

        # 清理中介信息
        self.data['agency'] = self.data['agency'].fillna('个人')

    def remove_duplicates(self):
        """移除重复数据"""
        if self.data is None:
            return

        initial_count = len(self.data)

        # 基于标题和价格去重
        self.data = self.data.drop_duplicates(subset=['title', 'price', 'area'])

        logger.info(f"去重后从 {initial_count} 条减少到 {len(self.data)} 条记录")

    def add_calculated_fields(self):
        """添加计算字段"""
        if self.data is None:
            return

        # 价格分位数分组
        self.data['price_category'] = pd.qcut(self.data['price'], q=4, labels=['低价', '中低价', '中高价', '高价'])

        # 面积分位数分组
        self.data['area_category'] = pd.qcut(self.data['area'], q=4, labels=['小户型', '中等', '较大', '大户型'])

        # 楼层分类
        self.data['floor_category'] = self.data.apply(self._classify_floor, axis=1)

    def _classify_floor(self, row):
        """分类楼层"""
        floor = row.get('floor', 0)
        total_floors = row.get('total_floors', 0)

        if total_floors == 0:
            return '未知'

        if floor / total_floors <= 0.3:
            return '低楼层'
        elif floor / total_floors <= 0.7:
            return '中楼层'
        else:
            return '高楼层'

    def validate_data_quality(self):
        """数据质量验证"""
        if self.data is None:
            return

        logger.info("=== 数据质量报告 ===")
        logger.info(f"总记录数: {len(self.data)}")

        # 检查缺失值
        missing_data = self.data.isnull().sum()
        if missing_data.sum() > 0:
            logger.info("缺失值统计:")
            for col, count in missing_data[missing_data > 0].items():
                logger.info(f"  {col}: {count} ({count/len(self.data)*100:.2f}%)")

        # 检查数值范围
        numeric_cols = ['price', 'price_per_sqm', 'area']
        for col in numeric_cols:
            if col in self.data.columns:
                stats = self.data[col].describe()
                logger.info(f"{col} 统计: 均值={stats['mean']:.2f}, 中位数={stats['50%']:.2f}, "
                          f"最小值={stats['min']:.2f}, 最大值={stats['max']:.2f}")

    def process_all(self):
        """执行所有数据处理步骤"""
        logger.info("开始数据处理...")

        self.load_raw_data()
        if self.data is None or len(self.data) == 0:
            logger.error("没有数据可处理")
            return None

        self.clean_price_data()
        self.clean_layout_data()
        self.clean_orientation_data()
        self.clean_location_data()
        self.remove_duplicates()
        self.add_calculated_fields()
        self.validate_data_quality()

        # 保存处理后的数据
        output_path = f"data/processed/processed_rental_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.data.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"处理后的数据已保存到: {output_path}")

        return self.data

if __name__ == "__main__":
    processor = DataProcessor()
    processed_data = processor.process_all()
