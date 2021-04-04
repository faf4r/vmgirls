# written by TMFfa
# parse with xpath, use decorate function
import requests
import parsel
import os
import re
import time
from functools import wraps

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.63'}


def run_time(function):
    """
    decorate function, used to record run time
    :param function: main()
    :return: print runtime
    """
    @wraps(function)
    def decorated(*args, **kwargs):
        start_time = time.time()
        function(*args, **kwargs)
        end_time = time.time()
        run_time = int(end_time-start_time)
        print('The whole process spent', run_time, 'seconds')
    return decorated


def change_name(name):
    """
    change unavailable file name
    :param name:a file name
    :return:available file name
    """
    mode = re.compile(r'[\\/:*?"<>|]')
    new_name = re.sub(mode, '_', name)
    return new_name


class HtmlData:
    """
    used to save html data from get_urls()
    """
    def __init__(self, urls, dir_name='.'):
        self.urls = urls
        self.dir_name = dir_name


def get_urls(html_url):
    """
    get response and parse it
    :param html_url:target html
    :return:HtmlData object including urls list and dir_name
    """
    print('requesting...')
    s = time.time()
    r = requests.get(html_url, headers=headers)
    e = time.time()

    selector = parsel.Selector(r.text)

    dir_name = selector.xpath("/html/body/main/div/div[2]/div[1]/div/h1/text()").get()
    print(dir_name, 'has found', 'spent', int(e-s), 'seconds', end='   ')

    original_urls = selector.xpath('/html/body/main/div/div[2]/div[1]/div/div[4]/div[3]/a/@href').getall()[1:]
    print('find', len(original_urls), 'pictures\n')
    urls = []
    for original_url in original_urls:
        url = 'https:' + original_url
        urls.append(url)

    try:
        os.mkdir(dir_name)
    except:
        pass

    return HtmlData(urls, dir_name)


class Data:
    """
    used with function get_data() to save data
    """
    def __init__(self, text, content, file_name, request_time):
        self.text = text
        self.content = content
        self.file_name = file_name
        self.request_time = request_time


def get_data(url):
    """
    obtain image data
    :param url: image url from urls list
    :return:Data object
    """
    s = time.time()
    r = requests.get(url=url, headers=headers, timeout=10)
    print(url, 'respond\ndownloading...')
    e = time.time()
    requests_time = 'request time spent: ' + str(int(e-s)) + ' seconds'
    file_name = url.split('/')[-1]
    return Data(r.text, r.content, file_name, requests_time)


def save(data, dir_name):
    """
    save image
    :param data: Data object
    :param dir_name: HtmlData.dir_name, to save images from the same html in a same directory
    :return: None
    """
    with open(dir_name+'/'+change_name(data.file_name), 'wb') as f:
        f.write(data.content)
    print(dir_name+'/'+data.file_name, 'has saved  ', data.request_time, end='\n\n')


@run_time
def main(html_url):
    html_data = get_urls(html_url)
    for url in html_data.urls:
        data = get_data(url)
        save(data, dir_name=html_data.dir_name)


if __name__ == '__main__':
    html_url = 'https://www.vmgirls.com/15925.html'
    main(html_url)
