from .models import employee as Employee, loginUser as Login_User, SubscriptionPlan, Order
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = "__all__"


class EmployeeQuerySerializer(serializers.Serializer):
    user_id = serializers.CharField()


class LoginUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Login_User
        fields = [
            "id",
            "user_id",
        ]


class UserTokenAndPermissionSeriailizer(TokenObtainPairSerializer):
    def get_token(self, attrs):
        print("hereeeeeeeeee")
        token = super(UserTokenAndPermissionSeriailizer, self).validate(attrs)
        print(self.user.user_id)
        loggedin_user_id = self.user.user_id
        print(loggedin_user_id)
        token.validated_data['username'] = self.user.user_id
        print(token['username'])
        chk_active = Employee.objects.get(user_id=token['username'], is_user=True)
        if chk_active:
            return token


class SubscriptionPlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    order_date = serializers.DateTimeField(format="%d %B %Y %I:%M %p")

    class Meta:
        model = Order
        fields = '__all__'
        depth = 2
