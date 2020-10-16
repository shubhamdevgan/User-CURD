from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet,ViewSet
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from apps.base.models import *
from apps.base.serializers import *
from django.contrib.auth import login , logout
from rest_framework.decorators import permission_classes,authentication_classes
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework.views import APIView
from apps.base.authentication import MyCustomAuth



@authentication_classes([])
class LoginUser(ViewSet):
    permission_classes = [AllowAny]
    def create(self,request): 
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email: 
            return Response({
                            'message':'unsuccessfull',
                            'error':'email requried'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if not password:
            return Response({
                            'message':'unsuccessfull',
                            'error':'password requried'
                            },
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request,email=email,password=password)
    
        if user:
            login(request,user)
            token = Token.objects.create(user=user)
            serializers = LoginSerializers(user)    
            return Response(
                {
                    'message':'successfull',
                    'data':serializers.data,
                    'token':token.key
                    },status=status.HTTP_200_OK
                )
            
        else:
            return Response({
                            'message':'unsuccessfull',
                            'error':'wrong user id or password'
                            },status=status.HTTP_400_BAD_REQUEST)
    

    def destroy(self,request,pk=None):
        user = User.objects.filter(pk=pk).first()
    
        if user:
           TokenDelete = Token.objects.filter(user=user).delete()
           logout(request)
           return Response({
                              'message':'successfull',
                              'data':'successfully loged out'
                              },status=status.HTTP_200_OK)
        else:
            return Response({
                            'message':'unsuccessfull',
                            'error':'no such user'
                            }
                            ,status=status.HTTP_400_BAD_REQUEST) 


    def get_permissions(self):
        if self.action == 'create':
            return []
        return super().get_permissions()           

@authentication_classes([])
class RegisterUser(ViewSet):

    def create(self,request):
        email = request.data.get('email')
        password=request.data.get('password')
        confirmpassword = request.data.get('confirmpassword')
        phone_number =request.data.get('phone_number')
        full_name =request.data.get('full_name')

        if not email:
            return Response({
                            'message':'unsuccessfull',
                            'error':'email requried'
                            },status=status.HTPP_400_BAD_REQUEST)
        
        if not password:
            return Response({
                            'message':'unsuccessfull',
                            'error':'password requried'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if not confirmpassword:
            return Response({
                            'message':'unsuccessfull',
                            'error':'confirmpassword requried'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if not phone_number:
            return Response({
                            'message':'unsuccessfull',
                            'error':'phone number requried'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if password != confirmpassword :
            return Response({
                            'message':'unsuccessfull',
                            'error':'password do not match'
                            },status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({
                            'message':'unsuccessfull',
                            'error':'email already exist'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(phone_number=phone_number).exists():
            return Response({
                            'message':'unsuccesfull',
                            'error':'phone number already exist'
                            },status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create(email=email,phone_number=phone_number,full_name=full_name,is_active=True)
        user.set_password(password)
        user.save()

        if user:
            token = Token.objects.create(user=user)
            serializers = LoginSerializers(user)
            login(request,user)
            return Response({
                            'message':'success',
                            'data':serializers.data,
                            'token':token.key
                            },status=status.HTTP_201_CREATED)
        else:
            return Response({
                            'message':'unsuccessfull',
                            'error':'some error has ouccured'
                            },status= status.HTTP_400_BAD_REQUEST)


#Chnage password API
class ChangePasswordView(APIView):
    authentication_classes = (MyCustomAuth,)

    def post(self, request, *args, **kwargs):
    
        if not request.data:
            # Retrun error message with 400 status
            return Response({"message": "Data is required.", "status": status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
    
        if not request.data.get('current_password'):
            # Retrun error message with 400 status
            return Response({"message": "Current Password is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

        if not request.data.get('new_password'):
            # Retrun error message with 400 status
            return Response({"message": "New Password is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)    

        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        user = User.objects.filter(id = request.user.id).first()
        
        if user:
            try:
                if user.check_password(current_password):
                    
                    if current_password == new_password:
                        return Response({"message": "Current password and new password are same.Please enter different password.", "status": status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)    
                    
                    user.set_password(new_password)
                    user.save()
                    return Response({"message": "Password changed successfully.", "status": status.HTTP_200_OK}, status.HTTP_200_OK)
                else:
                    return Response({"message": "Current password is incorrect.", "status": status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"message": "Error occured.", "status": status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Please login to change password.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)    


# User Logout View
class UserLogoutView(APIView):
    authentication_classes = (MyCustomAuth,)

    # def dispatch(self, request, *args, **kwargs):
    #     self.db_name = request.user.db_name
    #     return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


    def destroy(self, request, *args, **kwargs):
        # simply delete the token to force a login
        auth_token = request.META.get("HTTP_AUTHORIZATION")
        auth_token = auth_token.split(' ')[1]

        token = Token.objects.filter(key = auth_token).first()        
             
        if token:
            token.delete()
        
        # Return success message with 200 status
        return Response({"message": "Logout successfully.",
                                    "status": status.HTTP_200_OK}, status.HTTP_200_OK)

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

        fullname = request.data.get("full_name")
        phone_no = request.data.get('phone')
        email = request.data.get('email')
        password = request.data.get('password')

        user_obj.full_name = fullname
        user_obj.phone_no = phone_no
        user_obj.email = email
        user_obj.set_password(password)
        user_obj.save()

        response = {
            'status' : status.HTTP_200_OK,
            'message' : "User details updated!",
                }
        return Response(response, status=status.HTTP_200_OK)
        


