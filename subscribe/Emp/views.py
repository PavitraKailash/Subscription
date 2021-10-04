from django.shortcuts import render
from rest_framework import viewsets
from .models import *
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
    permission_classes = []

    def get(self, request):
        query = Employee.objects.all()
        serializer = EmployeeSerializer(query, many=True).data
        return Response(serializer, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        username = data['username']
        f_name = data['first_name']
        l_name = data['last_name']
        email = data['email']
        password = data['password']
        phone = data['emp_phone']
        hash_password = make_password(password)
        try:
            user_obj = {}
            user_obj["username"] = username
            user_obj["first_name"] = f_name
            user_obj["last_name"] = l_name
            user_obj["email"] = email
            user_obj["password"] = hash_password
            usr_save = User.objects.create(**user_obj)
            cst_dt = {}
            cst_dt["user_id"] = usr_save
            cst_dt["emp_phone"] = phone
            emp = Employee.objects.create(**cst_dt)
            return Response({"message": "User created successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EmployeeSubscriptionPlansViews(APIView):
    def get(self, request, user_id):
        my_plans = SubscriptionPlan.objects.filter(user_id=user_id, is_active=True)
        serializers = SubscriptionPlansSerializer(my_plans).data
        return Response(serializers, status=status.HTTP_200_OK)


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
    permission_classes = []
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
    permission_classes = []
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

