#*-----------------------------------------------------------------
#*-  Create a database of all the charities for all the years
#*-----------------------------------------------------------------
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

import os
import json
import sys
import pandas as pd

DIR = "/home/mkonchady/code/spiders/fcra/data/"
sys.path.append(DIR)
import util

# Average INR to USD exchange rate by year
exchange = {}
exchange['2016_2017'] =	67
exchange['2017_2018'] =	64.4
exchange['2018_2019'] =	69.9
exchange['2019_2020'] =	70.4
exchange['2020_2021'] =	74.1

os.chdir(DIR)
db_file_path = os.getcwd() + "/db/fcra.db"

engine = create_engine('sqlite:///' + db_file_path, echo = True)
Base = declarative_base()

# the 9 fields in the charity table
class Charity(Base):
    __tablename__ = "charity"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    category = Column(String)
    year = Column(String)
    state = Column(String)
    district = Column(String)
    registration = Column(String)
    address = Column(String)
    inr_amount = Column(Integer)
    usd_amount = Column(Integer)


# read the list of names and associated category
df = pd.read_csv('./name_cat/christian_names.csv')
category_dict = df.set_index('registration').T.to_dict('list')

# for each year get all the json files and add to the database
Base.metadata.create_all(engine)
YEARS = ['2020_2021', '2019_2020', '2018_2019', '2017_2018', '2016_2017']
charity_rows = []
id = 0
for YEAR in YEARS:
    flist = util.get_filelist(YEAR)
    for file in flist:
        f = open(file)
        data = json.load(f)
        for charity in data:
            registration_num = int(charity['registration'])
            if registration_num == -1:
                continue
            category = category_dict[registration_num][2]   # assign category
            amount = round(float(charity['amount']) / exchange[YEAR])   # convert to usd
            row = Charity(id = id, name = charity['name'], category = category, \
                year = charity['year'], state = charity['state'], \
                district = charity['district'], registration = charity['registration'], \
                address = charity['address'], usd_amount = amount, \
                inr_amount = round(float(charity['amount'])) )
            charity_rows.append(row)
            id = id + 1
        f.close()

Session = sessionmaker(bind=engine)
session = Session()
session.add_all(charity_rows)
session.commit()

print ("done")