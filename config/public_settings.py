"""
链家爬虫公共配置文件 - 可安全上传到版本控制系统
"""

# Cookie和User-Agent配置现在位于sensitive_settings.py中
# 请确保创建并配置sensitive_settings.py文件

# 爬虫配置
MAX_PAGES = 300  # 最大爬取页数
REQUEST_TIMEOUT = 30  # 请求超时时间
DELAY_MIN = 1  # 最小延迟
DELAY_MAX = 3  # 最大延迟

# 输出配置
OUTPUT_DIR = 'data'
OUTPUT_FILENAME_PREFIX = 'beijing_rental_data'

# 数据字段映射
DATA_FIELDS = [
    'title',           # 房源标题
    'rent_type',       # 出租方式
    'district',        # 区域
    'sub_district',    # 子区域
    'community',       # 小区
    'area',            # 面积
    'orientation',     # 朝向
    'bedrooms',        # 卧室数
    'living_rooms',    # 客厅数
    'bathrooms',       # 卫生间数
    'floor_level',     # 楼层位置
    'total_floors',    # 总楼层
    'tags',            # 标签
    'platform',        # 发布平台
    'price'            # 价格
]