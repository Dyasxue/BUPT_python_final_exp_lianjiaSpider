"""
链家爬虫配置文件
"""

# Cookie配置
COOKIE_STRING = 'lianjia_uuid=1f2749a3-4175-4dfa-bc32-2405d01a4a2a; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2219ab9852fe51a57-06aa525651597e8-26061b51-1821369-19ab9852fe62e82%22%2C%22%24device_id%22%3A%2219ab9852fe51a57-06aa525651597e8-26061b51-1821369-19ab9852fe62e82%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; _ga=GA1.2.1607223827.1764049116; crosSdkDT2019DeviceId=-hxgzup--1vlpj0-k6eu38qpioht4f3-sowkgwf9t; _ga_KJTRWRHDL1=GS2.2.s1764069753$o2$g1$t1764070765$j60$l0$h0; _ga_QJN1VP0CMS=GS2.2.s1764069753$o2$g1$t1764070765$j60$l0$h0; ftkrc_=3bed6966-45d3-4fb5-bb32-67718e5e2a74; lfrc_=a6f71c05-6e30-4978-b54f-04f244605256; Hm_lvt_efa595b768cc9dc7d7f9823368e795f1=1765343725; _jzqa=1.1607214649468784000.1764049105.1764140241.1765343904.5; _jzqx=1.1764140241.1765343904.2.jzqsr=bj%2Elianjia%2Ecom|jzqct=/ershoufang/pg1/.jzqsr=user%2Elianjia%2Ecom|jzqct=/; login_ucid=2000000516222564; lianjia_token=2.00140854504f4fd7d805a57d61232ffad1; lianjia_token_secure=2.00140854504f4fd7d805a57d61232ffad1; security_ticket=cD36bO+T3zZPYas6cGLYew7VflFFoyM4MVrdxet8LIW8jMEza0fLUZ2laeX8qRvWYICjM8DZTfw2KDG82TKP0iCH4WaN/kn9KvZBMC62ZE3f7ztNNXdG8V6h4XAnEmMCNLcIxJWxQTGJ19R4eGa2y2F6AI/dhblOZpBSoDXTeLM=; select_city=110000; lianjia_ssid=8571687f-0a31-41a4-9f99-7c1a7d114a5c; Hm_lvt_46bf127ac9b856df503ec2dbf942b67e=1765152013,1765325679,1765356945,1765450369; Hm_lpvt_46bf127ac9b856df503ec2dbf942b67e=1765450369; HMACCOUNT=3FF3F9AD80E0BF18; _gid=GA1.2.1052196573.1765450369; _ga_RCTBRFLNVS=GS2.2.s1765458093$o8$g0$t1765458093$j60$l0$h0; hip=M9wybmYz1AVybU5jnmmeaP2mjouYU6S7MNAqoaEZjrMIARO5gGDRAIakFGsWVmgLPj2z6oyksj3CFw6yp2KSjD5b8sNAP2jlRb6Y8JI7vWbzqKFSRkZw7g9pI269T4WvCdWaoOrAh2rRF_aVgIWmtVgFbzpfr2nQRiCy_HWtxpDlIIqYnMrAHCXux6JN3ZP-aB7vzwro7x66w_Mtwhhzv8Q8yhornz6XfSxCPymoUZioNtHZcTIgoCEbv7Aq44w8k7JlWXgAF7yyA4041KAPC0e4DGgrghLhObBCGQ%3D%3D'

# User-Agent配置
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'

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
