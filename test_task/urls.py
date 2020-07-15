from django.urls import path
from . import views

# apis for CRUD
urlpatterns = [
    path('/create/', views.BoxCreateAPIView.as_view(), name='box-create'),
    path('/update/<pk>/', views.UpdateBoxAPIView.as_view(), name='update-box'),
    path('/list/', views.BoxList.as_view(), name='box-list'),
    path('/list-my-boxes/', views.ListMyboxes.as_view(), name='box-list'),
    path('/delete/<pk>/', views.DeleteBox.as_view(), name='delete'),

]