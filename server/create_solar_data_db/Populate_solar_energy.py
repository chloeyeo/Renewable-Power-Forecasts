import os
import sys

sys.path.append(os.path.abspath(os.path.join(__file__, *[os.pardir]*2))) # append root directory to sys.path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

import django
django.setup()

from backend_db.models import SolarEnergyData
from datetime import datetime
import pytz
from pvlive_api import PVLive

START_YEAR = 2020
START_MONTH = 1
START_DAY = 1

END_YEAR = 2021
END_MONTH = 1
END_DAY = 1

ENTITY_ID = 0

pvl = PVLive()

solar_df = pvl.between(start=datetime(START_YEAR, START_MONTH, START_DAY, tzinfo=pytz.utc), end=datetime(END_YEAR, END_MONTH, END_DAY, tzinfo=pytz.utc), dataframe=True, entity_id = 1).sort_values(by = ['datetime_gmt'])

solar_dict = solar_df.to_dict(orient = 'index')

def main():
    for row in solar_dict:
        data_dict = solar_dict[row]
        SolarEnergyData.objects.create(**data_dict)
        print(f"Solar Energy GSP: {data_dict['gsp_id']} Time: {data_dict['datetime_gmt']} inserted")
main()