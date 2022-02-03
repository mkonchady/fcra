#*------------------------------------------
# run the FCRA spider one state at a time
# for a given year
#*------------------------------------------

import os
from scrapy.cmdline import execute
import time
import subprocess

state_codes = { 
    "24": "andaman", "01": "andhra_pradesh", "31": "arunachal_Pradesh", \
    "02": "assam", "03": "bihar", "29": "chandigarh", "32": "chhattisgarh", \
    "26": "dadra", "35": "daman", "23": "delhi", "27": "goa", \
    "04": "gujarat", "17": "haryana", "18": "himachal_pradesh",  "15": "kashmir", \
    "33": "jharkhand", "09": "karnataka", "05": "kerala", "25": "lakshwadeep", \
    "06": "madhya_pradesh", "08": "maharashtra", "19": "manipur", "21": "meghalaya", \
    "30": "mizoram", "16": "nagaland", 
    "10": "orissa", "28": "pondicherry", \
    "11": "punjab", "12": "rajasthan", "22": "sikkim", "07": "tamil_nadu", "36": "telangana", \
    "20": "tripura", "13": "uttar_pradesh", "34": "uttarakhand", "14": "west_bengal" \
}

SELECT_YEAR = '2020-2021'
DIR = "/home/mkonchady/code/spiders/fcra"
os.chdir(DIR)

# build the JSON file one state at a time
for state_code in state_codes:
    state_name = state_codes[state_code]
    try:
        command = ['scrapy', 'crawl', 'fcraList', '-o', state_name + '.json',
                '-a','state_code=' + state_code, '-a', 'select_year=' + SELECT_YEAR]
        spider = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        f = open(DIR + "/" + state_name + ".txt", "w")  # save the STDERR output
        for line in str(spider.stderr).split('\\n'):
            f.write(line + '\n')
        f.close()
        print ("Finished " + str(state_name))
    except SystemExit:
        pass
    time.sleep(10)  # wait for 10 seconds before the next state
