from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _



# Create your models here.
class employee(models.Model):
    user_id = models.CharField(primary_key=True, max_length=15)
    emp_first_name = models.CharField(max_length=30)
    emp_last_name = models.CharField(max_length=30)
    emp_id = models.CharField(max_length=15, null=True, db_index=True)
    emp_email = models.CharField(unique=True, max_length=250, null=True, db_index=True)
    emp_phone = models.CharField(unique=True, max_length=15, null=True, db_index=True)
    emp_lastupdated = models.DateTimeField(auto_now=True)
    emp_lastupdatedby = models.CharField(max_length=15, null=True)
    is_user = models.BooleanField(null=True, default=False)

    def __str__(self):
        return self.emp_first_name + " " + self.emp_last_name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["emp_email", "emp_phone"], name="unique_email_phone"
            )
        ]


class loginUser(AbstractUser):
    password = models.CharField(max_length=100, null=True)
    pwd_reset_date = models.DateTimeField(null=True)
    last_login = models.DateTimeField(null=True)
    user_id = models.CharField(max_length=15, null=True)

    class Meta:
        db_table = "login_user"


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
    user_id = models.ForeignKey(employee, on_delete=models.CASCADE, null=True)


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


