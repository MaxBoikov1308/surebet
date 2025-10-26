from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


def profit(update=False) -> list:
    # Настройки Chrome
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    # Подключаемся к уже открытому браузеру
    driver = webdriver.Chrome(options=chrome_options)

    # Получаем HTML текущей страницы
    html_content = driver.page_source

    # Не закрываем драйвер, чтобы браузер оставался открытым
    response = html_content

    if update:
        with open('index.txt', 'w', encoding='utf-8') as file:
            file.write(response)

    if 'data-profit' in response:
        import re
        profits = re.findall(r'data-profit="([\d.]+)"', response)
        print(profits[::2])
    return float(profits[0])

def calculate_stakes(k1: float, k2: float, summa: float = 10000) -> tuple:
    stake1 = 100 / (1 + k1 / k2)
    stake2 = 100 - stake1
    return round(stake1, 2) * summa / 100, round(stake2, 2) * summa / 100


if __name__ == '__main__':
    # profit(update=True)
    print(calculate_stakes(1.85, 3.4))