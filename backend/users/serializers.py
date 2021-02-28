import re

from django.contrib.auth import password_validation

from rest_framework import serializers
from rest_framework.validators import ValidationError

from .models import User, UserFollowing


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def validate_username(self, username):
        if not re.match(r'^\w+$', username):
            raise serializers.ValidationError(
                'The username may only contain alphanumeric characters and _'
            )
        else:
            return username

    def validate_password(self, password):
        password_validation.validate_password(password, self.instance)
        return password

    def save(self, request):
        user = User(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
        )

        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})

        user.set_password(password)
        user.save()
        return user


class FollowingSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    class Meta:
        model = UserFollowing
        fields = ('id', 'slug', 'display_name',)

    def get_display_name(self, obj):
        return obj.user_followed.display_name

    def get_slug(self, obj):
        return obj.user_followed.slug


class FollowersSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    class Meta:
        model = UserFollowing
        fields = ('id', 'slug', 'display_name',)

    def get_display_name(self, obj):
        return obj.user_follows.display_name

    def get_slug(self, obj):
        return obj.user_follows.slug


class UserSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'display_name', 'description', 'avatar',
                  'date_joined', 'slug', 'followers', 'following',)
        lookup_field = 'slug'

    def get_following(self, obj):
        # Add count
        return FollowingSerializer(obj.following.all(), many=True).data

    def get_followers(self, obj):
        # Add count
        return FollowersSerializer(obj.followers.all(), many=True).data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('display_name', 'description', 'avatar')

    def validate(self, data):
        display_name = data.get('display_name')

        if display_name is not None:
            if display_name in ('', ' ', '⠀'):
                raise ValidationError('d')

        return data


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')
