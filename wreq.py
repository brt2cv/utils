###############################################################################
# Name:         Web Http Request
# Usage:
# Author:       Bright Li
# Modified by:
# Created:      2020-02-11
# Version:      [0.0.3]
# RCS-ID:       $$
# Copyright:    (c) Bright Li
# Licence:
###############################################################################

_headers = {
    "Accept-Language": "zh-CN,zh;q=0.9",
    # "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    # "Pragma": "no-cache",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
}

def get_headers():
    return _headers

# _request_method = {
#     "requests",
#     "selenium",
#     "pyquery"
# }

def make_request(url, method="r", timeout=5, retry=0):
    # assert method in _request_method, f"未知的Method: 【{method}】"
    def run_requests(url, timeout, retry):
        import requests
        # r = requests.get(url, _headers, timeout=[timeout, 30])
        s = requests.Session()
        if retry:  # 用于设置超时重连
            from requests.adapters import HTTPAdapter
            s.mount('http://', HTTPAdapter(max_retries=retry))
            s.mount('https://', HTTPAdapter(max_retries=retry))

        r = s.get(url, headers=_headers, timeout=timeout)
        r.encoding = "utf-8"
        return r

    if method == "r" or method == "requests":
        return run_requests(url, timeout, retry)
    elif method == "dom" or method == "pyquery":
        from pyquery import PyQuery
        # dom = pyquery.PyQuery(url, encoding="utf-8")
        r = run_requests(url, timeout, retry)
        return PyQuery(r.text)
    elif method == "browser" or method == "selenium":
        # from selenium import webdriver
        browser = make_webdriver()
        browser.get(url)
        return browser
    # elif method in _dict_webdriver:
    else:
        raise Exception(f"未知的Method: 【{method}】")


#####################################################################
try:
    from selenium import webdriver
except ImportError:
    pass
else:
    _dict_webdriver = {
        "phantomjs": {
            "path_bin": r"webdriver\phantomjs-2.1.1\bin\phantomjs.exe"
        },
        "chrome": {
            "path_bin": r"D:\programs\chrome\GoogleChromePortable.exe",
            "path_webdriver": "webdriver/chrome76/chromedriver.exe"
        },
        "360chrome": {
            "path_bin": r"D:\programs\360chrome\360chrome.exe",
            "path_webdriver": "webdriver/chrome69/chromedriver.exe"
        }
    }

    def _make_options(path_chrome_bin, headless=False):
        options = webdriver.ChromeOptions()
        # 或者使用Options
        # from selenium.webdriver.chrome.options import Options
        # options = webdriver.chrome.options.Options()

        # 选项说明: https://sites.google.com/a/chromium.org/chromedriver/capabilities
        options.setBinary = path_chrome_bin
        if headless:
            options.add_argument("--headless")
            options.add_argument('--disable-gpu')
        return options

    def make_webdriver(name="phantomjs", headless=False):
        """ name: {"phantomjs", "chrome", "360chrome", "firefox", "android"} """
        assert name in _dict_webdriver, f"未知的webdriver: 【{name}】"
        path_bin = _dict_webdriver[name]["path_bin"]

        if name == "phantomjs":
            driver = webdriver.PhantomJS(path_bin)
        else:
            options = _make_options(path_bin, headless)

            path_webdriver = _dict_webdriver[name]["path_webdriver"]
            # print(">>>", path_bin, path_webdriver)
            driver = webdriver.Chrome(path_webdriver,
                                    options=options)

        # driver.implicitly_wait(5)
        return driver

    make_selenium = make_webdriver


#%% test测试
if __name__ == "__main__":
    from selenium.webdriver.common.keys import Keys
    import time

    driver = make_webdriver("360chrome")
    driver.get('http://www.baidu.com')
    driver.find_element_by_id("kw").send_keys("seleniumhq" + Keys.RETURN)
    # button = driver.find_elements_by_class_name('s_btn')[0].click()  # 或者使用按钮
    time.sleep(3)
    driver.save_screenshot("acb.jpg")
    driver.close()
    driver.quit()
