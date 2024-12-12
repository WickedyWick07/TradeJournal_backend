from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'password', 'email' ]


        def create(self, validated_data):
            user = CustomUser.objects.create_user(
                email = validated_data['email'],
                first_name = validated_data['first_name'],
                last_name = validated_data['last_name'],
                password =validated_data['password']
            )
            return user
        


class LoginSerializer(serializers.ModelSerializer):

    
    class Meta:
        model = CustomUser
        fields = ['email', 'password']

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

   
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                data['user'] = user
            else:
                raise serializers.ValidationError('Invalid email or password.')
        else:
            raise serializers.ValidationError('Must include "email" and "password".')

        return data