from django.shortcuts import render
from backend_db.models import ActualProduceElectricity, HistoricWind, WindFarmData, WindFarmDetailData, SolarFarmDetailData, SolarEnergyData, GSPLocation
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.generics import GenericAPIView
from .serializers import RegisterSerializer, MyTokenObtainPairSerializer
from rest_framework import permissions, status
import pytz
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_required
from .Wind_Turbine_Model.generic_wind_turbines_from_lib import get_all_generic_turbines
import numpy as np
from .Turbine import Turbine
from .WeatherSeries import WeatherSeries
from datetime import datetime, timedelta
from dateutil import parser
from rest_framework_simplejwt.views import TokenObtainPairView
import math

class PowerForecastViewSet(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format = None):
        """ On receiving a post request, generates power forecasts for the given turbine
            at the given lat and long

        Args:
            request (HTTPRequest): the latitude and longitude,
                                   the turbine data (hubHeight, 2D array tableData of wind speeds and projected power output)
            format (_type_, optional): _description_. Defaults to None.

        Returns:
            A Json response with the power forecasts as a 2D array of lists
        """
        hub_height = self.request.data['hubHeight']
        longitude = self.request.data['longitude']
        latitude = self.request.data['latitude']
        number_of_turbines = self.request.data['numOfTurbines']
        
        #table data is given as array of tuples(formated as arrays), 1st col is wind_speeds and 2nd is power_curve 
        wind_speeds, power_curve = np.array(request.data['tableData']).T

        # Get weather forecasts for the given lat and long
        weather = WeatherSeries(longitude, latitude, get_forecasts_on_init = True)
        weather_df = weather.forecasts
        
        # no forecasts found
        if weather_df.empty:
            return JsonResponse({'message' : "Could not find weather forecasts"}, status = 500)
        
        # will raise a TypeError exception if data type passed is wrong
        try:
            wind_turbine = Turbine(hub_height, wind_speeds, power_curve * 1000, number_of_turbines, model_on_create=True)
        except TypeError as e:
            return JsonResponse({'message' : str(e)}, status = 400)
        
        wind_turbine.generate_power_output(weather_df)
        power_output = wind_turbine.power_output
        
        response = {}

        # convert power forecast into a 2d Array of datetime, power_output
        response['power_forecast'] = [list(pair) for pair in zip(list(power_output.index) , list(power_output['feedin_power_plant'] / 1000))]
        
        return JsonResponse(response, safe = False)

class GenericWindTurbineViewSet(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format = None):
        """ Generates predefined power curves

        Args:
            reqeust : None
            format (_type_, optional): _description_. Defaults to None.

        Returns:
            JsonResponse of the wind turbines and associated power curves
        """
        # Convert to a dictionary of values to allow for Json response

        generic_turbines = get_all_generic_turbines()

        return JsonResponse(generic_turbines, safe = False)



def get_closest_coords(long, lat):
    return np.clip(round(long*4)/4, -7, 3), np.clip(round(lat*4)/4, 50, 59)

class HistoricWindViewSet(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format = None):
        longitude, latitude = get_closest_coords(self.request.data['longitude'], self.request.data['latitude'])
        date_format = '%Y-%m-%d'
        start_date = datetime.strptime(self.request.data['start_date'], date_format).replace(tzinfo=pytz.UTC)
        end_date = datetime.strptime(self.request.data['end_date'], date_format).replace(tzinfo=pytz.UTC)
        historic_wind_data = HistoricWind.objects.filter(date_val__lte=end_date, date_val__gte=start_date, longitude = longitude, latitude = latitude).values_list('date_val', 'wind_speed')
        if (historic_wind_data.exists()):
            return JsonResponse(list(historic_wind_data), safe = False)
        return JsonResponse({'message' : 'Could not find any data for these items and geolocations'}, status = 500)



class UserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        user = User(username=self.request.data['username'],
                            email=self.request.data['email'],
                            password=self.request.data['password'],
                            first_name=self.request.data['first_name'],
                            last_name=self.request.data['last_name'])

        user.save()
        return Response(request.data['username'])


def event_stream(data):
    data_len = len(data)
    start = 0
    next_set = 500
    while True:
        if next_set > data_len:
            next_set = data_len
        yield{f'{data[start:next_set]}'}
        start = next_set + 1
        next_set = next_set + 500


class GeolocationsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format = None):
        """Finds all available wind farms

        Args:
            None

        Returns:
            List of the farm data and their metadata for both smaller and larger (detail) data set
        """     
        
        wind_farms = WindFarmData.objects.all().values_list('windfarm_data_id',
                                                        'longitude',
                                                        'latitude',
                                                        'hub_height',
                                                        'number_of_turbines',
                                                        'turbine_capacity',
                                                        'is_onshore',)
    

        
        response = {}
        
        detail_wind_farms = WindFarmDetailData.objects.filter(longitude__isnull = False, 
        latitude__isnull = False,  latitude__lte=59, operator__isnull = False ,
        turbine_height__isnull = False, number_of_turbines__isnull = False, 
        sitename__isnull = False).values_list('id', 'latitude', 'longitude','operator',
        'sitename','is_onshore','turbine_height','number_of_turbines','turbine_capacity',
        'development_status',# 'address','region','country',
        )
    
        response['detail_windfarm_data'] = list(detail_wind_farms)
        response['core_windfarm_data'] = list(wind_farms)
        return JsonResponse(response, safe = False)


class RegisterApiView(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes= (permissions.AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

class SolarFarmGeolocationView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format = None):
        # Some have invalid longitude(infinity), remove with filter
        solar_farms = SolarFarmDetailData.objects.filter(longitude__lte=59).values_list('operator',
                                                            'sitename',
                                                            'development_status',
                                                            'mounting_type_for_solar',
                                                            'address',
                                                            'region',
                                                            'country',
                                                            'latitude',
                                                            'longitude',
                                                            )
        
        return JsonResponse(list(solar_farms), safe = False)

class WindFarmDataByArea(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format = None):
        """Get all available wind farm data for a specified area

        Args:
            request (_type_): min_latitude : float
                              max_latitude: float,
                              min_longitude: float,
                              min_latitude: float 
                              
            format (_type_, optional): _description_. Defaults to None.

        Returns:
           JsonResponse of all available data in the speicfied area, including the total number of turbines and average hub height
        """
        max_lat, max_long = request.data['max_latitude'], request.data['max_longitude']
        min_lat, min_long = request.data['min_latitude'], request.data['min_longitude']
        
        
        # Find all wind farms in the specified coordinate range
        wind_farms = WindFarmData.objects.filter(latitude__gte=min_lat,
                                                latitude__lte=max_lat,
                                                longitude__gte=min_long,
                                                longitude__lte=max_long)


        
        # Holds the data to be returned
        response = {}
        response['wind_farms'] = {}
        response['total_turbines'] = 0
        response['total_turbine_capacity'] = 0
        
        # If no windfarms found in area, set all to default value and return
        if len(wind_farms) == 0:
            response['average_hub_height'] = 0
            return JsonResponse(response, safe = False)
        
        response['average_hub_height'] = []

        # Go through all the wind turbines found and add them up to the response dict
        for farm in wind_farms:
            longitude = farm.longitude
            latitude = farm.latitude
            hub_height = farm.hub_height
            number_of_turbines = farm.number_of_turbines
            turbine_capacity = farm.turbine_capacity
            farm_id = farm.windfarm_data_id

            # Format wind farm data for each individual wind farm
            response['wind_farms'][farm_id] = {   'longitude' : longitude,
                                                                'latitude' : latitude,
                                                                'hub_height' : hub_height,
                                                                'number_of_turbines' : number_of_turbines,
                                                                'turbine_capacity' : turbine_capacity,
                                                                'is_onshore' : farm.is_onshore,}
            response['total_turbines'] += number_of_turbines
            response['total_turbine_capacity'] += farm.turbine_capacity
            response['average_hub_height'].append(hub_height)
            
            
        
        
        
        return JsonResponse(response, safe = False)

class SolarHistoricData(APIView):
    permission_classes = [permissions.AllowAny]

    # Return the distance between two points using pythagora's theorem
    def __distsance_between_points(self, x1, x2, y1, y2):
        return math.sqrt( (x1 - x2)**2 + (y1-y2)**2 )
    
    def post(self, request, format = None):
        latitude = int(self.request.data['latitude'])
        longitude = int(self.request.data['longitude'])
        gsp_long_lat = GSPLocation.objects.all()
        gsp_in_db = SolarEnergyData.objects.order_by().values_list('gsp_id').distinct()
        gsp_distinct = []
        for gsp in gsp_in_db:
            gsp_distinct.append(gsp[0])

        closest_gsp_id = None
        closest_gsp_dist = math.inf


        if gsp_long_lat.exists():
            for row in gsp_long_lat:
                if row.gsp_id in gsp_distinct:
                    dist = self.__distsance_between_points(x1 = longitude, x2 = row.gsp_lon, y1 = latitude, y2 = row.gsp_lat)
                    if dist < closest_gsp_dist:
                        print(dist, closest_gsp_id, row.gsp_id)
                        closest_gsp_id = row.gsp_id
                        closest_gsp_dist = dist
        else:
            JsonResponse({'message' : 'Could not find any data' }, status = 500)
        
        date_format = '%Y-%m-%d'
        start_date = datetime.strptime(self.request.data['start_date'], date_format)
        
        # End date will be set to 00:00:00, so increase day by one to set to end of day/ start of next day
        end_date = datetime.strptime(self.request.data['end_date'], date_format)
        end_date += timedelta(days = 1)
        
        historic_solar_data = list(SolarEnergyData.objects.filter(gsp_id = closest_gsp_id, datetime_gmt__lte=end_date, datetime_gmt__gte=start_date).values_list('datetime_gmt', 'generation_mw'))
        if len(historic_solar_data) == 0:
            return JsonResponse({'message' : 'Could not find any data for these dates and locations'}, status = 500)
        return JsonResponse(historic_solar_data, safe=False)
        
        
        
        

@csrf_exempt
@login_required
def get_elexon(request):
    context_dic = {}
    try:
        elexon_data = ActualProduceElectricity.objects.all()
        context_dic = {'elexon_data': elexon_data}
        return render(request, 'show_elexon/', context=context_dic)
    except ActualProduceElectricity.DoesNotExist:
        print(f"The ActualProduceElectricity is not exist")
        return render(request, 'get_elexon/', context=context_dic)


@csrf_exempt
@login_required
def get_elexon_by_date(request, date):
    context_dic = {}
    try:
        elexon_data = ActualProduceElectricity.objects.get(settlement_date=date)
        context_dic = {'elexon_data': elexon_data}
        return render(request, 'show_elexon/', context=context_dic)
    except ActualProduceElectricity.DoesNotExist:
        print(f"The ActualProduceElectricity is not exist")
        return render(request, 'get_elexon/', context=context_dic)
