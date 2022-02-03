# FCRA  

Indian NGOs receiving foreign funds have faced more government scrutiny and requirements. The code in the repository includes the Python code to download annual returns filed by Indian NGOs receiving foreign funds from the [Indian FCRA online website] (https://fcraonline.nic.in/home/index.aspx)

1. runner.py and fcra_list_spider.py

The collected data is stored in JSON files and a Python script is used to store the data in a database table in the following format

|Registration|Name|Year|State|District|Address|USD Received|
|------------|----|----|-----|--------|-------|------------|
|1234567|Aam Foundation|2020-2021|Delhi|Delhi|.....|???|

2. create_db.py

The data collected from the Python code is in .csv format

3. database.csv
4. christian_names.csv

