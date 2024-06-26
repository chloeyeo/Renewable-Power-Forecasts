from django.db import models
from backend_db.elexon_model import ActualProduceElectricity
from backend_db.open_meteo_model import WeatherForecast
from backend_db.power_forecast import PowerForecast
from backend_db.wind_farm_data import WindFarmData, WindFarmDetailData
from backend_db.solar_energy_data import SolarEnergyData, SolarFarmDetailData, GSPLocation
from django.contrib.auth.models import User
# Create your models here.


class HistoricWind(models.Model):
    wind_data_id = models.IntegerField(primary_key = True, unique = True, auto_created = True)
    height_above_ground = models.IntegerField(blank = False)
    date_val = models.DateTimeField(blank = False)
    longitude = models.FloatField(blank = False)
    latitude = models.FloatField(blank = False)
    u_comp = models.FloatField(blank = False, null = False)
    v_comp = models.FloatField(blank = False, null = False)
    wind_speed = models.FloatField(blank = False)
    
    
    def __str__(self):
        return "{} : ({},{}) : u_comp = {}, v_comp = {}".format(self.date_val.strftime("%Y-%m-%d"), self.latitude, self.longitude, self.u_comp, self.v_comp)