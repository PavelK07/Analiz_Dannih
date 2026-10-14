import requests
import csv
from bs4 import BeautifulSoup


# Запись в файл отдельно, чтобы не делать запрос каждый раз
CreateFile=1
if CreateFile: 
    url = 'https://mai.ru/press/news/'
    response = requests.get(url)
    if response.status_code==200:
        html = response.text

        with open('MaiNews.html', 'w', encoding='utf-8') as file:
            file.write(html)

# Чтение из файла и работа с BeautifulSoup
with open('MaiNews.html', 'r', encoding='utf-8') as file:
    content = file.read()
    soup = BeautifulSoup(content, 'html.parser')

    news_items = soup.find_all('article')
    news_data=[]

    for item in news_items:
        title = item.find('h5').text  
        print(title)

        date_tag = item.find('span', class_='badge')
        date = date_tag.get_text()
        print(date)
        
        link_tag = item.find_parent('a')
        
        link = link_tag.get('href', '')
        link = 'https://mai.ru/press/news/' + link
        
        print(link)

        news_data.append([title, date, link])
    
    print(news_data)

    with open('news_Mai.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for row in news_data:
            writer.writerow(row)
            
