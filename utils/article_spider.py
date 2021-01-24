from bs4 import BeautifulSoup
import requests_html


def get_article_page(url):
    from bs4 import BeautifulSoup
    import requests_html

    req = requests_html.HTMLSession()
    responses = req.get('https://mp.weixin.qq.com/s/q5wtK3iC9xYq_Wn3cMsy2A',
                        headers={
                            'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.9"})
    responses.html.render(sleep=1)

    soup = BeautifulSoup(responses.html.html, 'html.parser')

    nickname = soup.find('strong', {'class': 'profile_nickname'}).string
    title = soup.find('h2', {'class': 'rich_media_title'}).string

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
