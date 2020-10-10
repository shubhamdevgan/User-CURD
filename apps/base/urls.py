from rest_framework.routers import DefaultRouter,SimpleRouter
from django.conf.urls import include,url
from django.urls import path
from apps.base.views import *
# from .admin_apiviews import VendorViewset


router = DefaultRouter() 
router.register("login",LoginUser,"login")
router.register('register',RegisterUser,'register')


urlpatterns = [
    path('userlist/', UserListView.as_view(), name='user-list'),
    path('user/<int:id>/', UserGetView.as_view(), name='user-single'),
    
    path('changepassword/', ChangePasswordView.as_view(), name='change-password'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    path('editprofile/<int:id>', EditProfile.as_view(), name='edit-profile'),

] + router.urls


