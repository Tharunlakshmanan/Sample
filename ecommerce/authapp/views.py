from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib import messages
# for generating the token I imported few modules
from django.template.loader import render_to_string
# encode is generating the link if i click the link again it should decode so decode was imported
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .utils import TokenGenarator, genarate_token
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
# for email
from django.core.mail import EmailMessage
from django.conf import settings
from django.views.generic import View
# for authentication purpose
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator

# Create your views here.


def signup(request):
    # getting the data from frontend if the method is post
    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        password = request.POST['pass1']
        confirm_password = request.POST['pass2']
        if password != confirm_password:
            messages.warning(request, "Password do not match, Please Try again!")
            return render(request, 'signup.html')
        try:
            if User.objects.get(username=email):
                # return HttpResponse("Email already exist")
                messages.info("Email already taken")
                return render(request, 'signup.html')
        except Exception as identifier:
            pass
        user = User.objects.create_user(email, email, password)
        user.first_name = fname
        user.last_name = lname
        user.is_active = False
        messages.info(request,'Thanks for signing up')
        # saving the username in database for future reference, making the user status false user need to verify
        user.save()
# this is activate the email
        email_subject = f'Activate your Account{fname}'
        message = render_to_string('activate.html', {
            'user': user,
            'domain': '127.0.0.1:8000',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': genarate_token.make_token(user)
        })
        # email_message=EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email])
        # email_message.send()
        messages.success(
            request, f'Activate your account by clicking the link in your gmail {message}')
        return redirect('/auth/login/')
    return render(request, "Signup.html")

# this is class based view for genrating the  link for activation of account


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            # here decoding the url link and getting the primary key and match with the uid
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception as identifier:
            user = None
            # if user is give correct urls and after genarating the token that we are cross verifying the particulat user with the token
        if user is not None and genarate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.info(request, "Account Activates Successfully")
            return redirect('/auth/login')
        return render(request, 'activatefail.html')


def handlelogin(request):
    if request.method == "POST":
        username = request.POST['email']
        userpassword = request.POST['pass1']
        myuser = authenticate(username=username, password=userpassword)
        if myuser is not None:
            login(request, myuser)
            messages.success(request, "Login Success")
            return redirect('/')
        else:
            messages.error(request, "Invalid Credentials")
            return redirect('/auth/login')
    return render(request, "login.html")


def handlelogout(request):
    logout(request)
    messages.info(request, "Logout Successful")
    return render(request, "login.html")

# resertemail class based funciton


class RequestResetEmailView(View):
    def get(self, request):
        return render(request, 'request-reset-email.html')

    def post(self, request):
        email = request.POST['email']
        user = User.objects.filter(email=email)

# if user already exists in this particular html page this token will be generate
        if user.exists():
            email_subject = 'Reset Your Password'
            message = render_to_string('Reset-user-password.html', {
                'domain': '127.0.0.1:8000',
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0])
            })

            # Email_message=EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email])
            # Email_message.send()
            messages.info(
                request, f"WE HAVE THE SENT YOU AN EMAIL WITH INSTRUCTION ON HOW TO RESET THE PASSWORD")
            return render(request, 'request-reset-email.html')
        else:
            messages.error(request, "No user exists with this email")
            return render(request, 'request-reset-email.html')


class SetNewPasswordView(View):
    # if user click on that link here get the response
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }
        try:
            # we are decoding the uid same thing doing here as well of activation
            # after decode it going to take user based on pk
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            # here check the token for specific user with passwordtokegenrator, if anything in it wrong it show warning info
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.warning(request, "Password Reset link is Invalid")
                return render(request, 'request-reset-email.html')

        except DjangoUnicodeDecodeError as identifier:
            pass

        return render(request, 'set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }
        password = request.POST['pass1']
        confirm_password = request.POST['pass2']
        if password != confirm_password:
            messages.warning(request, "Password is not matching")
            return render(request, 'set-new-password.html', context)

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(
                request, "Password Reset Success PLease Login with new password")
            return redirect('/auth/login')

        except DjangoUnicodeDecodeError as identifier:
            messages.error(request, "Something went wrong")
            return render(request, 'set-new-password.html', context)
        return render(request, 'set-new-password.html', context)
