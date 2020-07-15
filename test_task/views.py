from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from test_task.serializers import *
from test_task.models import Box, Store
from test_task.permissions import IsStaffPermission, IsStaffAndSelf
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import  IsAuthenticated

# parameters for calculations
average_area = 1000
average_volume = 2000
overall_box_create_limit = 1000
box_create_limit = 100

# create API
class BoxCreateAPIView(generics.CreateAPIView):
    serializer_class = BoxCreateSerializer
    queryset = Box.objects.all()
    # only staff members can create BOX so permission check is added for staff
    permission_classes = [IsStaffPermission, IsAuthenticated]
    # token authentication provided by DRF to authenticate
    authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):
        try:
            # getting the data send by user
            _data = request.data.copy()

            # to calculate the no of boxes created in a week we need to find boxes created between today and 7 days back
            d = datetime.today() - timedelta(days=7)
            count = Box.objects.filter(Q(created_by=request.user) & Q(created_on__gte =d)).count()
            overall_count = Box.objects.filter(Q(created_on__gte =d)).count()

            # will return failed if no exceeds///it restrict user from creating boxes out of range
            if overall_count+1 > overall_box_create_limit:
                return Response(
                    {"message": f"Cannot create more than {overall_box_create_limit} box in a week", "status": 400, "statusType": "failed"})

            if count+1 > box_create_limit:
                return Response(
                    {"message": f"Cannot create more than {box_create_limit} box in a week", "status": 400, "statusType": "failed"})

            l = int(_data['length'])
            b = int(_data['width'])
            h = int(_data['height'])

            # formula to get area and volume
            area = 2 * (l * b + b * h + l * h)
            volume = l * b * h

            # area cannot be greater then benchmark
            if area > average_area:
                return Response({"message": f"Area cannot exceed {average_area}", "status": 400, "statusType": "failed"})

            # volume cannot be greater then benchmark
            if volume > average_volume:
                return Response({"message": f"Volume cannot exceed {average_volume}", "status": 400, "statusType": "failed"})

            serializer = self.get_serializer(data=_data)
            # checking if there are errors in data
            if serializer.is_valid():
                obj = self.perform_create(serializer, area, volume)
                # store = Store.objects.filter(employee=request.user).first()
                # if store is None:
                #     store = Store.objects.create(employee=request.user)
                # store.box.add(obj)
                # obj.area = area
                # obj.volume=volume
                # obj.save()
                return Response({"message": "Success",'data':serializer.data, "status": 200, "statusType": "success"})
        except Exception:
            # if any error occur then it will return failed
            return Response({"message": "something bad happened", "status": 400, "statusType": "failed"})

    def perform_create(self, serializer, area, volume):
        # saving area and volume of box
        return serializer.save(created_by=self.request.user, area=area, volume=volume)

# to update the BOX
class UpdateBoxAPIView(generics.UpdateAPIView):
    lookup_field = 'pk'
    serializer_class = BoxCreateSerializer
    queryset = Box.objects.all()
    # only staff can update the box..
    permission_classes = [IsStaffPermission, IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def put(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        instance = self.get_object()
        data = request.data
        serializer = self.get_serializer(instance, data=data)

        # created date and created by cannot be changed
        if 'created_on' in data:
            return Response({"status": 200, 'data': "You don't have permission to change create date of the box", "statusType": "failed"})

        if 'created_by' in data:
            return Response({"status": 200, 'data': "You don't have permission to change user of the box", "statusType": "failed"})

        if serializer.is_valid():
            serializer.save()
            return Response({"status": 200, 'data': serializer.data, "statusType": "success"})
        else:
            return Response({"status": 200, "message": serializer.errors['non_field_errors'][0] if 'non_field_errors' in serializer.errors else
            serializer.errors, "statusType": "success"})


# delete api
class DeleteBox(generics.DestroyAPIView):
    queryset = Box.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            # other users cannot delete box who didn't create BOX
            if instance.created_by != request.user:
                return Response({"message": "You don't have permission to delete this Box", "status": 400, "statusType": "failed"})
            instance.delete()
            return Response({"message": "Deleted Successfully", "status": 200, "statusType": "success"})
        except:
            return Response({"message": "Not found", "status": 400, "statusType": "failed"})

# ALL boxes api
class BoxList(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    serializer_class = BoxListSerializerUser
    queryset = Box.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    # filters we can add in the query to get required data
    filterset_fields = {
        'length': ['gte', 'lte', 'exact', 'gt', 'lt'],
        'width': ['gte', 'lte', 'exact', 'gt', 'lt'],
        'height': ['gte', 'lte', 'exact', 'gt', 'lt'],
        'area': ['gte', 'lte', 'exact', 'gt', 'lt'],
        'volume': ['gte', 'lte', 'exact', 'gt', 'lt']
    }

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()

            if request.user.is_staff:
                serializer = BoxSerializer(queryset, many=True, context={'request': request})
            else:
                serializer = self.get_serializer(queryset, many=True, context={'request': request})
            data = {"message": "", "statusType": "success", "status": 200, "detail": {"boxes": serializer.data}}
            return Response(data)
        except Exception:
            return Response({"message": "something bad happened", "statusType": "failed", "status": 400})

    def get_queryset(self, *args, **kwargs):
        return Box.objects.all()

# API to get my created  boxes
class ListMyboxes(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    # only staff members can see his created boxes
    permission_classes = [IsStaffPermission, IsAuthenticated]
    serializer_class = BoxSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'length': ['gte', 'lte', 'exact', 'gt', 'lt'],
        'width': ['gte', 'lte', 'exact', 'gt', 'lt'],
        'height': ['gte', 'lte', 'exact', 'gt', 'lt'],
        'area': ['gte', 'lte', 'exact', 'gt', 'lt'],
        'volume': ['gte', 'lte', 'exact', 'gt', 'lt'],
    }

    def get(self, request, *args, **kwargs):
        try:
            # id = int(kwargs.get('pk'))
            # user = User.objects.filter(id=id)
            #
            # if request.user != user:
            #     return Response({"message": "You don't have permission to access these records", "statusType": "failed", "status": 400})
            #
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True, context={'request': request})
            data = {"message": "", "statusType": "success", "status": 200, "detail": {"boxes": serializer.data}}
            return Response(data)
        except Exception:
            return Response({"message": "something bad happened", "statusType": "failed", "status": 400})

    def get_queryset(self, *args, **kwargs):
        # id = int(kwargs.get('pk'))
        # user = User.objects.filter(id=id)
        return Box.objects.filter(Q(created_by=self.request.user))
