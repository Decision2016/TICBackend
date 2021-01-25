from bs4 import BeautifulSoup
from selenium import webdriver
import time

def get_article_page(url):
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(url)

    html = driver.execute_script("return document.documentElement.outerHTML")
    soup = BeautifulSoup(html, 'html.parser')
    driver.close()

    nickname = soup.find('strong', {'class': 'profile_nickname'}).string
    title = soup.find('h2', {'class': 'rich_media_title'}).string
    title = title.strip().replace(' ', '')

    for div in soup.find_all("div", {'class': 'qr_code_pc_outer'}):
        div.decompose()
    main_div = soup.find_all("div", {'id': 'js_article'})

    for img in soup.find_all("img", {'class': 'img_loading'}):
        img["src"] = img["data-src"]
        img["data-src"] = ''

    page = "<html><body>{0}{1}</body></html>".format(soup.find_all("style")[0], main_div[0])
    return {
        'title': title,
        'nickname': nickname,
        'page': page
    }

# print(get_article_page('https://mp.weixin.qq.com/s/G52Q9Pag56Qp9NRXVWSHQQ'))