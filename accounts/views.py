from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import (
    authenticate, 
    login as django_login, 
    logout as django_logout, 
    get_user_model,
    get_user
)
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import VerificationCode

User = get_user_model() 

def send_verification_email(email, verification_code, username):
    subject = 'Verifique a sua conta na Votox'
    site_name = 'Votox' 

    html_message = render_to_string('emails/verify_account.html', {
        'verification_code': verification_code,
        'site_name': site_name,
        'username': username
    })
    
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,  
        from_email='hello@demomailtrap.co',  
        recipient_list=[email],
        html_message=html_message, 
        fail_silently=False,
    )


def cant_be_authenticated(view):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('home_page'))
        return view(request, *args, **kwargs)
    return wrapper

@cant_be_authenticated
def login(request):
    if request.method == "POST":
        username = request.POST.get('username', "").strip()
        password = request.POST.get('password', "").strip()

        if not username or not password:
            messages.error(request, 'Fill all the inputs, please.')
            return redirect(reverse('login'))
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            django_login(request, user)
            messages.success(request, 'Sucessfuly authenticated.')

            return redirect(reverse('home_page'))
        else:
            messages.error(request, 'Username/Password incorrects.')
            return redirect(reverse('login'))

    return render(request, 'accounts/login.html')


@cant_be_authenticated
def signup(request):
    step = request.GET.get("step", "").strip()

    if step == 'verify-account':
        action = request.GET.get("action", "")
        
        if action == 'resend-code':
            email = request.session.get("email", "").strip()
            username = request.session.get("username", "").strip()

            if not email or not username:
                messages.error(request, 'Session expired. Restart signup.')
                return redirect(reverse('signup'))
            
            code = VerificationCode.generate_code()
            verification_code = VerificationCode.objects.create(
                email=email, code=code
            )
            
            send_verification_email(email, code, username)
            
            messages.success(request, 'New code was sent.')
            return redirect(reverse('signup')+'?step=verify-account&after=resend-code')

        if request.method == "POST":
            username = request.session.get("username", "").strip()
            email = request.session.get("email", "").strip()
            password = request.session.get("password", "").strip()

            if not all([username, email, password]):
                messages.error(request, 'Error while signup, try again later.')
                return redirect(reverse('signup'))
            
            for key in ['email', 'password', 'username']:
                if  key not in request.session:
                    messages.error(request, 'Session expired. Restart signup.')
                    return redirect(reverse('signup'))

            code = request.POST.get("verification_code", "").strip()

            if not code:
                messages.error(request, 'Please, write the code.')
                return redirect(reverse('signup')+'?step=verify-account')
            
            verification_code = VerificationCode.objects.filter(
                email=email, 
                is_used=False
            ).latest('created_at')

            if verification_code.is_valid():
                verification_code.mark_as_used()
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                )

                for key in ['email', 'username', 'password']:
                    if key in request.session:
                        del request.session[key]

                messages.success(request, 'Account successfuly created.')
                return redirect(reverse('signup')+'?step=profile-photo&user='+username)
            messages.error(request, 'Invalid or expired code.')
            return redirect(reverse('signup')+'?step=verify-account')
        return render(request, 'accounts/verify_account.html')

    if step == 'profile-photo':
        username = request.GET.get('user', "").strip()

        if not username:
            messages.error(request, 'User not found. Try it later')
            return redirect(reverse('home_page'))
        
        user = User.objects.get(username=username)

        if request.method == "POST":
            profile_photo = request.FILES.get('profile-photo', "")

            if not profile_photo:
                messages.error(request, 'No image were given.')
                return redirect(reverse('signup')+'?step=profile-photo&user='+username)
            
            if profile_photo.content_type not in ('image/png', 'image/jpg', 'image/jpeg'):
                messages.error(request, 'Not allowed image extension.')
                return redirect(reverse('signup')+'?step=profile-photo&user='+username)

            if profile_photo.size > (2 * 1024):
                messages.error(request, 'File size is above 2MB.')
                return redirect(reverse('signup')+'?step=profile-photo&user='+username)

            user.profile_photo = profile_photo
            user.save()

            messages.success(request, 'Profile photo were set')
            return redirect(reverse('login'))
        return render(request, 'accounts/profile_photo.html', {'user': user})
    
    if request.method == "POST":
        username = request.POST.get('username', "").strip()
        email = request.POST.get('email', "").strip()
        password = request.POST.get('password', "").strip()

        if not username and not email and not password:
            messages.error(request, 'Fill all the inputs, please.')
            return redirect(reverse('signup'))

        if len(password) < 8:
            messages.error(request, 'Weak password.')
            return redirect(reverse('signup'))
        
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Insert a valid email.')
            return redirect(reverse('signup'))

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username isn\'t available.')
            return redirect(reverse('signup'))
        
        request.session["username"] = username
        request.session["email"] = email
        request.session["password"] = password
        
        code = VerificationCode.generate_code()
        verification_code = VerificationCode.objects.create(
            email=email, code=code
        )
        
        send_verification_email(email, code, username)

        messages.success(request, 'We sent an email to you.')
        return redirect(reverse('signup')+'?step=verify-account')
    return render(request, 'accounts/signup.html')


@login_required
def logout(request):
    django_logout(request)

    messages.success(request, 'You were logout.')
    return redirect(reverse('login'))