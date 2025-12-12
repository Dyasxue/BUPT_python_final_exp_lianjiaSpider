"""
链家租房数据爬虫
"""

import requests
import time
import random
import json
import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tqdm import tqdm
import logging
from datetime import datetime
import re
import os
from config import CITIES, SCRAPER_CONFIG, DATA_FIELDS

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LianjiaScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def get_random_delay(self):
        """随机延迟"""
        return random.uniform(1, 3)

    def parse_listing(self, soup, city_code):
        """解析单个房源信息"""
        try:
            listing = {}

            # 基本信息
            title_elem = soup.find('p', class_='content__title')
            listing['title'] = title_elem.get_text(strip=True) if title_elem else ''

            # 价格信息
            price_elem = soup.find('p', class_='content__list--item-price')
            if price_elem:
                price_text = price_elem.find('em').get_text(strip=True) if price_elem.find('em') else ''
                listing['price'] = int(re.findall(r'\d+', price_text)[0]) if re.findall(r'\d+', price_text) else 0

                # 单位面积租金
                price_per_sqm_elem = price_elem.find('i')
                if price_per_sqm_elem:
                    price_per_sqm_text = price_per_sqm_elem.get_text(strip=True)
                    listing['price_per_sqm'] = float(re.findall(r'\d+\.?\d*', price_per_sqm_text)[0]) if re.findall(r'\d+\.?\d*', price_per_sqm_text) else 0

            # 面积
            area_elem = soup.find('p', class_='content__list--item--des')
            if area_elem:
                area_text = area_elem.get_text(strip=True)
                area_match = re.search(r'(\d+\.?\d*)㎡', area_text)
                listing['area'] = float(area_match.group(1)) if area_match else 0

            # 户型信息
            layout_text = area_elem.get_text(strip=True) if area_elem else ''
            bedroom_match = re.search(r'(\d+)室', layout_text)
            living_match = re.search(r'(\d+)厅', layout_text)
            bathroom_match = re.search(r'(\d+)卫', layout_text)

            listing['bedrooms'] = int(bedroom_match.group(1)) if bedroom_match else 0
            listing['living_rooms'] = int(living_match.group(1)) if living_match else 0
            listing['bathrooms'] = int(bathroom_match.group(1)) if bathroom_match else 0

            # 楼层信息
            floor_elem = soup.find('p', class_='content__list--item--floor')
            if floor_elem:
                floor_text = floor_elem.get_text(strip=True)
                floor_match = re.search(r'(\d+)/(\d+)', floor_text)
                if floor_match:
                    listing['floor'] = int(floor_match.group(1))
                    listing['total_floors'] = int(floor_match.group(2))
                else:
                    listing['floor'] = 0
                    listing['total_floors'] = 0

            # 朝向
            orientation_elem = soup.find('p', class_='content__list--item--direction')
            listing['orientation'] = orientation_elem.get_text(strip=True) if orientation_elem else ''

            # 区域信息
            district_elem = soup.find('p', class_='content__list--item--area')
            if district_elem:
                district_text = district_elem.get_text(strip=True)
                parts = district_text.split('·')
                listing['district'] = parts[0].strip() if len(parts) > 0 else ''
                listing['subway'] = '有' in district_text if '地铁' in district_text or '近地铁' in district_text else False

            # 中介信息
            agency_elem = soup.find('p', class_='content__list--item--brand')
            listing['agency'] = agency_elem.get_text(strip=True) if agency_elem else '个人'

            # URL
            url_elem = soup.find('a', class_='content__list--item--aside')
            listing['url'] = 'https://' + city_code + '.lianjia.com' + url_elem['href'] if url_elem else ''

            # 元数据
            listing['city'] = CITIES[city_code]['name']
            listing['scrape_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            return listing

        except Exception as e:
            logger.error(f"解析房源信息失败: {e}")
            return None

    def scrape_city_page(self, city_code, page_num):
        """爬取单个城市单页数据"""
        url = f"https://{city_code}.lianjia.com/zufang/pg{page_num}/"
        max_retries = SCRAPER_CONFIG['max_retries']

        for attempt in range(max_retries):
            try:
                # 更新User-Agent
                self.session.headers.update({'User-Agent': self.ua.random})

                response = self.session.get(url, timeout=SCRAPER_CONFIG['request_timeout'])
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                # 检查是否被反爬
                if 'verify' in response.url or 'antibot' in response.text.lower():
                    logger.warning(f"触发反爬机制，等待重试... 尝试 {attempt + 1}/{max_retries}")
                    time.sleep(10 * (attempt + 1))
                    continue

                # 解析房源列表
                listings = soup.find_all('div', class_='content__list--item')

                if not listings:
                    logger.info(f"第{page_num}页没有找到房源，可能已到最后一页")
                    return []

                parsed_listings = []
                for listing in listings:
                    parsed = self.parse_listing(listing, city_code)
                    if parsed:
                        parsed_listings.append(parsed)

                logger.info(f"成功解析第{page_num}页，共{len(parsed_listings)}条房源")
                return parsed_listings

            except requests.RequestException as e:
                logger.error(f"请求失败: {e}，尝试 {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))
                continue

        logger.error(f"爬取第{page_num}页失败，已达到最大重试次数")
        return []

    def scrape_city(self, city_code, max_pages=None):
        """爬取单个城市全部数据"""
        city_info = CITIES[city_code]
        logger.info(f"开始爬取城市: {city_info['name']}")

        all_listings = []
        page_num = 1

        # 如果没有指定最大页数，根据最小记录数估算
        if max_pages is None:
            estimated_pages = max(city_info['min_records'] // 30 + 10, 50)  # 每页约30条，预留余量
        else:
            max_pages = estimated_pages

        with tqdm(total=estimated_pages, desc=f"爬取{city_info['name']}") as pbar:
            while page_num <= estimated_pages:
                if len(all_listings) >= city_info['min_records']:
                    logger.info(f"已达到最小记录数要求: {len(all_listings)}条")
                    break

                listings = self.scrape_city_page(city_code, page_num)
                if not listings:
                    break

                all_listings.extend(listings)
                page_num += 1
                pbar.update(1)

                # 随机延迟
                time.sleep(self.get_random_delay())

        logger.info(f"城市{city_info['name']}爬取完成，共获取{len(all_listings)}条数据")
        return all_listings

    def save_to_csv(self, listings, city_code):
        """保存数据到CSV文件"""
        if not listings:
            return

        df = pd.DataFrame(listings)
        output_path = f"data/raw/{city_code}_rentals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"数据已保存到: {output_path}")
        return output_path

def main():
    """主函数"""
    scraper = LianjiaScraper()

    for city_code in CITIES.keys():
        try:
            logger.info(f"开始处理城市: {CITIES[city_code]['name']}")
            listings = scraper.scrape_city(city_code)
            scraper.save_to_csv(listings, city_code)

        except Exception as e:
            logger.error(f"处理城市 {CITIES[city_code]['name']} 时发生错误: {e}")
            continue

if __name__ == "__main__":
    main()
