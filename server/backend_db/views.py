from django.shortcuts import render
# from django.http import HttpResponse
# from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from backend_db.models import ActualProduceElectricity, UserProfile, HistoricWind, WindFarmData
from django.http import JsonResponse
from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
)
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet
from .serializers import UserSerializer, HistoricWindSerializer, WindFarmDataSerializer, LoginSerializer, RegisterSerializer
# from rest_framework.decorators import api_view
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_required
from .Wind_Turbine_Model.siemens_2300KW import E_28_2300
import numpy as np
from .Turbine import Turbine
from .WeatherSeries import WeatherSeries

class PowerForecastViewSet(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format = None):
        hub_height = self.request.data['hubHeight']
        longitude = self.request.data['longitude']
        latitude = self.request.data['latitude']
        number_of_turbines = self.request.data['numOfTurbines']

        #table data is given as array of tuples(formated as arrays), 1st col is wind_speeds and 2nd is power_curve 
        wind_speeds, power_curve = np.array(request.data['tableData']).T

        
        #generate Power forecasts
        # power_output = generate_power_forecast( latitude = latitude,
        #                                         longitude= longitude,
        #                                         power_curve = power_curve * 1000, #convert to W from KW
        #                                         wind_speeds = wind_speeds,
        #                                         hub_height = hub_height,
        #                                         number_of_turbines = number_of_turbines).to_frame()
        weather = WeatherSeries(longitude, latitude, get_forecasts_on_init = True)
        weather_df = weather.get_forecasts()
        
        wind_turbine = Turbine(hub_height, wind_speeds, power_curve * 1000, number_of_turbines, model_on_create=True)
        wind_turbine.generate_power_output(weather_df)
        
        power_output = wind_turbine.get_power_output()
        response = {}

        # convert power forecast into a 2d Array of datetime, power_output
        response['power_forecast'] = [list(pair) for pair in zip(list(power_output.index) , list(power_output['feedin_power_plant'])   )]
        return JsonResponse(response, safe = False)

class GenericWindTurbineViewSet(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, reqeust, format = None):
        # Convert to a dictionary of values to allow for Json response
        generic_turbine = {}
        # Create a list of the default names for the turbines, currently only 1 default
        generic_turbine['default_turbines'] = []
        generic_turbine['default_turbines'].append(E_28_2300['name'])

        # convert power curve into a 2D array of wind_speed,power_production
        power_curve = [list(pair) for pair in zip(list(E_28_2300['power_curve']['wind_speed']), list(E_28_2300['power_curve']['value']/1000))]
        generic_turbine['E_28_2300'] = {
            'hub_height' : E_28_2300['hub_height'],
            'power_curve' : power_curve
        }

        return JsonResponse(generic_turbine, safe = False)


class HistoricWindViewSet(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format = None):
        historic_wind_data = HistoricWind.objects.all().values_list('longitude', 'latitude')

        return JsonResponse(list(historic_wind_data), safe = False)


class UserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        user = UserProfile( username=self.request.data['username'],
                            email=self.request.data['email'],
                            password=self.request.data['password'],
                            first_name=self.request.data['first_name'],
                            last_name=self.request.data['last_name'])

        user.save()
        return Response(request.data['username'])


class GeolocationsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        wind_farms = WindFarmData.objects.all().values_list('longitude', 'latitude')
        print("HELLO")
        print(wind_farms)
        
        return JsonResponse(list(wind_farms), safe=False)


# besides calling the serializers in the login, we should also check some invalid situations and give some response messages.
class LoginView(APIView):
        permission_classes = (permissions.AllowAny,)

        def post(self, request, format=None):
            if request.data['username'] and request.data['password']:
                serializer = LoginSerializer(data=self.request.data, context={'request': self.request})
                serializer.is_valid(raise_exception=True)
                user = serializer.validated_data['user']
                if not user:
                    print('A user with this email and password is not found.')
                    return Response({"status": status.HTTP_404_NOT_FOUND, "Token": None})
                login(request, user)
                token = Token.objects.create(user=user)
                return Response({"status": status.HTTP_202_ACCEPTED, "Token": token})
            else:
                print('The email or password is empty in the request data.')
                return Response({"status": status.HTTP_400_BAD_REQUEST, "Token": None})


class RegisterApiView(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# from rest_framework.views import APIView
# from rest_framework.request import Request
# from rest_framework.response import Response
# import {Login} from '../../src/pages/login'
#
# @csrf_exempt
# def register_view(request):
#     if request.method == "POST":
#         username = request.data['username']
#         email = request.data.get("email")
#         password = request.data.get("password")
#         first_name = request.data['first_name']
#         last_name = request.data['last_name']
#         user = authenticate(email=username, password=password)
#         if user:
#             user = UserProfile(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
#             user.save()
#             return JsonResponse({'status': 0})
#         else:
#             print(f"Invalid email or password: email: {email}, password: {password}")
#             return JsonResponse({'status': -1})
#     else:
#         return render(request, 'login/')
#
#
# @csrf_exempt
# def login_view(request):
#     if request.method == "POST":
#         email = request.data.get("email")
#         password = request.data.get("password")
#         user = authenticate(email=email, password=password)
#         if user:
#             login(request, user)
#             return {'status': 0}
#         else:
#             print(f"Invalid email or password: email: {email}, password: {password}")
#             return JsonResponse({'status': -1})
#     else:
#         return render(request, 'login/')


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

# validate password and email
# import urllib library
# from urllib.request import urlopen
  
# # import json
# import json

# # store the URL in url as 
# # parameter for urlopen
# url = "http://localhost:8000/postrequest"
  
# # store the response of URL
# response = urlopen(url)
  
# # storing the JSON response 
# # from url in data
# data_json = json.loads(response.read())
# # Create your views here.
# def register_user(request):
#     try:
#         registered = False
#         # store the URL in url as 
#         # parameter for urlopen
#         url = "http://localhost:8000/postrequest"

#         # store the response of URL
#         response = urlopen(url)
    
#         # storing the JSON response 
#         # from url in data
#         data_json = json.loads(response.read())
#         return data_json
    
#     # try:
#     #     # tells whether registration was successful
#     #     registered = False
#     #     # get data = request from login.js using fetch post
#     #     # password = request.GET.get("password")
#     #     # request is json object

#     #     return JsonResponse(data)
#     except:
#         data = {'registered': False, 'password':'', 'email': ''}
#         return JsonResponse(data)
