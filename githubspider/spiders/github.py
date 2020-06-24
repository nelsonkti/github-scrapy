# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest


class GithubSpider(scrapy.Spider):
    name = 'github'
    allowed_domains = ['github.com']

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Referer': 'https://github.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    # 请求头

    def start_requests(self):
        # 重写start_requests方法
        urls = ['https://github.com/login']
        for url in urls:
            yield Request(url, meta={'cookiejar': 1}, callback=self.github_login)
            # 通过meta传入cookiejar特殊key，爬取url作为参数传给回调函数
            # meta：字典格式的元数据
            # cookiejar：是meta的一个特殊的key，通过cookiejar参数可以支持多个会话对某网站进行爬取
            # 可以对cookie做标记1, 2, 3, 4......这样scrapy就维持了多个会话

    def github_login(self, response):
        authenticity_token = response.xpath(".//*[@id='login']/form/input[2]/@value").extract_first()

        # 首先从源码中获取到authenticity_token的值
        return FormRequest.from_response(
            response,
            url='https://github.com/session',
            meta={'cookiejar': response.meta['cookiejar']},
            headers=self.headers,
            formdata={
                'authenticity_token': authenticity_token,
                'commit': 'Sign in',
                'login': '***',
                'password': '****',
                'utf8': '✓'
            },
            callback=self.github_after,
            dont_click=True
            # dont_click如果是True，表单数据将被提交，而不需要单击任何元素
        )

    def github_after(self, response):
        home_page = response.xpath(".//*[@class='btn btn-outline mt-2']/text()").extract()
        # 获取登录成功后页面中的文本“Browse activity”

        if 'Explore GitHub' in home_page:
            self.logger.info('成功')
            # 如果含有“Browse activity”，则打印登录成功
        else:
            self.logger.error('失败')