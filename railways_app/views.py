from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
import jwt, datetime
from rest_framework.decorators import api_view
from rest_framework import status
from django.db import transaction

from .serializers import UserSerializer
from .models import User
from django.conf import settings
from .models import Train, Booking
from .serializers import TrainSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }

        return response
    
class UserView(APIView):

    def get(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            raise AuthenticationFailed('Unauthenticated!')

        token = auth_header.split(' ')[1]

        if not token:
            return Response({'error': 'Token not found!'})

        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
class LogoutView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()

        if not user:
            return Response({'error': 'User not found!'})
        
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'User Logged Out Successfully!'
        }
        return response
    


class AddTrainView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')

        api_key = request.headers.get('X-API-Key')
        if api_key != settings.API_KEY:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()

        if not user:
            return Response({'error': 'User not found!'})
        
        if user.is_staff == 0:
            return Response({'error': 'Not Allowed!'})
        
        serializer = TrainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class GetTrainView(APIView):
    def get(self, request, train_name):
        train = Train.objects.filter(name=train_name).first()

        if train is None:
            return Response({'error': 'Train not found'})
        
        serializer = TrainSerializer(train)
        return Response(serializer.data)

class GetSeatAvailabilityView(APIView):
    def get(self, request, source, destination):
        trains = Train.objects.filter(source=source, destination=destination)

        if not trains.exists():
            return Response({'error': 'No Trains Available for this route'})

        data = [{'train_name': train.name, 'available_seats': train.available_seats} for train in trains]
        return Response(data)

@api_view(['POST'])
@transaction.atomic
def book_seat(request, train_name):
    token = request.COOKIES.get('jwt')

    if not token:
        raise AuthenticationFailed('Unauthenticated!')

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Unauthenticated!')

    user = User.objects.filter(id=payload['id']).first()

    if not user:
        return Response({'error': 'User not found!'})
    
    try:
        train = Train.objects.select_for_update().get(name=train_name)
    except Train.DoesNotExist:
        return Response({'error': 'Train not found'}, status=status.HTTP_404_NOT_FOUND)

    if train.available_seats > 0:
        train.available_seats -= 1
        train.save()

        booking = Booking.objects.create(user=user, train=train, seat_number=train.available_seats+1)
        return Response({'error': 'Booking successful', 'seat_number': booking.seat_number, 'booking_id': booking.id})
    else:
        return Response({'error': 'No seats available'})

class GetBookingView(APIView):
    def get(self, request, booking_id):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        
        user = User.objects.filter(id=payload['id']).first()
        if not user:
            return Response({'error': 'User not found!'})

        booking = Booking.objects.filter(id=booking_id).first()

        if not booking:
            return Response({'error': 'Booking not found!'})
        
        if booking.user != user:
            return Response({'error': 'Unauthorized!'})

        data = {
            'name': booking.user.name,
            'train_name': booking.train.name,
            'seat_number': booking.seat_number
        }

        return Response(data)