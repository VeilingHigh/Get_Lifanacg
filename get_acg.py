# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
import os
from mongodb_queue import MogoQueue
headers={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}
start_url=input('请输入您要获取的漫画的首地址：')
P_url=start_url.rsplit('/',1)[0]+'/'
#地址前缀
spider_queue = MogoQueue('acg', 'sex_cool')
def mkdir(title):
    isExists=os.path.exists(os.path.join("/home/virgil/图片/adult_only", title))
    if not isExists:
        print(u'建立了一个名字叫做',title,u'的文件夹')
        os.makedirs(os.path.join("/home/virgil/图片/adult_only", title))
        os.chdir("/home/virgil/图片/adult_only/" + title)
        return True
    else:
        print(u'名字叫做',title,u'的文件夹已经存在了！')
        os.chdir("/home/virgil/图片/adult_only/" + title)
        return False

def acg():
    global headers
    global P_url
    global start_url

    while True:
        spider_queue.repair()
        try:
            href = spider_queue.pop()
            if href=='#':
                img_page_url=start_url
            else:
                img_page_url = P_url + href
        except KeyError:
            print('队列中没有数据！')
            spider_queue.clear()
            break
        else:
            img_page_html = requests.get(img_page_url, headers)
            img_Soup = BeautifulSoup(img_page_html.text, 'lxml').find('div', class_='content')
            img_url = img_Soup.find('img')['src']
            if href=='#':
                name='1'
            else:
                name=img_page_url[-9:-5].split('_')[-1]
            save_img(img_url,name)
            spider_queue.complete(href)
def save_img(img_url,name):
    name=name+'.jpg'
    print(u'正在保存图片...',name)
    img = requests.get(img_url, headers)
    f = open(name, 'ab')
    f.write(img.content)
    f.close()

def start(url):
    response = requests.get(url, headers)
    response.encoding = response.apparent_encoding
    Soup = BeautifulSoup(response.text, 'lxml')
    page_all = Soup.find('div', class_='dede_pages').find_all('li')[2:-1]
    title = Soup.find('title').get_text()
    for page in page_all:
        url=page.find('a')['href']
        spider_queue.push(url, title)
    """上面这个调用就是把URL写入MongoDB的队列了"""

if __name__ == "__main__":
    start(start_url)
    title = spider_queue.pop_title('#')
    mkdir(title)
    try:
        acg()
    except:
        print('掉线了，但可重新来过！')
        acg()
