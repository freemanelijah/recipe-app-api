"""
URL mappings for the user API.
"""
from django.urls import path
from user import views


# To be used with reverse function to generate the URL.
# test_user_api.py
# CREATE_USER_URL = reverse('user:create')
app_name = 'user'
urlpatterns = [
    # Django expects a function for the second parameters. as_view() method to get the
    # view function. This is how rest_framework converts the class based view into django supported
    # function view.
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
]
# View needs to be connected to the main app.