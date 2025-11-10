from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def fetch_links_and_texts(url):
    # 初始化 WebDriver（以 Chrome 为例）
    user_data_dir = '/tmp/data'
    options = webdriver.ChromeOptions()
    options.debugger_address = "127.0.0.1:9222"
    options.add_argument(f'--user-data-dir={user_data_dir}')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    try:
        # 访问目标页面
        driver.get(url)

        # 等待页面加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "conference__title"))
        )

        # 模拟点击 class="show-more-items__btn-holder" 的 span
        try:
            show_more_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "show-more-items__btn-holder"))
            )
            show_more_button.click()
            # 可选：等待新内容加载完成
            time.sleep(5)
        except Exception as e:
            print("No 'Show More' button found or clickable:", e)

        # 查找所有 class="conference__title left-bordered-title" 的 div
        divs = driver.find_elements(By.CLASS_NAME, "conference__title")

        # 提取 <a> 标签的链接地址和文本
        result = []
        for div in divs:
            a_tag = div.find_element(By.TAG_NAME, "a")
            link = a_tag.get_attribute("href")
            text = a_tag.text
            result.append((link, text))

        return result

    finally:
        # 关闭浏览器
        driver.quit()


def fetch_response_text(url, sub=False):
    # 初始化 WebDriver（以 Chrome 为例）
    user_data_dir = '/tmp/data'
    options = webdriver.ChromeOptions()
    options.debugger_address = "127.0.0.1:9222"
    options.add_argument(f'--user-data-dir={user_data_dir}')
    # options.add_argument('--headless')  # 可选：无头模式
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    # try:
    # 访问目标页面
    driver.get(url)

    # 等待页面加载完成
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "markall")))

    if not sub:
        try:
            driver.find_element(By.CLASS_NAME, "showAllProceedings")
            # 有分页标识，分页拉取
            print(url, 'Repeat 30')
            response_text = ''
            for page_id in range(20):
                url_sub = '{}?id={}'.format(url, page_id * 30 + 1)
                print(url_sub)
                sub_text = fetch_response_text(url_sub, sub=True)
                # print(sub_text)
                if sub_text == 'end':
                    print('end')
                    break
                else:
                    response_text += '\n' + sub_text
            return response_text
        except Exception as e:
            print(e)
            # 否则直接拉取
            print('Directly')

    # 模拟点击 name="markall" 的 checkbox
    checkbox = driver.find_element(By.NAME, "markall")
    driver.execute_script("arguments[0].click();", checkbox)

    # 等待并模拟点击 title="Export Citations" 的 a 标签
    export_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[title="Export Citations"]'))
    )
    export_button.click()

    response_json = 'Loading Citations ...'

    while 'Citations ...' in response_json and 'Loading' in response_json:
        if response_json == 'Loading 0 Citations ...':
            return 'end'
        # 等待请求完成并获取返回的 JSON 数据
        time.sleep(5)  # 等待页面处理（根据实际情况调整时间）
        response_element = driver.find_element(By.TAG_NAME, "pre")  # 假设 JSON 数据显示在 <pre> 标签中
        response_json = response_element.text
        # print(response_element)
        if 'Citations ...' in response_json and 'Loading' in response_json:
            print(response_json)
        print('LEN response: ', len(response_json))
        if len(response_json) == 0:
            raise Exception('No Citations')
    return response_json

    # finally:
    #     # 关闭浏览器
    #     driver.quit()


def process_citations(driver):
    response_json = 'Loading Citations ...'

    while 'Citations ...' in response_json and 'Loading' in response_json:
        if response_json == 'Loading 0 Citations ...':
            return 'end'
        # 等待请求完成并获取返回的 JSON 数据
        time.sleep(2)  # 等待页面处理（根据实际情况调整时间）
        response_element = driver.find_element(By.TAG_NAME, "pre")  # 假设 JSON 数据显示在 <pre> 标签中
        response_json = response_element.text
        if 'Citations ...' in response_json and 'Loading' in response_json:
            print(response_json)
        print('LEN response: ', len(response_json))
        if len(response_json) == 0:
            raise Exception('No Citations')
    return response_json


def fetch_and_process_singlepage_eachitem(url, output_path, start_idx=0):
    # 初始化 WebDriver（以 Chrome 为例）
    user_data_dir = '/tmp/data'
    options = webdriver.ChromeOptions()
    options.debugger_address = "127.0.0.1:9222"
    options.add_argument(f'--user-data-dir={user_data_dir}')
    # options.add_argument('--headless')  # 可选：无头模式
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    output_file = open(output_path, 'w+', encoding='utf-8')
    try:
        # 访问目标页面
        driver.get(url)

        # 等待页面加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'button[data-target="#exportCitation"]'))
        )

        # 查找所有 data-target="#exportCitation" 的按钮
        buttons = driver.find_elements(By.CSS_SELECTOR, 'button[data-target="#exportCitation"]')

        print(buttons)
        # 遍历并模拟点击每个按钮
        for idx, button in enumerate(buttons):
            if idx < start_idx:
                continue
            try:
                button.click()
                # 调用处理函数获取 JSON 数据
                response_json = process_citations(driver)
                output_file.write(response_json + '\n')
                print("Processed Citation IDX :", idx)

                # 模拟点击 class="close" 的按钮
                close_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "close"))
                )
                close_button.click()
            except Exception as e:
                print("Error processing citation:", e)

    finally:
        # 关闭浏览器
        driver.quit()


# 示例调用
# if __name__ == "__main__":
#     url = "https://dl.acm.org/doi/proceedings/10.1145/3636534"  # 替换为实际目标页面 URL
#     output_path = './bibtex/MobiCom \'24 - ResearchPaper.bib'
#     fetch_and_process_singlepage_eachitem(url, output_path)

# 示例调用
if __name__ == "__main__":
    # url = "https://dl.acm.org/conference/mobicom/proceedings"
    # url = "https://dl.acm.org/conference/mobisys/proceedings"
    url = "https://dl.acm.org/conference/sensys/proceedings"
    # url = "https://dl.acm.org/conference/ipsn/proceedings"

    links_and_texts = fetch_links_and_texts(url)
    print(links_and_texts)
    # exit(0)

    # # 近10年
    # links_and_texts = links_and_texts[1:]
    # retry_list = list(map(str, [20]))
    # retry_list = ['MobiSys \'20']
    retry_list = []

    for link, text in links_and_texts:
        if len(retry_list) > 0:
            found = False
            for retry in retry_list:
                if retry in text:
                    found = True
                    print("Retrying:", text)
                    break
            if not found:
                continue
        # 调用 fetch_response_text 获取 response_text
        response_text = fetch_response_text(link)

        # 提取文件名（取 text 的 ":" 前的子字符串）
        filename = './bibtex/{}'.format(text.split(":")[0].strip() + ".bib")

        # 保存 response_text 到 .bib 文件
        with open(filename, "w", encoding="utf-8") as bib_file:
            bib_file.write(response_text)
        print(f"Saved {filename}")
