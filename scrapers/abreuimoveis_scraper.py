import requests
import lxml
import csv
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver

def AbreuImoveisScraper():
    url = "https://abreuimoveis.com.br/venda/casa/natal/"
    driver = webdriver.PhantomJS()
    driver.set_window_size(1024, 768)
    driver.get(url)

    #Function created to activate the js pagination element
    def turnpage(page):
        if page < 4:
            driver.find_element_by_xpath('//*[@id="page"]/div[2]/div[3]/div[2]/ul/li['+ str(page) +']/a').click()
        else:
            driver.find_element_by_xpath('//*[@id="page"]/div[2]/div[3]/div[2]/ul/li[4]/a').click()
        driver.save_screenshot('screenshots/depois da espera '+ str(page) +'.png')
        sleep(5)

    def get_url_list():
        url_list = []
        page = 2
        while page != 17:
            #Temporario - só a partir da pagina 13
            if page > 8:
                soup = BeautifulSoup(driver.page_source, 'lxml')
                for container in soup.find_all('div', class_='col-xs-12 grid-imovel'):
                    #url source of the advert
                    re_source = container.find('a', class_='titulo-grid')['href']
                    url_list.append(re_source)
                print("Urls gathered from page  " + str(page))
            #Activate the pagination
            turnpage(page)
            page += 1
        return url_list

    output_file = open("output/rawdata_abreu_houses.csv","a")
    url_list = get_url_list()

    for url_address in url_list:
        sleep(20)
        headers = {'User-Agent':'Mozilla/5.0'}
        advert_soup = BeautifulSoup(requests.get(url_address, headers=headers).text, 'lxml')
        print("Parsing: " + url_address + "\n")
        #title
        title = advert_soup.find('div', class_='col-xs-12 col-sm-12 col-md-6 col-lg-7 clb-imovel-title')
        advert_title = title.h1.text
        #address
        address = advert_soup.find('p', class_='endereco')
        advert_address = address.text.replace(","," ")
        #price
        pricetag = advert_soup.find('span', class_='thumb-price')
        adv_price = pricetag.text.replace(",","")
        #condofee
        condofee = advert_soup.find('div', style='margin-top: 8px')
        try:
            adv_condofee = condofee.span.text.strip()
        except:
            adv_condofee = 'NotFound'
        #amenities
        amenities = advert_soup.find('div', class_='property-amenities')
        am_list = amenities.find_all('div', class_='col-xs-6 col-sm-4 col-md-1')
        for element in am_list:
            if element.find('i', class_='fa fa-arrows-alt') != None:
                adv_size = element.span.text
                break
            elif element.find('i', class_='fa fa-car') != None:
                adv_park = element.span.text
                continue
            elif element.find('i', class_='fa fa-shower') != None:
                adv_bath = element.span.text
                continue
            elif element.find('i', class_='fa fa-bed') != None:
                adv_bed = element.span.text
                continue
            else:
                adv_park ='NotFound'
                adv_bath = 'NotFound'
                adv_bed = 'NotFound'
                adv_size = 'NotFound'
        #Features
        features = advert_soup.find_all('p', class_='col-xs-12 col-sm-6')
        feature_list = []
        for p in features:
            feature_list.append(p.text)
        features = '/'.join(feature_list)

        output_file.write(advert_title + "," + advert_address + "," + adv_price + "," + adv_condofee + "," +
            adv_park + "," + adv_bath + "," + adv_bed + "," + adv_size + "," + features + "\n")

    output_file.close()
    driver.quit()

if __name__ == '__main__':
    AbreuImoveisScraper()
