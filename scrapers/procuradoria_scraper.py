import requests
from bs4 import BeautifulSoup
from time import sleep

def get_url_list(page, re_type):
    url_list = []
    #page = 1
    source_url = "http://www.procuradoriadeimoveis.com.br/imoveis.php?pg="+ str(page) +"&&busca=venda&finalidade=venda&cidade=natal&tipo=" + re_type +"&"
    headers = {'User-Agent':'Mozilla/5.0'}

    #while page <= 2:
    soup = BeautifulSoup(requests.get(source_url, headers=headers).text, 'lxml')
    for container in soup.find_all('div', class_='col-sm-6 col-md-4 boxi'):
        #url source of the advert
        re_source = "http://www.procuradoriadeimoveis.com.br/" + container.find('a')['href']
        url_list.append(re_source)
        #page += 1
    return url_list

def procuradoria_scraper(re_type):
    
    filename = "output/rawdata_procuradoria_{}.csv".format(re_type)
    f = open(filename,"a")
    
    TOTAL_PAGES = 36
    for page in range(1,TOTAL_PAGES):
        print("Scraping page {}".format(page))
        url_list = get_url_list(page, re_type)
        #print(url_list)
        for url in url_list:
            headers = {'User-Agent':'Mozilla/5.0'}
            sleep(0.5)
            advert_soup = BeautifulSoup(requests.get(url, headers=headers).text, 'lxml')
            #Advert Title
            advert_title = advert_soup.find('h1', class_='titulo').text.replace(",",".")
            #Advert Address
            #Sale price, removing the last 3 digits
            adv_sale = advert_soup.find_all('div', class_='titulo titulo-2 valor')[0].text[:-3]
            #Advert Condo Fee
            try:
                condofee = advert_soup.find_all('div', class_='titulo titulo-2 valor')[1].text[:-3].replace(",",".")
            except:
                condofee = "NotFound"
            #Find the table containing parking, bed, bath and size
            table = advert_soup.find('table')
            tlist = table.find_all('td')
            adv_bed = tlist[0].text
            adv_bath = tlist[1].text
            adv_park = tlist[2].text
            adv_size = tlist[3].text
            #Features
            try:
                features_div = advert_soup.find('div', class_='caracteristicas row')
                features = features_div.find_all('div', class_='col-lg-4 col-md-6')
                feature_list = []
                for p in features:
                    feature_list.append(p.text)
                features = '/'.join(feature_list)
            except:
                features = "NotFound"
            f.write(advert_title +","+ adv_sale +","+ condofee +","+ adv_bed +","+
            adv_bath +","+ adv_park +","+ adv_size +","+ features + "\n")
            print("Writing {}".format(advert_title))
        sleep(20)
        

if __name__ == '__main__':
    procuradoria_scraper(re_type="apartamento")
    procuradoria_scraper(re_type="casa")