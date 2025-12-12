"""
链家北京租房数据爬虫
"""

import requests
import time
import random
import pandas as pd
from bs4 import BeautifulSoup
import re
import os
from config.settings import COOKIE_STRING, USER_AGENT, MAX_PAGES, REQUEST_TIMEOUT, DELAY_MIN, DELAY_MAX, OUTPUT_DIR, OUTPUT_FILENAME_PREFIX, DATA_FIELDS

class LianjiaSpider:
    def __init__(self, cookie_string=None):
        self.session = requests.Session()

        # 使用传入的cookie或配置文件中的cookie
        self.cookie_string = cookie_string or COOKIE_STRING

        # 设置请求头（不在这里设置Cookie，会在update_cookies中设置）
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

        # 设置cookies
        self.update_cookies()

    def parse_cookie_string(self, cookie_string):
        """解析cookie字符串为字典"""
        cookies = {}
        if cookie_string:
            pairs = cookie_string.split(';')
            for pair in pairs:
                pair = pair.strip()
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    cookies[key.strip()] = value.strip()
        return cookies

    def set_cookies_from_string(self, cookie_string):
        """从字符串设置cookies"""
        cookies = self.parse_cookie_string(cookie_string)
        for key, value in cookies.items():
            self.session.cookies.set(key, value)

    def update_cookies(self, cookie_string=None):
        """更新cookies"""
        if cookie_string:
            self.cookie_string = cookie_string
            self.set_cookies_from_string(cookie_string)
        else:
            self.set_cookies_from_string(self.cookie_string)

    def get_random_delay(self):
        """随机延迟"""
        return random.uniform(DELAY_MIN, DELAY_MAX)

    def parse_listing(self, item_div):
        """解析单个房源信息"""
        try:
            listing = {}

            # 1. 房源基本信息（大标题）
            title_elem = item_div.find('p', class_='content__list--item--title')
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                listing['title'] = title_text

                # 解析出租方式
                if '整租' in title_text:
                    listing['rent_type'] = '整租'
                elif '合租' in title_text:
                    listing['rent_type'] = '合租'
                else:
                    listing['rent_type'] = '其他'

            # 2. URL (不再保存)
            # url_elem = item_div.find('a', class_='content__list--item--aside')
            # if url_elem and url_elem.get('href'):
            #     listing['url'] = 'https://bj.lianjia.com' + url_elem['href']

            # 3. 区域信息和详细参数
            des_elem = item_div.find('p', class_='content__list--item--des')
            if des_elem:
                des_text = des_elem.get_text(strip=True)

                # 解析区域信息
                area_links = des_elem.find_all('a')
                if len(area_links) >= 3:
                    listing['district'] = area_links[0].get_text(strip=True)  # 区域
                    listing['sub_district'] = area_links[1].get_text(strip=True)  # 子区域
                    listing['community'] = area_links[2].get_text(strip=True)  # 小区

                # 解析面积
                area_match = re.search(r'(\d+\.?\d*)㎡', des_text)
                if area_match:
                    listing['area'] = float(area_match.group(1))

                # 解析朝向
                orientation_match = re.search(r'/([^/]*?)/', des_text)
                if orientation_match:
                    listing['orientation'] = orientation_match.group(1).strip()

                # 解析户型
                layout_match = re.search(r'(\d+)室(\d+)厅(\d+)卫', des_text)
                if layout_match:
                    listing['bedrooms'] = int(layout_match.group(1))
                    listing['living_rooms'] = int(layout_match.group(2))
                    listing['bathrooms'] = int(layout_match.group(3))

                # 解析楼层信息（在隐藏的span中）
                hide_elem = des_elem.find('span', class_='hide')
                if hide_elem:
                    hide_text = hide_elem.get_text(strip=True)
                    floor_match = re.search(r'(\w+)楼层.*?\((\d+)层\)', hide_text)
                    if floor_match:
                        listing['floor_level'] = floor_match.group(1)
                        listing['total_floors'] = int(floor_match.group(2))

            # 4. 标签信息
            bottom_elem = item_div.find('p', class_='content__list--item--bottom')
            if bottom_elem:
                tags = []
                tag_elems = bottom_elem.find_all('i')
                for tag_elem in tag_elems:
                    tag_text = tag_elem.get_text(strip=True)
                    if tag_text:
                        tags.append(tag_text)
                listing['tags'] = '|'.join(tags)

            # 5. 来源（发布平台）
            brand_elem = item_div.find('p', class_='content__list--item--brand')
            if brand_elem:
                brand_span = brand_elem.find('span', class_='brand')
                if brand_span:
                    listing['platform'] = brand_span.get_text(strip=True)
                else:
                    listing['platform'] = brand_elem.get_text(strip=True)

            # 6. 金额
            price_elem = item_div.find('span', class_='content__list--item-price')
            if price_elem:
                em_elem = price_elem.find('em')
                if em_elem:
                    price_text = em_elem.get_text(strip=True)
                    try:
                        listing['price'] = int(price_text)
                    except ValueError:
                        listing['price'] = 0

            # 添加抓取时间 (不再保存)
            # listing['scrape_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            return listing

        except Exception as e:
            print(f"解析房源信息失败: {e}")
            return None

    def scrape_page(self, page_num):
        """爬取单页数据"""
        url = f"https://bj.lianjia.com/zufang/pg{page_num}/"

        try:
            # 使用指定的User-Agent
            self.session.headers.update({'User-Agent': USER_AGENT})

            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 查找房源列表
            list_container = soup.find('div', class_='content__list')
            if not list_container:
                print(f"第{page_num}页未找到房源列表")
                return []

            listings = list_container.find_all('div', class_='content__list--item')

            if not listings:
                print(f"第{page_num}页没有房源数据，可能已到最后一页")
                return []

            parsed_listings = []
            for item in listings:
                parsed = self.parse_listing(item)
                if parsed:
                    parsed_listings.append(parsed)

            print(f"第{page_num}页成功解析 {len(parsed_listings)} 条房源")
            return parsed_listings

        except requests.RequestException as e:
            print(f"请求第{page_num}页失败: {e}")
            return []
        except Exception as e:
            print(f"处理第{page_num}页时发生错误: {e}")
            return []

    def scrape_all(self, max_pages=None):
        """爬取所有页面数据"""
        return self.scrape_page_range(1, max_pages or MAX_PAGES)

    def scrape_page_range(self, start_page, end_page):
        """爬取指定页面区间的数据"""
        all_listings = []
        skipped_pages = []
        total_pages = end_page - start_page + 1

        print(f"开始爬取链家北京租房数据，第{start_page}页到第{end_page}页...")

        consecutive_empty_pages = 0
        max_consecutive_empty = 3  # 连续3页空页面就停止

        for page_num in range(start_page, end_page + 1):
            print(f"正在爬取第{page_num}页...")
            listings = self.scrape_page(page_num)

            if not listings:
                consecutive_empty_pages += 1
                skipped_pages.append(page_num)
                print(f"第{page_num}页没有数据 (连续空页: {consecutive_empty_pages})")
                if consecutive_empty_pages >= max_consecutive_empty:
                    print(f"连续{max_consecutive_empty}页都没有数据，停止爬取")
                    break
                # 跳过这个页面，继续下一个
                continue
            else:
                consecutive_empty_pages = 0  # 重置计数器

            all_listings.extend(listings)

            # 随机延迟
            time.sleep(self.get_random_delay())

        print(f"共获取 {len(all_listings)} 条房源数据")

        # 保存跳过页面信息
        if skipped_pages:
            self.save_skipped_pages(skipped_pages)

        return all_listings

    def save_skipped_pages(self, skipped_pages):
        """保存跳过页面信息"""
        if not skipped_pages:
            return

        filename = f"{OUTPUT_FILENAME_PREFIX}_skipped_pages.txt"

        # 确保输出目录存在
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filepath = os.path.join(OUTPUT_DIR, filename)

        # 追加写入跳过的页数
        with open(filepath, 'a', encoding='utf-8') as f:
            for page_num in skipped_pages:
                f.write(f"{page_num}\n")

        print(f"跳过页面信息已保存: {filepath} (本次跳过 {len(skipped_pages)} 页)")

    def save_to_csv(self, listings, filename=None, append=False):
        """保存数据到CSV文件"""
        if not listings:
            return

        if filename is None:
            filename = f"{OUTPUT_FILENAME_PREFIX}.csv"

        df = pd.DataFrame(listings)

        # 确保输出目录存在
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filepath = os.path.join(OUTPUT_DIR, filename)

        # 如果是追加模式且文件已存在，则读取现有数据并追加
        if append and os.path.exists(filepath):
            try:
                existing_df = pd.read_csv(filepath, encoding='utf-8-sig')
                df = pd.concat([existing_df, df], ignore_index=True)
                print(f"追加数据到现有文件: {filepath}")
            except Exception as e:
                print(f"读取现有文件失败，将创建新文件: {e}")

        # 保存数据
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"数据已保存到: {filepath} (共{len(df)}条记录)")
        return filepath

def main():
    """主函数"""
    spider = LianjiaSpider()

    # 爬取数据
    listings = spider.scrape_all(max_pages=50)  # 先爬取50页测试

    # 保存数据
    if listings:
        filepath = spider.save_to_csv(listings)
        print("爬取完成！")

        # 显示数据概览
        df = pd.DataFrame(listings)
        print("\n数据概览:")
        print(f"总记录数: {len(df)}")
        print(f"平均价格: ¥{df['price'].mean():.0f}")
        print(f"平均面积: {df['area'].mean():.1f}㎡")
        print(f"主要区域: {df['district'].value_counts().head(5).to_dict()}")

if __name__ == "__main__":
    main()
