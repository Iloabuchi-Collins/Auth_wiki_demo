from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from Auth import settings
from django.core.mail import send_mail
from email.message import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from .tokens import generate_token

# Create your views here.

def home(request):
    return render(request, 'authenticate/index.html')

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password1']
        password2 = request.POST['password2']

        if User.objects.filter(username=username):
            messages.error(request, 'Username already exists')
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request, 'Email already registered')
            return redirect('home')

        if len(username)>10:
            messages.error(request, 'Username cannot be more than 10 characters')
            return redirect('home')

        if len(password)<8:
            messages.error(request, 'Password cannot be less than 8 characters')
            return redirect('home')

        if password != password2:
            messages.error(request, 'Passwords do not match!')
            return redirect('home')

        if not username.isalnum():
            messages.error(request, 'Username only accepts letters and numbers')
            return redirect('home')

        myuser = User.objects.create_user(username, email, password)
        myuser.first_name = firstname
        myuser.last_name = lastname
        myuser.is_active = False
        myuser.save()

        messages.success(request, "Your account has been registered, please check your inbox for a confirmation email")

        # Welcome email
        subject = "Welcome to Auth_wiki - Django login"
        message = "Hello" + myuser.first_name + "! \n Welcome to Auth_wiki \n Thank you for visiting our website \n We have sent you a confirmation email. Please confirm your email address to activate your account"
        from_email = settings.EMAIL_HOST_USER
        send_to = [myuser.email]
        send_mail(subject, message, from_email, send_to, fail_silently=True)

        #Email address confirmation email
        current_site = get_current_site(request)
        email_subject = "Confirm your account with Auth_Wiki"
        message2 = render_to_string('email_confirmation.html', {
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_byte(myuser.url)),
            'token': generate_token.make_token(myuser),            
        })
        email = EmailMesssage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()

        return redirect('signin')

    return render(request, 'authenticate/signup.html')

def activate(request, uid64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError,OverflowError, User.DoesNotExist):
        myuser=None

    if myuser is not None and generate_token.check_token(myuser, tokens):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')

def signin(request):
    #   if request.method == "POST":
        username = request.POST.get('username', 'User1')
        password = request.POST.get('password1', 'password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            firstname = user.first_name
            return render(request, 'authentication/index.html', {'firstname': firstname})
        else:
            messages.error(request, "Bad Credentials")
            return redirect('home')

        return render(request, 'authenticate/signin.html')

def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("home")



