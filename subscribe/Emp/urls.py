from django.urls import path, include
from rest_framework import routers
from django.conf.urls import url
from .views import *

# router = routers.SimpleRouter()
#
# router.register(r"employee/signin", employeeViewset)

urlpatterns = [
    path(
        "employee/signin",
        employeeViewset.as_view(),
    ),
    path(
        "employee/plans",
        SubscriptionPlanView.as_view(),
    ),

    path(
        "employee/myplans/<str:user_id>",
        EmployeeSubscriptionPlansViews.as_view()
    ),

    path('pay/<int:sbp>', StartPaymentAPI.as_view(), name="payment"),
    path('payment/success/', HandlePaymentAPI.as_view(), name="payment_success"),

]