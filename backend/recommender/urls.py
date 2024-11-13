from django.urls import path
from .views import get_recommendations

urlpatterns = [
    path('recommendations/<str:user_id>/', get_recommendations, name='get_recommendations'),
]
