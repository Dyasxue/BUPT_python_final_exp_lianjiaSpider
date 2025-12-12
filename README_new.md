# 链家租房数据爬虫和分析系统

一个用于爬取链家北京租房数据并进行分析的Python项目。

## 项目结构

```
rental-scraper/
├── src/                          # 源代码目录
│   ├── scraper/                  # 爬虫模块
│   │   ├── __init__.py
│   │   └── spider.py             # 主爬虫类
│   ├── analysis/                 # 数据分析模块
│   │   ├── __init__.py
│   │   ├── layout_analyzer.py    # 户型分析
│   │   └── rent_analyzer.py      # 租金分析
│   └── utils/                    # 工具模块
│       ├── __init__.py
│       └── data_processor.py     # 数据处理工具
├── config/                       # 配置文件
│   ├── __init__.py
│   └── settings.py               # 项目配置
├── scripts/                      # 运行脚本
│   ├── run_scraper.py            # 运行爬虫
│   ├── run_layout_analysis.py    # 运行户型分析
│   └── run_rent_analysis.py      # 运行租金分析
├── data/                         # 数据文件目录
├── logs/                         # 日志文件
├── reports/                      # 分析报告和图表
└── requirements.txt              # 依赖包列表
```

## 功能特性

- 🕷️ **数据爬取**: 自动爬取链家北京租房数据
- 📊 **数据分析**: 提供租金和户型等多维度分析
- 📈 **可视化**: 生成丰富的图表和统计报告
- 🛠️ **模块化**: 清晰的代码结构，易于维护和扩展

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行爬虫

```bash
python scripts/run_scraper.py          # 爬取前10页
python scripts/run_scraper.py 50       # 爬取前50页
python scripts/run_scraper.py 1 50     # 爬取第1页到第50页
```

### 3. 数据分析

```bash
python scripts/run_layout_analysis.py  # 户型分析
python scripts/run_rent_analysis.py    # 租金分析
```

## 使用说明

### 爬虫模块

位于 `src/scraper/spider.py`，主要类：
- `LianjiaSpider`: 链家数据爬虫主类

### 分析模块

#### 户型分析 (`src/analysis/layout_analyzer.py`)
- 分析不同户型（一居、二居、三居等）的分布情况
- 生成户型统计图表和报告

#### 租金分析 (`src/analysis/rent_analyzer.py`)
- 分析租金分布和统计特征
- 生成租金趋势图表和报告

### 配置说明

项目配置位于 `config/settings.py`，包含：
- 爬虫参数（请求超时、延迟等）
- 用户代理和Cookie设置
- 输出路径配置

## 数据格式

爬取的数据字段包括：
- 基本信息：标题、出租方式、区域信息
- 房源详情：面积、朝向、户型、楼层
- 价格信息：租金价格
- 其他：标签、平台信息等

## 注意事项

1. 使用前请确保网络连接正常
2. 爬取过程中请遵守网站robots.txt和相关法律法规
3. 建议使用代理IP以避免被限制
4. 数据仅供学习和研究使用

## 许可证

本项目仅供学习使用，请勿用于商业用途。