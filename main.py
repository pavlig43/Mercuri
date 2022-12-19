import lxml

import requests
from bs4 import BeautifulSoup
import pandas as pd
from openpyxl import Workbook
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
from selenium.webdriver.support.ui import Select
wb =Workbook().save('Остатки.xlsx')# создаю книгу ексель пустую


options = webdriver.ChromeOptions()
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=options)
driver.get("https://mercury.vetrf.ru/")

WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Меркурий.ХС'))).click()  # ЗАхожу в меркурий
login = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.ID, "username"))).send_keys(
    'kovynjov_pe_221018')  # Логин

passw = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.ID, "password")))  # Пароль
passw.send_keys('25041992Aa')
passw.send_keys(Keys.RETURN)  # Вход
tg = WebDriverWait(driver, 120).until(EC.visibility_of_element_located((By.ID, "captcha")))  # поиск каптчи
s = WebDriverWait(driver, 120).until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, "label.active:nth-child(1614) > input:nth-child(1)"))).click()  # выбор мясокомб
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".positive"))).click()  # найти
window_before = driver.window_handles[0]  # Старое окно
WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, ".menu-help > li:nth-child(4) > a:nth-child(1)"))).click()  # Создаю новое окно

window_after = driver.window_handles[1]  # новое окно
driver.switch_to.window(window_after)  # переключаюсь на новую вкладку
time.sleep(3)
driver.find_elements('link text', 'Неоформленные')[2].click()  # перехожу в неоформ
time.sleep(3)
sel = Select(driver.find_element('xpath',
                                 "/html/body/div[1]/div/div[3]/form/div/div[2]/div[2]/select"))  # Выбираю список 100
sel.select_by_value('100')  # Выбираю список 100

lst = ['Слизистая оболочка тонкого отдела кишечника свиней замороженная груп. упак. 1кг Агрокомплекс',
       'Сетчатка глаза КРС зам. груп. упак. 1кг Агрокомплекс']
dl = []
for i in lst:
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "findFormTop"))).click()  # Тыкаю поиск
    time.sleep(2)
    # будет цикл по наименованию
    try:
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.ID, "cargoInfoGroupExpandBtn"))).click()
        # Открываю поиск для раскрыия, try потому что список уже открытый
    except:
        driver.find_element('id',"productNameId").clear()
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "productNameId"))).send_keys(i)
    # Поиск продукции , тут будет перебор
#    driver.find_element('id',"productNameId").clear()
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "productNameId"))).send_keys(i)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, ".ffControl > div:nth-child(1) > button:nth-child(1)"))).click()  # готовый список
    window_after = driver.window_handles[1]  # старое окно
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "printSettingsFormTop"))).click()  # печать
    time.sleep(2)
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "anotherName"))).click()  # другое наименование
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "productionDate"))).click()  # ддата выработки
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "bestBeforeDate"))).click()  # годен до
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "remainder"))).click()  # остаток
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                "table.layoutform2 > tbody:nth-child(1) > tr:nth-child(4) > td:nth-child(1) > div:nth-child(1) > button:nth-child(1)"))).click()  # печать

    window_table = driver.window_handles[2]  # окно с таблицей
    driver.switch_to.window(window_table)  # переключение на таблицу
    df_list = pd.read_html(driver.page_source,decimal=',', thousands='.')  # получаю html таблицы
    df = df_list[0]  # получаю датафрейм из таблицы
    dl.append(df)

    driver.switch_to.window(window_after)  # переключение на окно назад
with pd.ExcelWriter('Остатки.xlsx',mode='a',if_sheet_exists='overlay') as writer:
    for i in dl:
        i[i.columns[1]] = pd.to_datetime(i[i.columns[1]],format='%d%m%Y', errors='coerce').dt.strftime('%m.%d.%Y')
        i[i.columns[2]] = pd.to_datetime(i[i.columns[2]],format='%d%m%Y', errors='coerce').dt.strftime('%m.%d.%Y')
        i[i.columns[4]] = i[i.columns[4]].str.replace('.', ',')
        name = i.at[2, i.columns[1]]
        i.to_excel(writer, sheet_name=f'{name}',index=False)
