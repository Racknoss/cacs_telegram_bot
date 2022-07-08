from selenium import webdriver
import re
import requests
from bs4 import BeautifulSoup
import urllib


def find_person_s(surname):
    url = "https://cacs.econ.msu.ru/index.php"
    header_t =  {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7",
    "Referer":"https://cacs.econ.msu.ru/index.php"}
    session = requests.Session()
    data = {"VZESH": urllib.parse.quote(surname.encode("cp1251")) , 'VZESHB.x':'4', 'VZESHB.y':'4'}
    res_t = session.get(url, headers =  {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'})
    res = session.post(url,headers = header_t, data = data)
    print(session.cookies)
    #print(res.text)
    #driver = webdriver.Chrome()
    #driver.get("https://cacs.econ.msu.ru/index.php?mnu=75")
    #driver.find_element_by_class_name('InpLg').send_keys(surname)
    #driver.find_element_by_name('VZESHB').click()
    tag = res.text
    names_best = re.findall(r'{}'.format(surname), tag)
    names = re.findall(r'selst=([0-9]*)[^{}]*{}\s(\w*\s\w*)'.format(surname,surname), tag)
    #driver.quit()
    return names_best

def find_person_n(surname, f_name):
    driver = webdriver.Chrome()
    driver.get("https://cacs.econ.msu.ru/index.php?mnu=75")
    driver.find_element_by_class_name('InpLg').send_keys(surname)
    driver.find_element_by_name('VZESHB').click()
    tag = driver.page_source
    names = re.findall(r'selst=([0-9]*)[^{}]*{}\s(\w*)'.format(surname,surname+" "+f_name), tag)
    driver.quit()
    return names
    
    



def get_id(surname, f_name,s_name):
    full_name = surname + " " + f_name + " " + s_name
    driver = webdriver.Chrome()
    driver.get("https://cacs.econ.msu.ru/index.php?mnu=75")
    driver.find_element_by_class_name('InpLg').send_keys(surname)
    driver.find_element_by_name('VZESHB').click()
    tag = driver.page_source
    id_p = re.findall(r'selst=([0-9]*)[^{}]*{}'.format(surname,full_name), tag)
    driver.quit()
    return id_p[0]


def get_timetable_list(id_p,time):  
    url = "https://cacs.econ.msu.ru/index.php?aID=4&mnu=75&selst={}&selday={}".format(id_p,time)
    headers =  {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'} 
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    quotes = soup.find_all('table', class_='TEXT1')
    temp = ""
    for quote in quotes:
        #print(re.sub(r"\d\sпара","", re.sub(r'(\d\sпара)',r"\1\1" ,re.sub(r'\n','',quote.text)),1)  )
        temp = re.findall(r'(\d\sпара.*?)\d\sпара',
                          re.sub(r"\d\sпара","",re.sub(r'(\d\sпара)',r"\1\1" ,re.sub(r'\n','',quote.text+"9 пара")),1))
        for key,t in enumerate(temp):
             temp[key] = re.sub(r"(а:)|\'",'',t)
        test = quote
    return temp

def get_timetable(id_p,time):
    temp = ""
    for t in get_timetable_list(id_p,time):
        temp = temp + t + "\n\n"
    return temp


#Тестируем
if __name__ == "__main__":
    name = "Николаев"
    group = "Лысенко".encode("cp1251")
    print(urllib.parse.quote(group))
    print(find_person_s("Людмирский"))
    
    



