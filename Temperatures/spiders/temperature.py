import scrapy
from time import sleep
import os.path
from time import sleep
import json

# Source of this crawlling is www.timeanddate.com

"""
Users have to provide the following information which is within class Temperature:
    start_month
    end_month
    year
    file_name (What name do you want to save file to)

How to run:
    scrapy crawl temperature

Prequestict:
    All of the imoprt library need to be installed
"""
class Temperature(scrapy.Spider):
    name = "temperature"
    start_month = 9
    end_month = 9
    year = 2017
    file_name = "Cambodia_Temperature_Data.csv"
    province_name = ""
    month = ""
    province_nameOnWeb = {}
    province_nameOnWeb['/cambodia/kampong-chhnang/historic'] = "Kampong Chhnang"
    province_nameOnWeb['/@1899273/historic'] = "Banteay Meanchey"
    province_nameOnWeb['/cambodia/battambang/historic'] = "Battambang"
    province_nameOnWeb['/@1831172/historic'] = "Kampong Cham"
    province_nameOnWeb['/@1831132/historic'] = "Kampong Speu"
    province_nameOnWeb['/@1831124/historic'] = "Kampong Thom"
    province_nameOnWeb['/@1831111/historic'] = "Kampot"
    province_nameOnWeb['/@11320725/historic'] = "Kandal"
    province_nameOnWeb['/@1830468/historic'] = "Koh Kong"
    province_nameOnWeb['/cambodia/kratie/historic'] = "Kratié"
    province_nameOnWeb['/@1822210/historic'] = "Oddar Meanchey"
    province_nameOnWeb['/@1822676/historic'] = "Preah Vihear"
    province_nameOnWeb['/@1821301/historic'] = "Pursat"
    province_nameOnWeb['/@1822609/historic'] = "Prey Veng"
    province_nameOnWeb['/@1822449/historic'] = "Ratanakiri"
    province_nameOnWeb['/cambodia/siem-reap/historic'] = "Siem Reap"
    province_nameOnWeb['/cambodia/stung-treng/historic'] = "Stung Treng"
    province_nameOnWeb['/@1821992/historic'] = "Svay Rieng"
    province_nameOnWeb['/@7647532/historic'] = "Takeo"
    province_nameOnWeb['/@1830937/historic'] = "Kep"
    province_nameOnWeb['/cambodia/phnom-penh/historic'] = "Phnom Penh"
    province_nameOnWeb['/cambodia/sihanoukville/historic'] = "Preah Sihanouk"
    province_nameOnWeb['/@7647525/historic'] = "Tboung Khmum"

    month_to_number = {}
    month_to_number['Jan'] = 1
    month_to_number['Feb'] = 2
    month_to_number['Mar'] = 3
    month_to_number['Apr'] = 4
    month_to_number['May'] = 5
    month_to_number['Jun'] = 6
    month_to_number['Jul'] = 7
    month_to_number['Aug'] = 8
    month_to_number['Sept'] = 9
    month_to_number['Oct'] = 10
    month_to_number['Nov'] = 11
    month_to_number['Dec'] = 12


    def construct_link(self,urls,name_onweb):
        number_of_month = self.end_month - self.start_month + 1
        url_data = ""
        url_result = []
        for ind in range(number_of_month):
            self.month = self.start_month+ind
            url_data = urls+str(name_onweb)+"?month="+str(self.start_month+ind)+"&year="+str(self.year)
            url_result.append(url_data)
        return url_result
    def start_requests(self):
        #self.construct_link('https://www.timeanddate.com/weather',self.province_nameOnWeb)
        #urls = [
        #    'https://www.timeanddate.com/weather/@1831172/historic?month=11&year=2017'
        #]
        url = 'https://www.timeanddate.com/weather'
        for key in self.province_nameOnWeb:
            self.province_name = self.province_nameOnWeb[key]
            url_get_data = self.construct_link(url,key)
            for i in range(len(url_get_data)):
                yield scrapy.Request(url=url_get_data[i], callback=self.parse)

    def parse(self, response):
        info = response.xpath('//script/text()').extract()
        #print(len(response.url.split("/")))
        url = response.url
        final_result = "test"

        for key, value in self.province_nameOnWeb.items():
            if key in url:
                self.province_name = value

        for data in info:
            if "var data" in data:
                result = data.replace("var data=","").split(";")
                final_result = result[0]
                break
        json_result = json.loads(final_result)
        temp_detail = json_result['detail']
        #check file first creation
        first_time = False
        if(not os.path.exists(self.file_name)):
            first_time = True

        with open(self.file_name,'a') as open_file:
            lenght = len(temp_detail)
            if first_time:
                open_file.write("Date,Low_Temp,Hi_Temp,Humi,Province\n")
            tracking_ind = 0
            for i in range(len(temp_detail)):
                date = temp_detail[tracking_ind]['ds'].split(",")[1]
                #print(temp_detail[tracking_ind])
                #print(temp_detail[tracking_ind]['ds'])
                date_split = date.split(" ")
                for key,value in self.month_to_number.items():
                    if key in date_split[2].strip():
                        if value < 10:
                            self.month = '0'+str(value)
                        else:
                            self.month = str(value)
                if int(date_split[1]) < 10:
                    date_split[1] = '0'+date_split[1]
                final_date = date_split[3]+self.month+date_split[1]
                final_low_temp = 0.0
                final_hi_temp = 0.0
                final_hum = 0.0
                divi = 0
                for k in range(4):
                    if tracking_ind + k >= len(temp_detail):
                        break
                    if not ('templow' in temp_detail[tracking_ind+k]) or not ('temp' in temp_detail[i+k]) or not ('hum' in temp_detail[i+k]):
                        continue
                    low_temp = float(temp_detail[tracking_ind+k]['templow'])
                    hi_temp = float(temp_detail[tracking_ind+k]['temp'])
                    humi = float(temp_detail[tracking_ind+k]['hum'])
                    final_low_temp  = final_low_temp + low_temp
                    final_hi_temp = final_hi_temp + hi_temp
                    final_hum = final_hum + humi
                    divi = divi + 1
                tracking_ind = i + k
                open_file.write(final_date+","+str(final_low_temp/divi)+","+str(final_hi_temp/divi)+","+str(final_hum/divi)+","+self.province_name+"\n")
        #Write Data Into CSV
        #print("Json Result: "+ str(json_result['temp'][1]['temp']))
        #with open('E:\makara\WBO\Temperature Crawling\weathercrawling\weathercrawling\spiders\/text.txt','w') as open_file:
        #    open_file.write(final_result)