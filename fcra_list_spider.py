#*---------------------------------------------------------
#*- A Scrapy spider to collect FCRA annual return data from
#*-  https://fcraonline.nic.in/fc3_Amount.aspx
#*- 
#*- 1. Extract the year and state from the passed arguments
#*- 2. Run the spider for all the districts in the state for
#*-    given year
#*- 3. Dump the results in a JSON file
#*----------------------------------------------------------

from lxml import html
import scrapy 
import sys
from bs4 import BeautifulSoup
from urllib.parse import unquote
import re

# build the constants
DIR = "/home/mkonchady/code/spiders/fcra/fcra/spiders"
sys.path.append(DIR)
URL = 'https://fcraonline.nic.in/fc3_Amount.aspx'

# return form data in a dict for the request
def getFormData(response, year = '0', state = '0', district = '0', eventTarget = ''):
    return {
        'DdnListBlockYear': year,
        'DdnListState': state,
        'DdnListdist': district,
        '__EVENTTARGET': eventTarget,
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': unquote(response.css('input#__VIEWSTATE::attr(value)').extract_first()),
        '__VIEWSTATEGENERATOR': unquote(response.css("input#__VIEWSTATEGENERATOR::attr(value)").extract_first()),
        '__VIEWSTATEENCRYPTED': '',
        'ctl00$hidden1': '',
        'ctl00$ddlLanguage': 'en-US',
        'ctl00$ContentPlaceHolder1$HiddenField1': '',
        'ctl00$ContentPlaceHolder1$hdnDetail': '',
        '__ASYNCPOST': 'false'
    }

class FcraDonor(scrapy.Item):
    year = scrapy.Field()
    state = scrapy.Field()
    district = scrapy.Field()
    registration = scrapy.Field()
    name = scrapy.Field()
    address = scrapy.Field()
    amount = scrapy.Field()
    #link = scrapy.Field()

class FcraList(scrapy.Spider): 
    name = 'fcraList' 
    start_urls = [URL] 
    download_delay = 3.0

    # request the states for the year
    def parse(self, response): 
        for year in response.css('select#DdnListBlockYear > option ::attr(value)').extract(): 
            if year == '0':
                continue
            if year == self.select_year:
                yield( scrapy.FormRequest( URL, formdata = getFormData(response, year), \
                    callback=self.parse_state ) )
                  
    # request the districts for each state
    def parse_state(self, response):
        for state in response.css('select#DdnListState > option ::attr(value)').extract():
            if state == '0' or state != self.state_code:
                continue
            year = response.css('select#DdnListBlockYear > option[selected] ::attr(value)' ).extract_first()
            yield(scrapy.FormRequest( URL,  formdata = getFormData(response, year, state), \
                    callback=self.parse_district) )
        
    # request the list of organizations for the district, state, and year                 
    def parse_district(self, response): 
        for district in response.css('select#DdnListdist > option ::attr(value)').extract():
            if district == '0':
                continue
            year = response.css('select#DdnListBlockYear > option[selected] ::attr(value)' ).extract_first()
            state = response.css('select#DdnListState > option[selected] ::attr(value)' ).extract_first()
            yield(scrapy.FormRequest.from_response( response,  formname = 'form1',
                    formdata = getFormData(response, year, state, district),
                    clickdata = {'name': 'Button1', 'value': 'Submit'},
                    callback = self.parse_table) )


    def parse_table(self, response):
        # extract the year, state, and district
        soup = BeautifulSoup(response.text, features="lxml")
        year = soup.find("span", {"id": "lblblockyear"}).text
        year = re.sub("^Year\s*:\s* ", '', year)
        state = soup.find("span", {"id": "lblstate"}).text
        state = re.sub("^State\s*:\s*", '', state)
        district = soup.find("span", {"id": "lbldist"}).text
        district = re.sub("^District\s*:\s*", '', district)
        # check if the table is blank for the district
        blank = soup.find("span", {"id": "lblerror"})
        if blank is None:
            table = soup.find("table", {"id": "GridView1"})
            first_row = True
            for row in table.find_all('tr'):
                if first_row:
                    first_row = False
                    continue        
                column_num = 0
                registration = ""
                name = ""
                address = ""
                amount = ""
                link = ""
                for column in row.find_all('td'):
                    if column_num == 0:
                        pass
                    elif column_num == 1:
                        registration = column.text
                    elif column_num == 2:
                        name = column.text
                    elif (column_num == 3):
                        address = column.text
                    elif (column_num == 4):
                        amount = column.text
                    column_num = column_num + 1
                yield FcraDonor(year = year, state = state, district = district, \
                    registration = registration, name = name, address = address, amount = amount)
        else:
            yield FcraDonor(year = year, state = state, district = district, \
                registration = '-1', name = '', address = '', amount = '0')
