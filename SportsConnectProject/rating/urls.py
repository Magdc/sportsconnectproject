from django.urls import path
from . import views

app_name = 'rating'

urlpatterns = [
    path('create/<int:reservation_id>/', views.create_rating, name='create_rating'),
    path('view/<int:rating_id>/', views.view_rating, name='view_rating'),
    path('edit/<int:rating_id>/', views.edit_rating, name='edit_rating'),
    path('facility/<int:facility_id>/', views.facility_ratings, name='facility_ratings'),
    path('my-ratings/', views.my_ratings, name='my_ratings'),
]
