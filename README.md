Plan Subscription App
This project demostrates a Registration of Managers, Subscriptions plans and Payments.  Here I have integrated Razorpay payment gateway to complete a payment. 
Once the employee/manager is created using the respective Apis, the user will receive an email on the given email id. Originally, the user will be given a generated password. 
The email  says to verify the email and he/she will have to update his password. 
When the user updates the password, the is_user field will be set to True.

Apis for creating and getting a list of Subscription Plans. 
Apis for payment of a plan using the Razorpayment gateway. 
When the payment is initiated, the user_id who will be buying the plan will be updated in the SubscriptionPlan model.
Once the payment is completed, the SubscriptionPlan model will be updated with the order_id and also is_paid will be set to True

The models created are:
a) Employee
b) loginUser
c) SubscriptionPlan
d) Order


1. Clone the project code using the command:
      git clone 
   Activate the env using env\Scripts\activate
2. Navigate to subscribe folder
3. Install the required libraries for the project with
	pip install freeze -r requirements.txt
4. python version used for the project is Python 3.9.1
5. Please alter the database configuration based on your local mySQL schema.
     The code that has to be altered is:
	DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'assgn',
        'USER': 'root',
        'PASSWORD': 'Pass1word',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
6. After installing the requirements, complete migrations for the app using the commands
	python manage.py migrate
7.  The Postman collection is 
	https://www.getpostman.com/collections/3260893946b5bbe11d2a
	a) 127.0.0.1:8000/user/employee/signin - API for Creating and Retrieving list of employees
	b) 127.0.0.1:8000/user/employee/verify?user_id={{user_id}} - API that will be hit when the user will click on the Verify Email button from his/her email. 
	c) 127.0.0.1:8000/user/api-token-auth/ - Token
	d) 127.0.0.1:8000/user/employee/plans - API for Creating and Retrieving list of plans
	e) 127.0.0.1:8000/user/pay/{{sbp}} - API for payment of the Subscription plan whose id is passed as parameter (sbp)
	f) 127.0.0.1:8000/user/payment/success/ - API for successfull payment verification
	g) 127.0.0.1:8000/user/employee/myplans/<str:user_id> - API that will return plans of a person
