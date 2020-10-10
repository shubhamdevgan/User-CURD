from django.shortcuts import render
from ..base.serializers import *
from ..base.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework.decorators import permission_classes,authentication_classes


# user list all records
class UserListView(APIView):
    
    def post(self, request,format=None):
        try:
            page = int(request.data.get('page',1))
            limit = int(request.data.get('limit',10))
            start = (page - 1) * limit
            end = start + limit
            
            search_param = request.data.get('search_param')
            
            order_by = "id"

            user_qs = User.objects.all().order_by(order_by)
            total_record = len(user_qs)

            # searching data
            if search_param:
                filter_data_qs = user_qs.filter(Q(full_name__icontains = search_param) |
                                                    Q(phone_number__icontains = search_param) |
                                                    Q(email__icontains = search_param)).order_by(order_by)
                
                filter_record = len(filter_data_qs)
                list_with_pagelimit = filter_data_qs[start:end]
                serializer = UserSerializers(list_with_pagelimit, many=True, context={'request':request})
                serializer_data = serializer.data
                
                
            else:
                list_with_pagelimit = user_qs[start:end]
                filter_record = len(list_with_pagelimit)
                serializer = UserSerializers(list_with_pagelimit, many=True, context={'request':request})
                serializer_data = serializer.data
            
        except Exception as e:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'error':'Somthing went wrong',
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if len(serializer_data) == 0:
            response = {'status_code' : status.HTTP_404_NOT_FOUND,'message' : 'NO DATA FOUND.'}
            return Response(response, status.HTTP_404_NOT_FOUND)  
        else:
            msg = 'Data fetch succesfully'   

        response = {
            'status_code':status.HTTP_200_OK,
            'data': serializer_data,
            'total_record':total_record,
            'filter_record':filter_record,
            'message':msg
        }
        return Response(response, status=status.HTTP_200_OK)

# user single record fetch
class UserGetView(APIView):
    def get(self, request, id, format=None):
        try:
            user_obj = User.objects.get(id=id)
        except:
            response = {
                'status' : status.HTTP_404_NOT_FOUND,
                'message' : 'User not found!'
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializers(user_obj)
        

        response = {
            'status' : status.HTTP_200_OK,
            'message': 'Data fetch succesfully',
            'data' : serializer.data,
        }
        
        return Response(response, status=status.HTTP_200_OK)
       

class EditProfile(APIView):
    
    def put(self, request, id, format=None):
        try:
            user_obj = User.objects.get(id=id)
        except:
            response = {
                'status' : status.HTTP_404_NOT_FOUND,
                'message' : 'User not found!'
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        shipping_address_obj = user_obj.address

        fullname = request.data.get("full_name")
        phone_no = request.data.get('phone')
        email = request.data.get('email')
        address = request.data.get('address')
        city = request.data.get('city')
        state = request.data.get('state')
        country = request.data.get('country')
        zipcode = request.data.get('zipcode')
        password = request.data.get('password')


        user_obj.full_name = fullname
        user_obj.phone_no = phone_no
        user_obj.email = email
        user_obj.set_password(password)
        user_obj.save()

        shipping_address_obj.address = address
        shipping_address_obj.city = city
        shipping_address_obj.state = state
        shipping_address_obj.country = country
        shipping_address_obj.zipcode = zipcode
        shipping_address_obj.save()
        


        response = {
            'status' : status.HTTP_200_OK,
            'message' : "User details updated!",
                }
        return Response(response, status=status.HTTP_200_OK)
        
