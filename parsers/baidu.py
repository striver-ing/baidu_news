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
        next_keyword = False
        for num in range(0, 751, 50):
            # link = "http://news.baidu.com/ns?word=%s&pn=%s&cl=2&ct=1&tn=news&rn=50&ie=utf-8&bt=0&et=0"
            keyword = tools.quote(keyword)
            link = 'http://news.baidu.com/ns?word=%s&pn=%s&cl=2&ct=0&tn=news&rn=50&ie=utf-8&bt=0&et=0' % (keyword, num)
            html = tools.get_html_by_webdirver(link)
            headers = tools.get_tag(html, 'h3', {'class': 'c-title'}, find_all=True)
            for i in range(0, len(headers)):
                # print(headers[i])
                url = headers[i].a['href']
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
                        '''%(uuid, title, author, release_time, website_domain, url, content))

                    # 入库
                    if tools.is_have_chinese(title):
                        self_base_parser.add_news_acticle(uuid, title, author, release_time, website_name , website_domain, website_position, url, content)

                    current_date = tools.get_current_date('%Y-%m-%d')
                    if release_time and current_date > release_time:
                        next_keyword = True
                        break

            if next_keyword:
                break


# 必须定义 解析网址
def parser(url_info):
    pass
    # root_url = url_info['url']
    # html = tools.get_html_by_webdirver(root_url)
    # headers = tools.get_tag(html, 'h3', {'class': 'c-title'}, find_all=True)
    # for i in range(0, len(headers)):
    #     url = headers[i].a['href']
    #     print(url)
    #     article_extractor = ArticleExtractor(url)
    #     title = article_extractor.get_title()
    #     release_time = article_extractor.get_release_time()
    #     print(release_time)
    #     author = article_extractor.get_author()
    #     content = article_extractor.get_content()
    #     current_date = tools.get_current_date('%Y-%m-%d')
    #     if current_date > release_time:
    #         base_parser.update_value('BAIDU_NEWS_urls', {'remark': url_info['remark']}, {'status': Constance.DONE})
    #         break
    #     base_parser.save_baidu_info('BAIDU_NEWS_info', site_id=SITE_ID, content=content, release_time=release_time,
    #                                 title=title, author=author, url=url)
    #
    # base_parser.update_url('BAIDU_NEWS_urls', url_info['url'], Constance.DONE)
