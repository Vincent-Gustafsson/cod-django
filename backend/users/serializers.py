from rest_framework import serializers

from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {
                'write_only':True
            }
        }

    def validate_password(self, data):
        min_password_length = 6
        if len(data) < min_password_length:
            raise serializers.ValidationError({'password':'The password must be at least 6 characters long.'})

        else:
            return data

    def save(self, request):
        user = User(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
        )

        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password':'Passwords must match.'})
        
        user.set_password(password)
        user.save()
        return user

"""
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('display_name', 'description', 'avatar',)
"""

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'display_name', 'description', 'avatar', 'date_joined')
