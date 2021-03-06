from . import models
from . import serializers
from rest_framework import permissions
from . import permissions as my_permissions
from wm_assignment import settings
from .models import BusStop
import urllib2
import json

from django.contrib.auth import authenticate, login, logout, get_user_model
from rest_framework import permissions, authentication, status, generics
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry, LineString, Point, Polygon
from rest_framework.authtoken.models import Token
# from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator


class UsersList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.UserOtherSerializer

    def get_queryset(self):
        return get_user_model().objects.all().order_by("username")

    def get_serializer_context(self):
        return {"request": self.request}

class busStopList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.stopSerializer

    def get_queryset(self):
        return BusStop.objects.all()

    def get_serializer_context(self):
        return {"request": self.request}


class UserMe_R(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.UserOtherSerializer

    def get_object(self):
        return get_user_model().objects.get(email=self.request.user.email)


class UserOther_R(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        if "uid" in self.kwargs and self.kwargs["uid"]:
            users = get_user_model().objects.filter(id=self.kwargs["uid"])
        elif "email" in self.kwargs and self.kwargs["email"]:
            users = get_user_model().objects.filter(email=self.kwargs["email"])
        else:
            users = None
        if not users:
            self.other = None
            raise exceptions.NotFound
        self.other = users[0]
        return self.other

    def get_serializer_class(self):
        if self.request.user == self.other:
            return serializers.UserMeSerializer
        else:
            return serializers.UserOtherSerializer


class UpdatePosition(generics.UpdateAPIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.UserMeSerializer

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UpdatePosition, self).dispatch(*args, **kwargs)

    def get_object(self):
        return get_user_model().objects.get(email=self.request.user.email)

    def perform_update(self, serializer, **kwargs):
        try:
            lat1 = float(self.request.data.get("lat", False))
            lon1 = float(self.request.data.get("lon", False))
            # lat2 = float(self.request.query_params.get("lat", False))
            # lon2 = float(self.request.query_params.get("lon", False))
            if lat1 and lon1:
                point = Point(lon1, lat1)
            # elif lat2 and lon2:
            #     point = Point(lon2, lat2)
            else:
                point = None

            if point:
                # serializer.instance.last_location = point
                serializer.save(last_location = point)
            return serializer
        except:
            pass


# Endpoint for logging in securely
@api_view(["GET", ])
@permission_classes((permissions.AllowAny,))
def token_login(request):
    if (not request.GET["username"]) or (not request.GET["password"]):
        return Response({"detail": "Missing username and/or password"}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=request.GET["username"], password=request.GET["password"])
    if user:
        if user.is_active:
            login(request, user)
            try:
                my_token = Token.objects.get(user=user)
                return Response({"token": "{}".format(my_token.key)}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"detail": "Could not get token"})
        else:
            return Response({"detail": "Inactive account"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"detail": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

# Calls the public endpoint for all the bus stops that are used by dublin bus
# and sends it to the application
# results limit to 100 by choice as takes a while to load if all bus stops are pulled
@api_view(["GET", ])
@permission_classes((permissions.AllowAny,))
@csrf_exempt
def getBusStops(request):
    url = 'https://data.dublinked.ie/cgi-bin/rtpi/busstopinformation?operator=bac&maxresults=100' #limit results to 100
    file = urllib2.urlopen(url)
    data = file.read()
    file.close()

    return Response({"data": data}, status=status.HTTP_200_OK)

# Uses the public endpoint to get the timetable information of a bus stop using the stop id
@api_view(["GET", ])
@permission_classes((permissions.AllowAny,))
@csrf_exempt
def getStopSchedule(request):
    stopid = request.GET["stopid"]
    url = 'https://data.dublinked.ie/cgi-bin/rtpi/realtimebusinformation?stopid=' + str(stopid) + '&format=json'
    file = urllib2.urlopen(url)
    data = file.read()
    file.close()

    return Response({"data": data}, status=status.HTTP_200_OK)

# REST endpoint to register a new user
# takes in username,password,firstname,lastname,email
@api_view(["GET", ])
@permission_classes((permissions.AllowAny,))
@csrf_exempt
def signup(request):
    print (request.GET)

    print("first bp hit")
    if (not request.GET["username"]) or (not request.GET["password"] or (not request.GET["email"])):
        return Response({"detail": "Missing username and/or password and/or email"}, status=status.HTTP_400_BAD_REQUEST)
        print("no values")
    try:
        user = get_user_model().objects.get(username=request.GET["username"])
        if user:
            print("user already exists")
            return Response({"detail": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
    except get_user_model().DoesNotExist:
        user = get_user_model().objects.create_user(username=request.GET["username"])

        # Set user fields provided
        print(request.GET["password"] + request.GET["firstname"] + request.GET["lastname"] + request.GET["email"])
        user.set_password(request.GET["password"])
        user.first_name = request.GET["firstname"]
        user.last_name = request.GET["lastname"]
        user.email = request.GET["email"]
        user.save()
        print("done")

    return Response({"detail": "Successfully created"}, status=status.HTTP_201_CREATED)

