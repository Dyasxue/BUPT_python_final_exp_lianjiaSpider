"""
运行链家爬虫的脚本

支持两种使用方式：
1. 交互式输入（推荐）：
   python scripts/run_scraper.py          # 运行后提示输入页数范围

2. 命令行参数：
   python scripts/run_scraper.py 50       # 爬取前50页
   python scripts/run_scraper.py 1 50     # 爬取第1页到第50页
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.scraper import LianjiaSpider

def get_page_range_interactive():
    """获取用户输入的页数范围"""
    print("\n=== 链家北京租房数据爬虫 ===")
    print("请输入要爬取的页数范围：")

    while True:
        try:
            # 获取起始页数
            start_input = input("请输入起始页数 (默认: 1): ").strip()
            start_page = int(start_input) if start_input else 1

            # 获取结束页数
            end_input = input("请输入结束页数: ").strip()
            if not end_input:
                print("错误：结束页数不能为空")
                continue

            end_page = int(end_input)

            # 验证输入
            if start_page < 1:
                print("错误：起始页数必须大于0")
                continue
            if end_page < start_page:
                print("错误：结束页数必须大于等于起始页数")
                continue

            return start_page, end_page

        except ValueError:
            print("错误：请输入有效的整数")
        except KeyboardInterrupt:
            print("\n\n用户取消操作")
            return None, None

def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) == 1:
        # 没有参数时进入交互式输入模式
        start_page, end_page = get_page_range_interactive()
        if start_page is None or end_page is None:
            return
    else:
        # 有命令行参数时的处理
        start_page = 1
        end_page = 10  # 默认爬取前10页

        if len(sys.argv) == 2:
            # 单个参数：爬取前N页
            try:
                end_page = int(sys.argv[1])
            except ValueError:
                print("错误：页数参数必须是整数")
                return
        elif len(sys.argv) == 3:
            # 两个参数：爬取指定区间
            try:
                start_page = int(sys.argv[1])
                end_page = int(sys.argv[2])
                if start_page > end_page or start_page < 1:
                    print("错误：起始页数必须小于等于结束页数，且起始页数必须大于0")
                    return
            except ValueError:
                print("错误：页数参数必须是整数")
                return

    # 显示爬取信息
    print(f"\n开始爬取第 {start_page} 页到第 {end_page} 页...")
    print(f"预计爬取页数: {end_page - start_page + 1} 页")
    print("-" * 50)

    # 创建爬虫实例
    spider = LianjiaSpider()

    # 爬取数据
    listings = spider.scrape_page_range(start_page, end_page)

    # 保存数据
    if listings:
        filepath = spider.save_to_csv(listings, append=True)

        # 显示数据概览
        print("\n=== 数据概览 ===")
        print(f"总记录数: {len(listings)}")

        # 简单的统计
        prices = [item['price'] for item in listings if item.get('price', 0) > 0]
        if prices:
            print(f"平均价格: ¥{sum(prices)/len(prices):.0f}")
            print(f"最低价格: ¥{min(prices):.0f}")
            print(f"最高价格: ¥{max(prices):.0f}")
        areas = [item['area'] for item in listings if item.get('area', 0) > 0]
        if areas:
            print(f"平均面积: {sum(areas)/len(areas):.1f}㎡")
        districts = {}
        for item in listings:
            district = item.get('district', '未知')
            districts[district] = districts.get(district, 0) + 1

        print(f"区域分布: {dict(sorted(districts.items(), key=lambda x: x[1], reverse=True)[:5])}")

        print(f"\n数据已保存到: {filepath}")
        print("爬取完成！")
    else:
        print("没有获取到任何数据")

if __name__ == "__main__":
    main()
