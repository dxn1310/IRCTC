from django.urls import path
from .views import RegisterView, LoginView, UserView, LogoutView, GetTrainView, AddTrainView, GetSeatAvailabilityView, GetBookingView
from .views import book_seat

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('user/', UserView.as_view()),
    path('logout/', LogoutView.as_view()),

    path('add_train/', AddTrainView.as_view()),
    path('train/get_train/<str:train_name>/', GetTrainView.as_view()),
    path('train/get_seat_availability/<str:source>/<str:destination>/', GetSeatAvailabilityView.as_view()),
    path('book_seat/<str:train_name>/', book_seat, name='book_seat'),
    path('get_booking/<int:booking_id>/', GetBookingView.as_view()),
]