from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

import csv

def click_btn_more(driver):
    while True:
        try:
            btn_tag = driver.find_element(By.CLASS_NAME, "btn_more")
            btn_tag.click()
            driver.implicitly_wait(3)
        except:
            break
    pass

driver = webdriver.Chrome()

kbank_qa_url = 'https://www.kbanknow.com/ib20/mnu/CBRCSC060200'
driver.get(kbank_qa_url)

ul_tag = driver.find_element(By.XPATH, '//*[@id="contentForm"]/div/div[3]/ul')
li_tags = ul_tag.find_elements(By.TAG_NAME, 'li')

items = []

for i in range(len(li_tags)):

    ul_tag = driver.find_element(By.XPATH, '//*[@id="contentForm"]/div/div[3]/ul')
    li_tags = ul_tag.find_elements(By.TAG_NAME, 'li')
    li_tag = li_tags[i]

    category = li_tag.text
    li_tag.click()  # category로 들어가기

    print(category)

    click_btn_more(driver)  # 더보기 버튼 클릭 전부하기

    driver.implicitly_wait(3)

    question_tags = driver.find_elements(By.CLASS_NAME, "question")
    answer_tags = driver.find_elements(By.CLASS_NAME, "answer")

    for question_tag, answer_tag in zip(question_tags, answer_tags):

        question_tag.click()

        driver.implicitly_wait(3)

        question, answer = question_tag.text, answer_tag.text

        item = {
            'category': category,
            'question': question,
            'answer': answer
        }

        items.append(item)

    driver.get(kbank_qa_url)

# write csv
with open('kbank_qa_dataset.csv', 'w', encoding='utf-8', newline='') as f:

    writer = csv.writer(f, delimiter='|')

    for item in items:
        category = item['category']
        question = item['question']
        answer = item['answer']

        writer.writerow([category, question, answer])
