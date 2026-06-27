---
title: Python爬虫实战
aliases:
  - Python爬虫实战
  - Web Scraping
tags:
  - python
  - scraping
  - web
  - requests
  - beautifulsoup
  - scrapy
  - anti-crawling
type: wiki
status: published
created: 2026-06-28
updated: 2026-06-28
source: ""
difficulty: advanced
project: AI-Agent
---

# Python爬虫实战

Python是网络爬虫开发的首选语言，拥有丰富的库和框架支持。本页面涵盖从基础请求到高级反爬策略的完整实战指南。

## 1. requests库基础

### 1.1 基本请求方法

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json

# 基本GET请求
def basic_get_request():
    url = "https://httpbin.org/get"
    response = requests.get(url)
    
    print(f"状态码: {response.status_code}")
    print(f"响应头: {response.headers}")
    print(f"内容: {response.json()}")
    
    return response

# 带参数的GET请求
def get_with_params():
    url = "https://httpbin.org/get"
    params = {
        'key1': 'value1',
        'key2': 'value2',
        'page': 1,
        'limit': 10
    }
    
    response = requests.get(url, params=params)
    print(f"完整URL: {response.url}")
    return response

# POST请求
def post_request():
    url = "https://httpbin.org/post"
    
    # 表单数据
    data = {
        'username': 'testuser',
        'password': 'testpass'
    }
    
    # JSON数据
    json_data = {
        'name': 'John',
        'age': 30,
        'city': 'Beijing'
    }
    
    # 发送表单数据
    response_form = requests.post(url, data=data)
    
    # 发送JSON数据
    response_json = requests.post(url, json=json_data)
    
    return response_form, response_json

# 带重试机制的会话
def create_session_with_retry():
    session = requests.Session()
    
    # 配置重试策略
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # 设置默认headers
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    })
    
    return session

# 使用会话
def use_session():
    session = create_session_with_retry()
    
    try:
        response = session.get('https://httpbin.org/get', timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None
    finally:
        session.close()
```

### 1.2 高级请求技巧

```python
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import base64

# 文件上传
def upload_file():
    url = "https://httpbin.org/post"
    
    # 单文件上传
    with open('file.txt', 'rb') as f:
        files = {'file': ('file.txt', f, 'text/plain')}
        response = requests.post(url, files=files)
    
    # 多文件上传
    files = [
        ('files', ('file1.txt', open('file1.txt', 'rb'), 'text/plain')),
        ('files', ('file2.txt', open('file2.txt', 'rb'), 'text/plain'))
    ]
    response = requests.post(url, files=files)
    
    return response

# 认证请求
def authenticated_request():
    url = "https://httpbin.org/basic-auth/user/passwd"
    
    # Basic认证
    response = requests.get(url, auth=HTTPBasicAuth('user', 'passwd'))
    
    # Digest认证
    response = requests.get(url, auth=HTTPDigestAuth('user', 'passwd'))
    
    # 自定义认证头
    headers = {
        'Authorization': 'Bearer your_token_here'
    }
    response = requests.get(url, headers=headers)
    
    return response

# 代理设置
def use_proxy():
    url = "https://httpbin.org/ip"
    
    proxies = {
        'http': 'http://proxy.example.com:8080',
        'https': 'https://proxy.example.com:8080'
    }
    
    # 使用代理
    response = requests.get(url, proxies=proxies, timeout=10)
    
    # 使用SOCKS代理
    # pip install requests[socks]
    socks_proxies = {
        'http': 'socks5://proxy.example.com:1080',
        'https': 'socks5://proxy.example.com:1080'
    }
    response = requests.get(url, proxies=socks_proxies)
    
    return response

# 流式下载大文件
def download_large_file(url, filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"文件下载完成: {filename}")

# 并发请求
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def fetch_url(url):
    """获取单个URL"""
    try:
        response = requests.get(url, timeout=10)
        return url, response.status_code, len(response.content)
    except Exception as e:
        return url, str(e), 0

def concurrent_requests(urls, max_workers=5):
    """并发请求多个URL"""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(fetch_url, url): url for url in urls}
        
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                results.append(result)
                print(f"完成: {url} - 状态: {result[1]}")
            except Exception as e:
                print(f"错误: {url} - {e}")
    
    return results
```

## 2. BeautifulSoup解析

### 2.1 HTML解析基础

```python
from bs4 import BeautifulSoup
import re

# 基本解析
def parse_html(html_content):
    """解析HTML内容"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 获取标题
    title = soup.title.string if soup.title else "无标题"
    
    # 获取所有链接
    links = []
    for link in soup.find_all('a', href=True):
        links.append({
            'text': link.get_text(strip=True),
            'href': link['href']
        })
    
    # 获取所有图片
    images = []
    for img in soup.find_all('img', src=True):
        images.append({
            'alt': img.get('alt', ''),
            'src': img['src']
        })
    
    return {
        'title': title,
        'links': links,
        'images': images
    }

# CSS选择器
def css_selectors_example():
    """CSS选择器示例"""
    html = """
    <html>
    <body>
        <div class="container">
            <h1 id="title">标题</h1>
            <p class="content">段落1</p>
            <p class="content">段落2</p>
            <ul>
                <li class="item">项目1</li>
                <li class="item">项目2</li>
                <li class="item">项目3</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # ID选择器
    title = soup.select_one('#title').text
    
    # 类选择器
    paragraphs = [p.text for p in soup.select('.content')]
    
    # 组合选择器
    items = [li.text for li in soup.select('ul li.item')]
    
    # 属性选择器
    elements = soup.select('[class="content"]')
    
    return {
        'title': title,
        'paragraphs': paragraphs,
        'items': items
    }

# 正则表达式配合使用
def regex_with_bs4():
    """正则表达式配合BeautifulSoup"""
    html = """
    <div>
        <p>电话: 13800138000</p>
        <p>邮箱: test@example.com</p>
        <p>日期: 2026-06-28</p>
    </div>
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # 使用正则表达式查找
    phone_pattern = re.compile(r'1[3-9]\d{9}')
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
    
    text = soup.get_text()
    
    phones = phone_pattern.findall(text)
    emails = email_pattern.findall(text)
    dates = date_pattern.findall(text)
    
    return {
        'phones': phones,
        'emails': emails,
        'dates': dates
    }

# 表格数据提取
def extract_table_data(html):
    """提取表格数据"""
    soup = BeautifulSoup(html, 'html.parser')
    
    tables = []
    for table in soup.find_all('table'):
        rows = []
        for tr in table.find_all('tr'):
            cells = []
            for td in tr.find_all(['td', 'th']):
                cells.append(td.get_text(strip=True))
            rows.append(cells)
        tables.append(rows)
    
    return tables

# 清理HTML
def clean_html(html):
    """清理HTML，移除脚本和样式"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # 移除script和style标签
    for script in soup(["script", "style"]):
        script.decompose()
    
    # 获取纯文本
    text = soup.get_text()
    
    # 清理多余空白
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    return text
```

### 2.2 lxml解析器

```python
from lxml import html, etree
import requests

def parse_with_lxml(url):
    """使用lxml解析网页"""
    response = requests.get(url)
    tree = html.fromstring(response.content)
    
    # XPath选择
    titles = tree.xpath('//h1/text()')
    links = tree.xpath('//a/@href')
    images = tree.xpath('//img/@src')
    
    # 复杂XPath
    items = tree.xpath('//div[@class="item"]//text()')
    
    return {
        'titles': titles,
        'links': links,
        'images': images,
        'items': items
    }

def extract_structured_data(html_content):
    """提取结构化数据"""
    tree = html.fromstring(html_content)
    
    # 提取表格数据
    table_data = []
    rows = tree.xpath('//table//tr')
    for row in rows:
        cells = row.xpath('.//td/text() | .//th/text()')
        table_data.append(cells)
    
    # 提取列表数据
    list_items = tree.xpath('//ul/li/text()')
    
    # 提取属性值
    data_attrs = tree.xpath('//div[@data-id]/@data-id')
    
    return {
        'table': table_data,
        'list': list_items,
        'attrs': data_attrs
    }
```

## 3. Scrapy框架

### 3.1 Scrapy项目结构

```python
# 项目结构示例
"""
myproject/
    scrapy.cfg
    myproject/
        __init__.py
        items.py
        middlewares.py
        pipelines.py
        settings.py
        spiders/
            __init__.py
            example_spider.py
"""

# items.py - 定义数据结构
import scrapy

class ProductItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    category = scrapy.Field()
    url = scrapy.Field()
    image_url = scrapy.Field()
    timestamp = scrapy.Field()

# spiders/example_spider.py
import scrapy
from myproject.items import ProductItem

class ExampleSpider(scrapy.Spider):
    name = 'example'
    allowed_domains = ['example.com']
    start_urls = ['http://example.com/products']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 5,
        'ROBOTSTXT_OBEY': True,
    }
    
    def parse(self, response):
        # 解析产品列表
        for product in response.css('.product-item'):
            item = ProductItem()
            item['name'] = product.css('.name::text').get()
            item['price'] = product.css('.price::text').get()
            item['url'] = product.css('a::attr(href)').get()
            
            # 跟进详情页
            yield response.follow(
                product.css('a::attr(href)').get(),
                callback=self.parse_detail,
                meta={'item': item}
            )
        
        # 分页处理
        next_page = response.css('.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
    
    def parse_detail(self, response):
        item = response.meta['item']
        item['description'] = response.css('.description::text').get()
        item['category'] = response.css('.category::text').get()
        item['image_url'] = response.css('.product-image img::attr(src)').get()
        
        yield item

# pipelines.py - 数据处理管道
import sqlite3
from datetime import datetime

class SQLitePipeline:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def open_spider(self, spider):
        self.connection = sqlite3.connect('products.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                price REAL,
                description TEXT,
                category TEXT,
                url TEXT UNIQUE,
                image_url TEXT,
                timestamp DATETIME
            )
        ''')
        self.connection.commit()
    
    def process_item(self, item, spider):
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO products 
                (name, price, description, category, url, image_url, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.get('name'),
                float(item.get('price', 0)),
                item.get('description'),
                item.get('category'),
                item.get('url'),
                item.get('image_url'),
                datetime.now()
            ))
            self.connection.commit()
        except Exception as e:
            spider.logger.error(f"Error processing item: {e}")
        
        return item
    
    def close_spider(self, spider):
        self.connection.close()

# settings.py - 配置文件
BOT_NAME = 'myproject'
SPIDER_MODULES = ['myproject.spiders']
NEWSPIDER_MODULE = 'myproject.spiders'

# 遵守robots.txt
ROBOTSTXT_OBEY = True

# 下载延迟
DOWNLOAD_DELAY = 1

# 并发请求
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8

# User-Agent
USER_AGENT = 'myproject (+http://www.yourdomain.com)'

# 中间件
DOWNLOADER_MIDDLEWARES = {
    'myproject.middlewares.RandomUserAgentMiddleware': 400,
    'myproject.middlewares.ProxyMiddleware': 410,
}

# 管道
ITEM_PIPELINES = {
    'myproject.pipelines.SQLitePipeline': 300,
    'myproject.pipelines.CleanPipeline': 310,
}

# 缓存
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400
HTTPCACHE_DIR = 'httpcache'

# 日志
LOG_LEVEL = 'INFO'
LOG_FILE = 'scrapy.log'
```

### 3.2 Scrapy中间件

```python
# middlewares.py
import random
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware

class RandomUserAgentMiddleware:
    """随机User-Agent中间件"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
        'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
    ]
    
    def process_request(self, request, spider):
        user_agent = random.choice(self.USER_AGENTS)
        request.headers['User-Agent'] = user_agent
        return None

class ProxyMiddleware:
    """代理中间件"""
    
    PROXIES = [
        'http://proxy1.example.com:8080',
        'http://proxy2.example.com:8080',
        'http://proxy3.example.com:8080',
    ]
    
    def process_request(self, request, spider):
        proxy = random.choice(self.PROXIES)
        request.meta['proxy'] = proxy
        return None

class SmartRetryMiddleware(RetryMiddleware):
    """智能重试中间件"""
    
    def process_response(self, request, response, spider):
        if response.status in [403, 429]:
            # 被封禁或限流，更换代理和User-Agent
            request.headers['User-Agent'] = random.choice(
                RandomUserAgentMiddleware.USER_AGENTS
            )
            request.meta['proxy'] = random.choice(
                ProxyMiddleware.PROXIES
            )
            return self._retry(request, response.status, spider) or response
        
        return super().process_response(request, response, spider)

class SeleniumMiddleware:
    """Selenium中间件，处理JavaScript渲染"""
    
    def __init__(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=options)
    
    def process_request(self, request, spider):
        if request.meta.get('render_js'):
            self.driver.get(request.url)
            
            # 等待页面加载
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            from scrapy.http import HtmlResponse
            return HtmlResponse(
                request.url,
                body=self.driver.page_source,
                encoding='utf-8',
                request=request
            )
        
        return None
    
    def spider_closed(self, spider):
        self.driver.quit()
```

## 4. 反爬策略与应对

### 4.1 常见反爬技术

```python
import requests
import time
import random
from functools import wraps

class AntiCrawler:
    """反爬策略集合"""
    
    @staticmethod
    def random_delay(min_delay=1, max_delay=3):
        """随机延迟装饰器"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                delay = random.uniform(min_delay, max_delay)
                time.sleep(delay)
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def rotate_user_agents():
        """User-Agent轮换"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
        ]
        return random.choice(user_agents)
    
    @staticmethod
    def get_headers():
        """生成随机请求头"""
        headers = {
            'User-Agent': AntiCrawler.rotate_user_agents(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/',
        }
        return headers

class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(AntiCrawler.get_headers())
    
    def update_cookies(self, url):
        """更新cookies"""
        self.session.get(url)
        return self.session.cookies
    
    def request_with_retry(self, url, max_retries=3, **kwargs):
        """带重试的请求"""
        for attempt in range(max_retries):
            try:
                # 更新headers
                self.session.headers.update(AntiCrawler.get_headers())
                
                response = self.session.get(url, **kwargs)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 403:
                    print(f"请求被拒绝，尝试 {attempt + 1}/{max_retries}")
                    time.sleep(random.uniform(2, 5))
                elif response.status_code == 429:
                    print(f"请求过于频繁，等待后重试...")
                    time.sleep(random.uniform(5, 10))
                else:
                    print(f"请求失败: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"请求异常: {e}")
                time.sleep(random.uniform(1, 3))
        
        return None

# 使用示例
@AntiCrawler.random_delay(1, 3)
def crawl_page(url):
    """爬取单个页面"""
    session = SessionManager()
    response = session.request_with_retry(url)
    return response
```

### 4.2 验证码处理

```python
import ddddocr
from PIL import Image
import io
import base64

class CaptchaSolver:
    """验证码识别"""
    
    def __init__(self):
        self.ocr = ddddocr.DdddOcr()
    
    def recognize_text_captcha(self, image_path):
        """识别文字验证码"""
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        result = self.ocr.classification(image_bytes)
        return result
    
    def recognize_from_url(self, url):
        """从URL识别验证码"""
        response = requests.get(url)
        image_bytes = response.content
        
        result = self.ocr.classification(image_bytes)
        return result
    
    def recognize_base64(self, base64_string):
        """识别base64编码的验证码"""
        # 移除data:image/xxx;base64,前缀
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        image_bytes = base64.b64decode(base64_string)
        result = self.ocr.classification(image_bytes)
        return result

# 使用打码平台
class CaptchaPlatform:
    """第三方打码平台"""
    
    def __init__(self, api_key, platform='2captcha'):
        self.api_key = api_key
        self.platform = platform
    
    def solve_recaptcha_v2(self, site_key, page_url):
        """解决reCAPTCHA v2"""
        # 2captcha API
        if self.platform == '2captcha':
            # 提交任务
            submit_url = 'http://2captcha.com/in.php'
            data = {
                'key': self.api_key,
                'method': 'userrecaptcha',
                'googlekey': site_key,
                'pageurl': page_url,
                'json': 1
            }
            
            response = requests.post(submit_url, data=data)
            task_id = response.json().get('request')
            
            # 等待结果
            result_url = f'http://2captcha.com/res.php?key={self.api_key}&action=get&id={task_id}&json=1'
            
            for _ in range(30):  # 最多等待30秒
                time.sleep(1)
                result = requests.get(result_url).json()
                
                if result.get('status') == 1:
                    return result.get('request')
            
            return None
```

### 4.3 动态页面处理

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time

class SeleniumScraper:
    """Selenium爬虫"""
    
    def __init__(self, headless=True):
        self.options = Options()
        
        if headless:
            self.options.add_argument('--headless')
        
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=self.options)
        
        # 隐藏webdriver特征
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def get_page(self, url, wait_time=10):
        """获取页面"""
        self.driver.get(url)
        
        # 等待页面加载
        WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        return self.driver.page_source
    
    def scroll_to_bottom(self, scroll_pause_time=2):
        """滚动到页面底部"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # 滚动到页面底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # 等待页面加载
            time.sleep(scroll_pause_time)
            
            # 计算新的滚动高度
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            
            last_height = new_height
    
    def click_element(self, selector, by=By.CSS_SELECTOR):
        """点击元素"""
        element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((by, selector))
        )
        element.click()
        return element
    
    def input_text(self, selector, text, by=By.CSS_SELECTOR):
        """输入文本"""
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((by, selector))
        )
        element.clear()
        element.send_keys(text)
        return element
    
    def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """等待元素出现"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
    
    def execute_js(self, script):
        """执行JavaScript"""
        return self.driver.execute_script(script)
    
    def take_screenshot(self, filename):
        """截图"""
        self.driver.save_screenshot(filename)
    
    def close(self):
        """关闭浏览器"""
        self.driver.quit()

# 使用Playwright（更现代的方案）
"""
pip install playwright
playwright install
"""

from playwright.sync_api import sync_playwright

class PlaywrightScraper:
    """Playwright爬虫"""
    
    def __init__(self, headless=True):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.page = self.context.new_page()
    
    def get_page(self, url, wait_until='networkidle'):
        """获取页面"""
        self.page.goto(url, wait_until=wait_until)
        return self.page.content()
    
    def click(self, selector):
        """点击元素"""
        self.page.click(selector)
    
    def fill(self, selector, value):
        """填写表单"""
        self.page.fill(selector, value)
    
    def wait_for_selector(self, selector, timeout=30000):
        """等待选择器"""
        self.page.wait_for_selector(selector, timeout=timeout)
    
    def screenshot(self, path):
        """截图"""
        self.page.screenshot(path=path)
    
    def close(self):
        """关闭"""
        self.context.close()
        self.browser.close()
        self.playwright.stop()
```

## 5. 实战案例

### 5.1 电商网站爬虫

```python
import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join
import re

class EcommerceSpider(scrapy.Spider):
    name = 'ecommerce'
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 4,
        'ROBOTSTXT_OBEY': True,
        'FEEDS': {
            'products.json': {
                'format': 'json',
                'encoding': 'utf8',
                'indent': 4,
            },
        },
    }
    
    def start_requests(self):
        urls = [
            'https://www.example.com/category/electronics',
            'https://www.example.com/category/clothing',
        ]
        
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_category)
    
    def parse_category(self, response):
        """解析分类页面"""
        # 获取产品链接
        product_links = response.css('.product-card a::attr(href)').getall()
        
        for link in product_links:
            yield response.follow(link, callback=self.parse_product)
        
        # 分页
        next_page = response.css('.pagination .next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_category)
    
    def parse_product(self, response):
        """解析产品详情页"""
        loader = ItemLoader(item=ProductItem(), response=response)
        
        loader.add_css('name', 'h1.product-title::text')
        loader.add_css('price', '.price::text', MapCompose(lambda x: re.sub(r'[^\d.]', '', x)))
        loader.add_css('description', '.product-description::text', Join(' '))
        loader.add_css('category', '.breadcrumb a::text')
        loader.add_css('image_url', '.product-image img::attr(src)')
        loader.add_value('url', response.url)
        
        yield loader.load_item()
```

### 5.2 新闻网站爬虫

```python
import scrapy
from datetime import datetime

class NewsSpider(scrapy.Spider):
    name = 'news'
    
    def start_requests(self):
        yield scrapy.Request(
            url='https://news.example.com',
            callback=self.parse_homepage
        )
    
    def parse_homepage(self, response):
        """解析首页"""
        article_links = response.css('.article-link::attr(href)').getall()
        
        for link in article_links[:10]:  # 只爬取前10篇
            yield response.follow(link, callback=self.parse_article)
    
    def parse_article(self, response):
        """解析文章详情"""
        yield {
            'title': response.css('h1::text').get('').strip(),
            'author': response.css('.author::text').get('').strip(),
            'date': response.css('.date::text').get('').strip(),
            'content': ' '.join(response.css('.article-content p::text').getall()),
            'tags': response.css('.tag::text').getall(),
            'url': response.url,
            'crawl_time': datetime.now().isoformat(),
        }
```

## 最佳实践

### 1. 遵守robots.txt
```python
# 在Scrapy中启用
ROBOTSTXT_OBEY = True

# 手动检查
import urllib.robotparser

def check_robots_txt(url):
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(url + '/robots.txt')
    rp.read()
    return rp.can_fetch('*', url)
```

### 2. 限速与并发控制
```python
# Scrapy配置
DOWNLOAD_DELAY = 1
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 4
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
```

### 3. 数据存储
```python
# 使用Pipeline存储到数据库
import pymongo

class MongoDBPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )
    
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
    
    def process_item(self, item, spider):
        collection = self.db[spider.name]
        collection.insert_one(dict(item))
        return item
    
    def close_spider(self, spider):
        self.client.close()
```

### 4. 错误处理与日志
```python
import logging
from scrapy.exceptions import DropItem

class ValidationPipeline:
    def process_item(self, item, spider):
        if not item.get('name'):
            raise DropItem("Missing product name")
        
        if not item.get('price'):
            logging.warning(f"No price for item: {item.get('name')}")
        
        return item
```

## 相关页面

- [[Python自动化办公]] - 办公文档处理
- [[Python数据处理]] - 数据清洗与分析
- [[Python Web开发]] - Web应用开发
- [[Python机器学习实战]] - 机器学习应用

## 参考资源

- [requests文档](https://docs.python-requests.org/)
- [BeautifulSoup文档](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Scrapy文档](https://docs.scrapy.org/)
- [Selenium文档](https://www.selenium.dev/documentation/)
- [Playwright文档](https://playwright.dev/python/)

---

*最后更新：2026年6月28日*