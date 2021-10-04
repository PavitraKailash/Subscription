from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


# Create your models here.
class Employee(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    emp_phone = models.IntegerField(null=True)


class SubscriptionPlan(models.Model):
    class plan_choices(models.TextChoices):
        MONTHLY = "MONTHLY", _("MONTHLY")
        WEEKLY = "WEEKLY", _("WEEKLY")

    plan_name = models.CharField(max_length=50)
    plan_type = models.CharField(
        max_length=10, choices=plan_choices.choices, default=plan_choices.MONTHLY
    )
    plan_createdon = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_paid = models.BooleanField(null=True)
    order_id = models.ForeignKey('Order', on_delete=models.CASCADE, null=True)
    plan_rate = models.IntegerField()
    user_id = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "subscription_plan"


class Order(models.Model):
    ord_id = models.AutoField(primary_key=True)
    sb_pln_id = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, null=True)
    order_product = models.CharField(max_length=100, null=True)
    order_amount = models.CharField(max_length=25, null=True)
    order_order_id = models.CharField(max_length=100, null=True)
    order_pay_id = models.CharField(max_length=100, null=True)
    order_signature = models.CharField(max_length=100, null=True)
    isPaid = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_product
