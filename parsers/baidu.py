import sys
sys.path.append('..')
import init

import base.base_parser as base_parser
import utils.tools as tools
from utils.log import log
from extractor.article_extractor import ArticleExtractor
import base.constance as Constance
import parsers.base_parser as self_base_parser

SITE_ID = 1712150002
NAME = '百度新闻 '


# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')

    table = 'BAIDU_NEWS_site_info'
    url = 'http://news.baidu.com'

    base_parser.add_website_info(table, site_id=SITE_ID, url=url, name=NAME)


# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(keywords):
    log.debug('''
        添加根url
        parser_params : %s
        ''' % str(keywords))
    for keyword in keywords:
        log.debug('添加根url 关键词 ' + keyword)
        keyword = tools.quote(keyword)
        link = 'http://news.baidu.com/ns?word=%s&pn=0&cl=2&ct=0&tn=news&rn=50&ie=utf-8&bt=0&et=0' % (keyword)
        base_parser.add_url('BAIDU_NEWS_urls', SITE_ID, link, remark = {'offset':0})


# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']
    offset = remark.get('offset')

    html = tools.get_html_by_webdirver(root_url)
    headers = tools.get_tag(html, 'div', {'class': 'result'}, find_all=True)
    if not headers:
        base_parser.update_url('BAIDU_NEWS_urls', root_url, Constance.DONE)

    for header in headers:
        # 查看更多相关新闻
        regex = ' <span class="c-info"><a.*?href="(.*?)".*?查看更多相关新闻'
        more_news_url = tools.get_info(str(header), regex, fetch_one = True)
        if more_news_url:
            more_news_url = tools.get_full_url('http://news.baidu.com', more_news_url)
            more_news_url = more_news_url.replace('amp;', '')
            base_parser.add_url('BAIDU_NEWS_urls', SITE_ID, more_news_url, depth = 1, remark = {'offset':0})

        url = header.h3.a['href']
        article_extractor = ArticleExtractor(url)
        content = title = release_time = author = website_domain =''
        content = article_extractor.get_content()
        if content:
            title = article_extractor.get_title()
            release_time = article_extractor.get_release_time()
            author = article_extractor.get_author()
            website_domain = tools.get_domain(url)
            uuid = tools.get_uuid(title, website_domain)
            website_name = ''
            website_position = None

            log.debug('''
                uuid         %s
                title        %s
                author       %s
                release_time %s
                domain       %s
                url          %s
                content      %s
                '''%(uuid, title, author, release_time, website_domain, url, '...'))

            # 入库
            if tools.is_have_chinese(content):
                is_continue = self_base_parser.add_news_acticle(uuid, title, author, release_time, website_name , website_domain, website_position, url, content)

                if not is_continue:
                    break
    else:
        # 循环正常结束 该页均正常入库， 继续爬取下页
        offset += 50
        url = tools.replace_str(root_url, 'pn=\d*', 'pn=%d'%offset)
        base_parser.add_url('BAIDU_NEWS_urls', SITE_ID, url, depth = 0, remark = {'offset': offset})

    base_parser.update_url('BAIDU_NEWS_urls', root_url, Constance.DONE)

if __name__ == '__main__':
    pass

    # link = 'http://news.baidu.com/ns?ct=1&rn=30&ie=utf-8&bs=%E6%B5%99%E6%B1%9F%E7%9C%81&rsv_bp=1&sr=0&cl=2&f=3&prevct=no&tn=news&word=%E6%B5%99%E6%B1%9F%E7%9C%81&rsv_sug3=2&rsv_sug4=32&rsv_sug1=1&rsp=0&inputT=844&rsv_sug=1'
    # html = tools.get_html_by_webdirver(link)
    # headers = tools.get_tag(html, 'div', {'class': 'result'}, find_all=True)

    # for header in headers:
    #     # 查看更多相关新闻
    #     regex = ' <span class="c-info"><a.*?href="(.*?)".*?查看更多相关新闻'
    #     more_news_url = tools.get_info(str(header), regex, fetch_one = True)
    #     if more_news_url:
    #         more_news_url = tools.get_full_url('http://news.baidu.com', more_news_url)
    #         more_news_url = more_news_url.replace('amp;', '')
    #         print(more_news_url)
    #     # print(headers[i])
    #     url = header.h3.a['href']
    #     article_extractor = ArticleExtractor(url)
    #     content = title = release_time = author = website_domain =''
    #     content = article_extractor.get_content()
    #     if content:
    #         title = article_extractor.get_title()
    #         release_time = article_extractor.get_release_time()
    #         author = article_extractor.get_author()
    #         website_domain = tools.get_domain(url)
    #         uuid = tools.get_uuid(title, website_domain)
    #         website_name = ''
    #         website_position = None

    #         log.debug('''
    #             uuid         %s
    #             title        %s
    #             author       %s
    #             release_time %s
    #             domain       %s
    #             url          %s
    #             content      %s
    #             '''%(uuid, title, author, release_time, website_domain, url, '...'))
