from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
)
from django.contrib.auth import (
    login as django_login,
)
from django.contrib.auth import (
    logout as django_logout,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .models import VerificationCode
from .tasks import custom_send_email

User = get_user_model()
TokenManager = default_token_generator


def cant_be_authenticated(view):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse("home_page"))
        return view(request, *args, **kwargs)

    return wrapper


@cant_be_authenticated
def login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "Fill all the inputs, please.")
            return redirect(reverse("login"))

        user = authenticate(request, username=username, password=password)

        if user is not None:
            django_login(request, user)
            messages.success(request, "Sucessfuly authenticated.")

            return redirect(reverse("home_page"))
        else:
            messages.error(request, "Username/Password incorrects.")
            return redirect(reverse("login"))

    return render(request, "accounts/login.html")


def verify_code(request):
    purpose = request.GET.get("purpose", "").strip()

    if not purpose:
        messages.error(request, "Nothing to verify")
        return redirect(reverse("home_page"))

    if purpose == "VA":
        action = request.GET.get("action", "")

        if action == "resend-code":
            email = request.session.get("email", "").strip()
            username = request.session.get("username", "").strip()

            if not email or not username:
                messages.error(request, "Session expired. Restart signup.")
                return redirect(reverse("signup"))

            code = VerificationCode.generate_code()
            verification_code = VerificationCode.objects.create(email=email, code=code)

            custom_send_email.delay(
                subject="Verifique a sua conta | Votox",
                template="emails/verify_account.html",
                recipient_list=[email],
                context={
                    "verification_code": verification_code.code,
                    "username": username,
                },
            )

            messages.success(request, "New code was sent.")
            return redirect(
                reverse("verify_code") + f"?purpose={purpose}&after=resend-code"
            )

        if request.method == "POST":
            username = request.session.get("username", "").strip()
            email = request.session.get("email", "").strip()
            password = request.session.get("password", "").strip()

            if not all([username, email, password]):
                messages.error(request, "Error while signup, try again later.")
                return redirect(reverse("signup"))

            for key in ["email", "password", "username"]:
                if key not in request.session:
                    messages.error(request, "Session expired. Restart signup.")
                    return redirect(reverse("signup"))

            code = request.POST.get("verification_code", "").strip()

            if not code:
                messages.error(request, "Please, write the code.")
                return redirect(reverse("verify_code") + "?purpose=" + purpose)

            verification_code = VerificationCode.objects.filter(
                email=email, is_used=False
            ).latest("created_at")

            if verification_code.is_valid() and verification_code.code == code:
                verification_code.mark_as_used()

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                )

                for key in ["email", "username", "password"]:
                    if key in request.session:
                        del request.session[key]

                messages.success(request, "Account successfuly created.")
                return redirect(
                    reverse("signup") + "?step=profile-photo&user=" + username
                )
            messages.error(request, "Invalid or expired code.")
            return redirect(reverse("verify_code") + "?purpose=" + purpose)
    return render(request, "accounts/verify_account.html", {"purpose": purpose})


@cant_be_authenticated
def signup(request):
    step = request.GET.get("step", "").strip()

    if step == "profile-photo":
        username = request.GET.get("user", "").strip()

        if not username:
            messages.error(request, "User not found. Try it later")
            return redirect(reverse("home_page"))

        user = User.objects.get(username=username)

        if request.method == "POST":
            profile_photo = request.FILES.get("profile-photo", "")

            if not profile_photo:
                messages.error(request, "No image were given.")
                return redirect(
                    reverse("signup") + "?step=profile-photo&user=" + username
                )

            if profile_photo.content_type not in (
                "image/png",
                "image/jpg",
                "image/jpeg",
            ):
                messages.error(request, "Not allowed image extension.")
                return redirect(
                    reverse("signup") + "?step=profile-photo&user=" + username
                )

            if profile_photo.size > (2 * 1024 * 1024):
                messages.error(request, "File size is above 2MB.")
                return redirect(
                    reverse("signup") + "?step=profile-photo&user=" + username
                )

            user.profile_photo = profile_photo
            user.save()

            messages.success(request, "Profile photo were set")
            return redirect(reverse("login"))
        return render(request, "accounts/profile_photo.html", {"user": user})

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        if not username and not email and not password:
            messages.error(request, "Fill all the inputs, please.")
            return redirect(reverse("signup"))

        if len(password) < 8:
            messages.error(request, "Weak password.")
            return redirect(reverse("signup"))

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Insert a valid email.")
            return redirect(reverse("signup"))

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username isn't available.")
            return redirect(reverse("signup"))

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email isn't available.")
            return redirect(reverse("signup"))

        request.session["username"] = username
        request.session["email"] = email
        request.session["password"] = password

        code = VerificationCode.generate_code()
        verification_code = VerificationCode.objects.create(
            email=email, code=code, purpose="VA"
        )

        custom_send_email.delay(
            subject="Verifique a sua conta | Votox",
            template="emails/verify_account.html",
            recipient_list=[email],
            context={"verification_code": verification_code.code, "username": username},
        )

        messages.success(request, "We sent an email to you.")
        return redirect(reverse("verify_code") + "?purpose=VA")
    return render(request, "accounts/signup.html")


@login_required
def logout(request):
    if request.method == "POST":
        django_logout(request)
        messages.success(request, "You were logout.")
        return redirect(reverse("login"))
    return render(request, "accounts/logout.html")


@cant_be_authenticated
def forgot_password(request):
    ctx = {}

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if not email:
            messages.error(request, "Please, fill the input.")
            return redirect(reverse("forgot_password"))

        user = User.objects.filter(email__iexact=email).first()

        if not user:
            messages.error(
                request, "This email is not registrated, redirecting to signup."
            )
            return redirect(
                reverse("forgot_password") + "?redirect=" + quote(reverse("signup"))
            )

        try:
            token = TokenManager.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            link = request.build_absolute_uri(
                reverse("reset_password", args=[uidb64, token])
            )

            custom_send_email.delay(
                subject="Reset Password | Votox",
                template="emails/reset_password.html",
                recipient_list=[email],
                context={
                    "link": link,
                    "username": user.username,
                },
            )

            messages.success(request, "Reset password link was sent")
            return redirect(reverse("login"))
        except Exception as e:
            print(e)
            messages.error(request, "Error. Try it later, redirecting to signup.")
            return redirect(
                reverse("forgot_password") + "?redirect=" + quote(reverse("login"))
            )
    return render(request, "accounts/forgot_password.html", ctx)


@cant_be_authenticated
def reset_password(request, uidb64, token):
    ctx = {"uidb64": uidb64, "token": token}

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if not TokenManager.check_token(user, token):
            raise ValueError

    except (TypeError, OverflowError, ValueError, user.DoesNotExist):
        messages.error(request, "Invalid link. Try again later.")
        return redirect(reverse("login"))

    if request.method == "POST":
        new_password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get("password2", "").strip()

        if not all([new_password, confirm_password]):
            messages.error(request, "Please, fill the inputs")
            return redirect(reverse("reset_password", args=[uidb64, token]))

        if new_password != confirm_password:
            messages.error(request, "Diferent passwords.")
            return redirect(reverse("reset_password", args=[uidb64, token]))

        user.set_password(new_password)
        user.save()

        messages.success(request, "Password reseted.")
        return redirect(reverse("login"))
    return render(request, "accounts/reset_password.html", ctx)
