import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from lxml import etree
from typing import List, Dict
import re


firefox_options = Options()
firefox_options.add_argument('-headless')
firefox_options.add_argument('--disable-gpu')
# 不加载图片
firefox_options.add_argument('blink-settings=imagesEnabled=false') # https://ftp.mozilla.org/pub/firefox/releases/115.10.0esr/linux-x86_64/en-US/

firefox_binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox" # https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz
firefox_options.binary_location = firefox_binary_location
# requests不能正常获取到页面元素，所以用selenium库
service = Service('/opt/homebrew/bin/geckodriver')
bro = webdriver.Firefox(
    options=firefox_options,
    service=service
)

def process_gbk(content:str) -> str:
    content = re.sub(u'([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b])', '', content)
    return content

class JiuyanSpider:
    def __init__(self, bro) -> None:
        self.bro = bro

    # //*[@id="__layout"]/div/div[2]/div/div[1]/div[1]
    def _get_title(self, li):
        try:
            title = li.xpath('./div/section/div[2]/div/div/span//text()')[0]
        except:
            title = ''
        return title
    
    def _get_author_name(self, li):
        try:
            author = li.xpath('./div/section/div[1]/div[1]/div/div[2]/div[1]/div[1]/span//text()')[0]
        except:
            author = ''
        return author
    
    def _get_forward_num(self, li):
        try:
            forward_num = li.xpath('./div/section/div[3]/div/div[2]/div[1]/span//text()')[0]
        except:
            forward_num = ''
        return forward_num
    
    def _get_reply_num(self, li):
        try:
            reply_num = li.xpath('./div/section/div[3]/div/div[2]/div[2]/span//text()')[0]
        except:
            reply_num = ''
        return reply_num
    
    def _get_likes_num(self, li):
        try:
            likes_num = li.xpath('./div/section/div[3]/div/div[2]/div[3]/span//text()')[0]
        except:
            likes_num = ''
        return likes_num
    
    def _get_referer(self, li):
        detailed_url = 'https://www.jiuyangongshe.com' + li.xpath('./div/section/div[3]/div/section/div/div/a//@href')[0]
        return detailed_url
    
    def _get_content(self, url:str) -> List:
        l = []
        self.bro.get(url)
        response = self.bro.page_source
        tree = etree.HTML(response)
        try:
            time = tree.xpath('//*[@id="__layout"]/div/div[2]/div/div[1]/div[2]/div/div/div[2]//text()')[0]
        except:
            time = ''
        l.append(time)
        try:
            # content = tree.xpath('//*[@id="__layout"]/div/div[2]/div/div[1]/section/div[1]/div[1]//text()')
            content = tree.xpath('//*[@id="__layout"]/div/div[2]/div/div[1]/section/div[1]//text()')
            content = ','.join(content)
            content = process_gbk(content)
        except:
            content = ''
        l.append(content)
        return l
 
    def get_jiuyan_data(self, query:str, items_num:int) -> List[Dict] :
        page_url = f'https://www.jiuyangongshe.com/search/new?k={query}'
        self.bro.get(page_url)
        page_response = self.bro.page_source
        page_tree = etree.HTML(page_response)
        li_list = page_tree.xpath('//*[@id="container"]/div[5]/div/ul/li')
        data_info_list = []
        for li in li_list[:items_num]:
            referer = self._get_referer(li)
            data_info = {
                'title': self._get_title(li),
                'author': self._get_author_name(li),
                'forward_num': self._get_forward_num(li),
                'reply_num': self._get_reply_num(li),
                'likes_num': self._get_likes_num(li),
                'time': self._get_content(referer)[0],
                'content': self._get_content(referer)[1]
            }
            data_info_list.append(data_info)
        return data_info_list



class GubaSpider:
    def __init__(self, bro) -> None:
        self.bro = bro

    def _get_referer(self, div):
        # 首页获取的帖子网址有两种形式，如果是以news开头，则已经是最后的网址，如果不是，则要多做一步获得最后网址
        if div.xpath('./td[3]/div//a/@href')[0][1:5:] == 'news':
            detail_url = 'https://guba.eastmoney.com' + div.xpath('./td[3]/div//a/@href')[0]
            return detail_url
        else:
            detail_url = 'https:' + div.xpath('./td[3]/div//a/@href')[0]
            self.bro.get(detail_url)  # 打开页面
            response = self.bro.page_source
            tree = etree.HTML(response)
            try:
                comment_url = 'https:' + tree.xpath('//div[@class="bottom_btns clearfix"]/a/@href')[0]
                try:
                    if tree.xpath('//div[@class="bottom_btns clearfix"]/@style')[0] == 'display: none;':
                        comment_url = detail_url
                except:
                    if len(comment_url) < 30:
                        comment_url = detail_url
                    comment_url = comment_url
            except:
                comment_url = detail_url
            return comment_url
    
    def _get_content_guba(self, url):
        l = []
        self.bro.get(url)  # 打开页面
        response = self.bro.page_source
        tree = etree.HTML(response)
        try:
            time = tree.xpath('//*[@class="author-info cl"]/div[@class="time"]//text()')[0].strip()
        except:
            time = ''
        l.append(time)
        try:
            content = tree.xpath('/html/body/div[1]/div[4]/div[1]/div[1]/div[4]/div//text()')
            content = ','.join(content)
            content = process_gbk(content)
        except:
            content = ''
        l.append(content)
        return l
    
    def _get_content_caifuhao(self, url):
        l = []
        self.bro.get(url)  # 打开页面
        response = self.bro.page_source
        tree = etree.HTML(response)
        try:
            time = tree.xpath('/html/body/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/span[2]//text()')[0].strip()
        except:
            time = ''
        l.append(time)
        try:
            content = tree.xpath('/html/body/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[3]//text()')
            content = ','.join(content)
            content = process_gbk(content)
        except:
            content = ''
        l.append(content)
        return l
    
    def _get_child_comments(self, re, data_info):
        for child in re['child_replys']:
            data_info['comment'].append(process_gbk(child['reply_text']))
        return data_info

    def _get_reply(self, referer, postid, replyid, data_info, count):
        referer = referer
        headers_reply = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'Connection': 'keep-alive',
                'Content-Length': '144',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Cookie': 'qgqp_b_id=02219768835ea8d780485368a0c72c3d; st_si=03840835922058; st_asi=delete; st_pvi=66677116630513; st_sp=2023-01-17%2011%3A45%3A16; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=63; st_psi=20230119214823454-117001300541-1526738941',
                'Host': 'guba.eastmoney.com',
                'Origin': 'https://guba.eastmoney.com',
                'Referer': referer,
                'sec-ch-ua': '"Not_A Brand";v="99", "Microsoft Edge";v="109", "Chromium";v="109"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.55',
                'X-Requested-With': 'XMLHttpRequest'
            }
        p = 1
        param = f'postid={postid}&replyid={replyid}&sort=1&sorttype=1&ps=10&p={p}'
        payload = {
            'param': param,
            'path': 'reply/api/Reply/ArticleReplyDetail',
            'env': '2'
        }
        reply_url = 'https://guba.eastmoney.com/interface/GetData.aspx?path=reply/api/Reply/ArticleReplyDetail'
        # 同样，通过post方法获取带有回复的json数据来获取回复
        response = requests.post(reply_url, headers=headers_reply, data=payload)
        flag = True
        while response.json()['re']['child_replys']:
            param = f'postid={postid}&replyid={replyid}&sort=1&sorttype=1&ps=10&p={p}'
            payload = {
                'param': param,
                'path': 'reply/api/Reply/ArticleReplyDetail',
                'env': '2'
            }
            response = requests.post(reply_url, headers=headers_reply, data=payload)
            re = response.json()['re']
            if count == 1:
                # 如果这个回复所对应的评论还未写入，则先写入这条评论，再写入回复
                if flag:
                    data_info['comment'].append(process_gbk(re['reply_text']))
                    flag = False
                data_info = self._get_child_comments(re, data_info)
            else:
                if flag:
                    data_info['comment'].append(process_gbk(re['reply_text']))
                    flag = False
                data_info = self._get_child_comments(re, data_info)
            count += 1
            p += 1

        return data_info

    def _get_comments(self, referer, postid, data_info):
        '''
        获取帖子网址开头为"guba"的评论
        :param referer: 评论所在网址
        :param postid: 帖子的postid
        :param writer: 要写入的文件
        :param data_info: 用于作为帖子第一条记录的标题、内容、发布者等信息
        :return:
        '''
        referer = referer
        headers_comments = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Content-Length': '122',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'qgqp_b_id=02219768835ea8d780485368a0c72c3d; st_si=03840835922058; st_asi=delete; st_pvi=66677116630513; st_sp=2023-01-17%2011%3A45%3A16; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=60; st_psi=20230119185641946-117001300541-9828226267',
            'Host': 'guba.eastmoney.com',
            'Origin': 'https://guba.eastmoney.com',
            'Referer': referer,
            'sec-ch-ua': '"Not_A Brand";v="99", "Microsoft Edge";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.55',
            'X-Requested-With': 'XMLHttpRequest'
        }
        page = 1
        param = f'postid={postid}&sort=1&sorttype=1&p={page}&ps=30'
        payload = {
            'param': param,
            'path': 'reply/api/Reply/ArticleNewReplyList',
            'env': '2'
        }
        comment_url = 'https://guba.eastmoney.com/interface/GetData.aspx?path=reply/api/Reply/ArticleNewReplyList'
        # 使用post方法获取存有评论的json数据
        response = requests.post(comment_url, headers=headers_comments, data=payload)
        # 当response.json()['re']有内容时，循环一直进行，获取评论
        count = 1
        while response.json()['re']:
            param = f'postid={postid}&sort=1&sorttype=1&p={page}&ps=30'
            payload = {
                'param': param,
                'path': 'reply/api/Reply/ArticleNewReplyList',
                'env': '2'
            }
            response = requests.post(comment_url, headers=headers_comments, data=payload)
            re_list = response.json()['re']
            for re in re_list:
                if int(re['reply_count']) > 2:
                    replyid = re['reply_id']
                    data_info = self._get_reply(referer, postid, replyid, data_info, count)
                    count += 1
                else:
                    if count == 1:
                        data_info['comment'].append(process_gbk(re['reply_text']))
                        data_info = self._get_child_comments(re, data_info)
                    else:
                        data_info['comment'].append(process_gbk(re['reply_text']))
                        data_info = self._get_child_comments(re, data_info)
                count += 1
            page += 1
        
        return data_info

    def _get_comments_caifuhao(self, url, postid, data_info):
        # 网址为开头为”caifuhao“的帖子无法通过post获取json数据来获取评论，因此通过selenium来获取评论
        self.bro.get(url)  # 打开页面
        response = self.bro.page_source
        tree = etree.HTML(response)
        div_list = tree.xpath('//*[@id="comment_all_content"]/div/div')
        count = 1
        try:
            for div in div_list:
                comment = process_gbk(div.xpath('./div/div[2]/div[2]/text()')[0])
                # 如果这条评论的回复数大于2，则调用获取回复方法
                if int(div.xpath('./@data-reply_count')[0]) > 2:
                    replyid = div.xpath('./@data-reply_id')[0]
                    data_info = self._get_reply(url, postid, replyid, data_info, count)
                    count += 1
                elif int(div.xpath('./@data-reply_count')[0]) == 0:
                    if count == 1:
                        data_info['comment'] == comment
                        data_info['comment'].append(comment)
                    else:
                        data_info['comment'].append(comment.replace(u'\xa0', u''))
                else:
                    if count == 1:
                        data_info['comment'] == comment
                        data_info['comment'].append(comment)
                        
                    else:
                        data_info['comment'].append(comment)
                        reply_list = div.xpath('./div/div[4]/div[2]')
                        for reply in reply_list[0:-2:]:
                            reply_comment = reply.xpath('./div[1]/div[1]/span[@class="l2_short_text"]/text()')[0]
                            data_info['comment'].append(process_gbk(reply_comment))
                count += 1
            return data_info
        except:
            return data_info
        
    def _get_postid(self, div):
        if div.xpath('./td[3]/div//a/@href')[0][1:5:] == 'news':
            # postid有两种不同存在方式
            try:
                postid = div.xpath('./td[3]/div//a/@data-postid')[0]
            except:
                postid = div.xpath('./td[3]/div/a/@href')[0][13:-5:]
        else:
            referer = 'https:' + div.xpath('./td[3]/div//a/@href')[0]
            self.bro.get(referer)
            response = self.bro.page_source
            tree = etree.HTML(response)
            res = tree.xpath('/html/head/script[1]//text()')[0].strip().lower()
            postid = res[res.find('postid')+8: res.find('postid')+18]
        return postid
    
    def _get_title(self, div):
        try:
            title = div.xpath('./td[3]/div//a/text()')[0]
        except:
            title = ''
        return title
    
    def _get_author_name(self, div):
        try:
            author = div.xpath('./td[4]/div//a/text()')[0]
        except:
            author = ''
        return author
    
    def _get_read_num(self, div):
        try:
            read = div.xpath('./td[1]/div//text()')[0]
        except:
            read = ''
        return read
    
    def _get_comment_num(self, div):
        try:
            comment_number = div.xpath('./td[2]/div//text()')[0]
        except:
            comment_number = ''
        return comment_number

    def get_guba_data(self, stock_code: str, items_num: int):
        page_url = f'http://guba.eastmoney.com/list,{stock_code}.html'
        self.bro.get(page_url)  # 打开页面
        page_response = self.bro.page_source
        page_tree = etree.HTML(page_response)
        div_list = page_tree.xpath('/html/body/div[1]/div[3]/div[1]/div[1]/div/ul/li[1]/table/tbody/tr')
        data_info_list = []
        for div in div_list[:items_num]:
            title = self._get_title(div)
            author = self._get_author_name(div)
            read = self._get_read_num(div)
            comment_number = self._get_comment_num(div)
            data_info = {
                'title': title,
                'author': author,
                'read': read,
                'comment_number': comment_number,
                'time': '',
                'content': '',
                'comment': []
            }
            referer = self._get_referer(div)
            postid = self._get_postid(div)
            # 获取帖子的发布时间和内容
            if referer[8:12:] == 'guba':
                temp = self._get_content_guba(referer)
                data_info['time'] = temp[0]
                data_info['content'] = temp[1]
                # 判断，如果帖子评论数为0，则不需要调用获取评论方法
                if int(div.xpath('./td[2]/div//text()')[0]) == 0:
                    data_info_list.append(data_info)
                else:
                    data_info = self._get_comments(referer, postid, data_info)
                    data_info_list.append(data_info)

            elif referer[8:16:] == 'caifuhao':
                temp = self._get_content_caifuhao(referer)
                data_info['time'] = temp[0]
                data_info['content'] = temp[1]
                if int(div.xpath('./td[2]/div//text()')[0]) == 0:
                    data_info_list.append(data_info)
                else:
                    data_info = self._get_comments_caifuhao(referer, postid, data_info)
                    data_info_list.append(data_info)
            # 有些帖子是视频，遇到直接跳过
            else:
                continue
        return data_info_list
    
if __name__ == '__main__':
    api = JiuyanSpider(bro)
    data_list = api.get_jiuyan_data('永冠新材',3) # 股票名称/股票代码

    # api = GubaSpider(bro)
    # data_list = api.get_guba_data('000001', 3)
    print(data_list)