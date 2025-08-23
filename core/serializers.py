from djoser.serializers import UserCreateSerializer


class MyUserCreateSerializer(UserCreateSerializer):
    
    class Meta(UserCreateSerializer.Meta):
        fields = ['id', 'first_name', 'last_name','email', 'password']
