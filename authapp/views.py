from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
import base64
from django.contrib.auth import authenticate
from authapp.models import User
from authapp.serializers import UserSerializer, PasswordOtpSerializer, SetPasswordSerializer, ChangePasswordSerializer, ResendActivationSerializer, UserActivationSerializer
from rest_framework import status
from .utils import ResponseInfo

# Create your views here.

class Registration(APIView):

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                self.response_format['data'] = serializer.data
                self.response_format['message'] = 'User register succesfully, check you email for active your account.'
                return Response(self.response_format)
            else:
                self.response_format['error'] = serializer.errors
                self.response_format['status'] = status.HTTP_400_BAD_REQUEST
                return Response(self.response_format)
        except Exception as e:
            self.response_format['error'] = str(e)
            self.response_format['status'] = status.HTTP_400_BAD_REQUEST
            return Response(self.response_format)


class LogIn(APIView):

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        content = [email, password]
        if all(content):
            user = User.objects.filter(email=email).first()
            if user is not None:
                if user.is_active == True:
                    check = authenticate(email=email, password=password)
                    if check is not None:
                        token, _ = Token.objects.get_or_create(user=user)
                        data = {}
                        data['token'] = token.key
                        data['user'] = UserSerializer(user).data
                        self.response_format['data'] = data
                        self.response_format['message'] = 'Successfully login'
                        return Response(self.response_format)
                    else:
                        self.response_format['error'] = 'Incorrect password, enter right password'
                        self.response_format['status'] = status.HTTP_400_BAD_REQUEST
                        return Response(self.response_format)
                else:
                    self.response_format["error"] = 'You account is not active yet!'
                    self.response_format["status"] = status.HTTP_400_BAD_REQUEST
                    return Response(self.response_format)                
            else:               
                self.response_format["error"] = 'This email not register, please enter register email!'
                self.response_format["status"] = status.HTTP_400_BAD_REQUEST
                return Response(self.response_format)
        else:
            self.response_format["error"] = 'Please enter email and password!'
            self.response_format["status"] = status.HTTP_400_BAD_REQUEST
            return Response(self.response_format)


class Activate(APIView):

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response

    def get(self,request,email,user_otp):
        dec_email =  email.encode("ascii")
        email_string_bytes = base64.b64decode(dec_email)
        get_email = email_string_bytes.decode("ascii")
        user = User.objects.filter(email=get_email).first()
        serializer = UserActivationSerializer(
            data={
            'user_otp':user_otp, 
            'user':user.id
            }, 
            context = {
                'get_email':get_email, 
                'user_otp':user_otp
                }
            )
        try:
            if serializer.is_valid():
                result = serializer.save()     
                if result == True:
                    self.response_format["message"] = 'Now user is active, Please login!'
                    return Response(self.response_format)
            else:
                self.response_format["error"] = (serializer.errors,'=======')
                self.response_format["status"] = status.HTTP_400_BAD_REQUEST
                return Response(self.response_format)
        except Exception as e:
            self.response_format["error"] = str(e)
            self.response_format["status"] = status.HTTP_400_BAD_REQUEST
            return Response(self.response_format)
            



class ResendActivationLink(APIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response

    def post(self, request):
        serializer = ResendActivationSerializer(data=request.data)
        try:
            if serializer.is_valid():
                result = serializer.save()     
                if result == True:
                    self.response_format["message"] = 'Activation Link has been sent to you email address!'
                    return Response(self.response_format)
            else:
                self.response_format["error"] = serializer.errors
                self.response_format["status"] = status.HTTP_400_BAD_REQUEST
                return Response(self.response_format)
        except Exception as e:
            self.response_format["error"] = str(e)
            self.response_format["status"] = status.HTTP_400_BAD_REQUEST
            return Response(self.response_format)


class LogOut(APIView):
    permission_classes = (IsAuthenticated,)   

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response


    def post(self, request):
        user = User.objects.filter(id=request.user.id).first()
        token = Token.objects.filter(user=user).first()
        token.delete()
        self.response_format["message"] = 'Logout succesfully'
        return Response(self.response_format)


class ForgotPassword(APIView):

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response

    def post(self, request):
        serializer = PasswordOtpSerializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                result = serializer.save()
                if result:
                        self.response_format["message"] = 'Check you email for otp'
                        return Response(self.response_format)
            else:
                self.response_format["error"] = serializer.errors
                self.response_format["status"] = status.HTTP_400_BAD_REQUEST
                return Response(self.response_format)
        except Exception as e:
            self.response_format["error"] = str(e)
            self.response_format["status"] = status.HTTP_400_BAD_REQUEST
            return Response(self.response_format)


class SetNewPassword(APIView):

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response

    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        try:
            if serializer.is_valid():
                result = serializer.save()
                if result:
                    self.response_format["message"] = 'Password set succesfully'
                    return Response(self.response_format)
            else:
                self.response_format["error"] = serializer.errors
                self.response_format["status"] = status.HTTP_400_BAD_REQUEST
                return Response(self.response_format)
        except Exception as e:
            self.response_format["error"] = str(e)
            self.response_format["status"] = status.HTTP_400_BAD_REQUEST
            return Response(self.response_format)


class ChangePassword(APIView):
    permission_classes = (IsAuthenticated,)

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response

    def post(self, request):
        serializer = ChangePasswordSerializer(request.user ,data=request.data)
        try:
            if serializer.is_valid():
                result = serializer.save()
                if result:
                    self.response_format["message"] = 'Passwod change succesfully'
                    return Response(self.response_format)
            else:
                self.response_format["error"] = serializer.errors
                self.response_format["status"] = status.HTTP_400_BAD_REQUEST
                return Response(self.response_format)
        except Exception as e:
            self.response_format["error"] = str(e)
            self.response_format["status"] = status.HTTP_400_BAD_REQUEST
            return Response(self.response_format)