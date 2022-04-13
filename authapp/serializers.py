from rest_framework import serializers   
from authapp.models import User, PassOtp, UserActivation
import random
from datetime import datetime, timedelta
from .utils import CustomException, activation_email, forgot_password_email
from django.contrib.auth.hashers import check_password


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'gender', 'age', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise CustomException("This email already exists!.")
        return value

    def validate(self, attrs):
        if len(attrs['password']) < 8:
            raise serializers.ValidationError({"password": "Password must be 8 or more than 8 character!."})
        elif int(attrs['age']) < 18:
            raise CustomException("Minimum age should be 18 years old")
        elif int(attrs['age']) > 70:
            raise CustomException("Only! under 70 year old accepted!")   
        elif len(str(attrs['phone'])) < 10 or len(str(attrs['phone'])) > 10:
            raise CustomException("Phone length should be 10 to 12 digit!.")    
        return attrs
    
    def create(self, validate_data):
        instance = User.objects.create(
            first_name = validate_data['first_name'],
            last_name = validate_data['last_name'],
            email = validate_data['email'],
            phone = validate_data['phone'],
            gender = validate_data['gender'],
            age = validate_data['age']
            )
        instance.set_password(validate_data['password'])    
        # send mail 
        try: 
            otp = random.randint(100000, 999999)
            activation_email(email=instance.email, otp=otp)
            obj = UserActivation.objects.create(user=instance, user_otp=otp)
        except Exception as e:
            print(e,'=================')
            raise CustomException(e)
        instance.save()
        return instance


class UserActivationSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserActivation
        fields = '__all__'
    
    def create(self, validate_data):
        email = self.context['get_email']
        user_otp = self.context['user_otp']
        user = User.objects.filter(email=email).first()
        instance = UserActivation.objects.filter(user=user, user_otp=user_otp).first()
        if instance is not None: 
            created_time = instance.created_at 
            target_time = created_time + timedelta(hours=24)
            target_time = datetime.strptime(str(target_time), "%Y-%m-%d %H:%M:%S.%f+00:00")
            current_time = datetime.now()
            if current_time > target_time:
                instance.delete()
                raise CustomException('This activation link is expire, !')
            else:
                user.is_active = True
                user.save()
                instance.delete()
                return True
        else:
            raise CustomException("This link is invalid, Please resend activation link!")


class ResendActivationSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=200, write_only=True)

    def create(self, validate_data):
        email = validate_data['email']
        user = User.objects.filter(email=email).first()
        if user is not None:
            if user.is_active:
                raise CustomException('This email already activate.')
            else:
                try: 
                    otp = random.randint(100000, 999999)
                    activation_email(email=email, otp=otp)
                    instance = UserActivation.objects.filter(user=user.id).first()
                    if instance is None:
                        obj = UserActivation.objects.update_or_create(user=user, user_otp=otp, created_at=datetime.now())
                        return True
                    else:
                        instance.delete()
                        obj = UserActivation.objects.update_or_create(user=user, user_otp=otp, created_at=datetime.now())
                        return True
                except Exception as e:
                    print(e,'=================')
                    raise CustomException(e)
        else:
            raise CustomException('This email not register!')


class PasswordOtpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=200)

    class Meta:
        model = PassOtp
        fields = ['email']

    def create(self, validate_data):
        email = validate_data['email']
        user = User.objects.filter(email=email).first()
        if user is not None:
            if user.is_active == True:
                otp = random.randint(100000, 999999)
                forgot_password_email(email=email, otp=otp)
                instance = PassOtp.objects.update_or_create(user=user, user_otp=otp, created_at = datetime.now())
                return True
            else:
                raise CustomException('Your account is not activate !')
        else:
            raise CustomException('Email not register !')


class SetPasswordSerializer(serializers.Serializer):
    otp =  serializers.CharField(max_length=6)
    password = serializers.CharField(max_length=50)

    def validate(self, attrs):
        if len(attrs['password']) < 8:
            raise CustomException("Password must be 8 or more than 8 character!.")
        return attrs

    def create(self, validate_data):
        otp = validate_data['otp']
        check_otp = PassOtp.objects.filter(user_otp=otp).first()
        if check_otp is not None:
            created_time = check_otp.created_at
            target_time = created_time + timedelta(minutes=1)
            target_time = datetime.strptime(str(target_time), "%Y-%m-%d %H:%M:%S.%f+00:00")
            current_time = datetime.now()
            if current_time > target_time:
                check_otp.delete()   
                raise CustomException('This otp is expire, Please try again!') 
            else:       
                email = check_otp.user.email
                user = User.objects.filter(email=email).first()
                password = validate_data['password']
                user.set_password(password)
                user.save()
                check_otp.delete()
                return True 
        else:
            raise CustomException('Otp did not matched, please try again!') 


class ChangePasswordSerializer(serializers.Serializer):
    old_pass =  serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)

    def validate(self, attrs):
        if len(attrs['password']) < 8:
            raise serializers.ValidationError({"password": "Password must be 8 or more than 8 character!."})  
        return attrs

    def update(self,obj, validate_data):
        check = check_password(validate_data['old_pass'], obj.password)
        if check:
            obj.set_password(validate_data['password'])
            obj.save()
            return True
        else:
            raise CustomException("Old password not match")        