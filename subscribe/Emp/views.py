from django.shortcuts import render
from rest_framework import viewsets
from .models import employee as Employee, loginUser as Login_User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny

from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
import random
import datetime
from django.conf import settings
from .utils import *
import razorpay
import json


class employeeViewset(APIView):
    def get(self, request):
        query = Employee.objects.all()
        serializer = EmployeeSerializer(query, many=True).data
        return Response(serializer, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            data = request.data
            data['user_id'] = gen_user_id(data["emp_first_name"], data["emp_last_name"])
            data['emp_id'] = gen_emp_id(data["emp_first_name"])
            data['emp_lastupdated'] = datetime.datetime.now()
            data['is_user'] = False
            Employee.objects.create(**data)

            password = "User@123"
            password_hash = make_password(password=password)
            login_data = {
                'user_id': data['user_id'],
                'password': password_hash,
                'username':  data['user_id']
            }

            Login_User.objects.create(**login_data)

            template_data = {
                "user_id": data['user_id']
            }
            send_mail(settings.VERIFY_EMAIL_TEMPLATE, [data["emp_email"]], template_data)

            return Response({"message": "User created successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            res = {"code": "400", "message": "Error occured" + str(e)}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)


class EmployeeSubscriptionPlansViews(APIView):
    def get(self, request, user_id):
        my_plans = SubscriptionPlan.objects.filter(user_id=user_id, is_active=True)
        serializers = SubscriptionPlansSerializer(my_plans).data
        return Response(serializers, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    def post(self, request):
        try:
            query_serializer = EmployeeQuerySerializer()
            user_id = request.query_params["user_id"]
            input_data = request.data
            if input_data["password"] == input_data["confirm_password"]:
                login_user = Login_User.objects.get(user_id=user_id)
                password_hash = make_password(password=input_data['password'])
                login_user.password = password_hash
                login_user.pwd_reset_date = datetime.datetime.now()
                login_user.save()
                emp_details = Employee.objects.get(user_id=user_id)
                emp_details.is_user = True
                emp_details.save()
                return Response("password updated", status=status.HTTP_200_OK)
            else:
                return Response("Do no match", status=status.HTTP_200_OK)
        except Exception as e:
            res = {"code": "400", "message": "Error occured" + str(e)}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)


class UserTokenAndPermissionView(TokenObtainPairView):
    serializer_class = UserTokenAndPermissionSeriailizer


class SubscriptionPlanView(APIView):
    def get(self, request):
        plans = SubscriptionPlan.objects.filter(is_active=True)
        serializers = SubscriptionPlansSerializer(plans, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        # data = request.data
        serializer = SubscriptionPlansSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def patch(self, request, plan_id):
    #     instance = SubscriptionPlan.objects.get(pk=plan_id)


class StartPaymentAPI(APIView):
    def post(self, request, sbp):
        sbs_plan = SubscriptionPlan.objects.get(pk=sbp)

        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        order_amount = sbs_plan.plan_rate
        order_currency = 'INR'


        order_id = client.order.create(dict(amount=order_amount, currency=order_currency,
                                            payment_capture=1))

        order = Order.objects.create(order_product=sbs_plan.plan_name,
                                     order_amount=order_amount,
                                     order_order_id=order_id['id'],
                                     sb_pln_id=sbs_plan
                                     )

        context = {
            'order_amount': order_amount,
            "currency": order_currency,
            "order_name": sbs_plan.plan_name,
            "api_key": settings.RAZOR_KEY_ID,
            "order_id": order_id['id']
        }

        return render(request, "payment.html", context)


class HandlePaymentAPI(APIView):
    def post(self, request, template='payment_successful.html'):
        # request.data is coming from frontend
        response = request.POST

        res = {
            'razorpay_order_id': response['razorpay_order_id'],
            'razorpay_payment_id': response['razorpay_payment_id'],
            'razorpay_signature': response['razorpay_signature']

        }

        Order.objects.filter(order_order_id=response['razorpay_order_id']).update(order_pay_id=response['razorpay_payment_id'],
                                                                               order_signature = response['razorpay_signature'])

        ord_id = ""
        raz_pay_id = ""
        raz_signature = ""

        # res.keys() will give us list of keys in res
        for key in res.keys():
            if key == 'razorpay_order_id':
                ord_id = res[key]
            elif key == 'razorpay_payment_id':
                raz_pay_id = res[key]
            elif key == 'razorpay_signature':
                raz_signature = res[key]

        # get order by payment_id which we've created earlier with isPaid=False
        order = Order.objects.get(order_order_id=ord_id)

        data = {
            'razorpay_order_id': ord_id,
            'razorpay_payment_id': raz_pay_id,
            'razorpay_signature': raz_signature
        }

        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

        check = client.utility.verify_payment_signature(data)

        if check is not None:
            res_data = {
                'message': 'payment successfully received!'
            }
            return render(request, template, res_data)

        # if payment is successful that means check is None then we will turn isPaid=True
        order.isPaid = True
        order.save()

        if order.isPaid == True:
            SubscriptionPlan.objects.filter(pk=order.sb_pln_id_id).update(is_paid=True, order_id=order, is_active=True)

        res_data = {
            'message': 'payment successfully received!'
        }

        return render(request, template, res_data)

