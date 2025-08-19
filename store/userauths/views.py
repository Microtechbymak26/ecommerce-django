from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from .forms import UserRegisterForm
from .models import User, UserProfile
from .forms import UserRegisterForm, AddressForm
from userauths.forms import LoginForm, UserRegisterForm
from .forms import LoginForm

def register_view(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already signed in")
        return redirect("home")

    form = UserRegisterForm(request.POST or None)
    address_form = AddressForm(request.POST or None)

    if form.is_valid() and address_form.is_valid():
        # --- User Save ---
        user = form.save(commit=False)
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password1")
        user.set_password(password)
        user.save()

        # --- Profile Save ---
        UserProfile.objects.create(
            user=user,
            full_name=form.cleaned_data.get("full_name"),
            mobile_number=form.cleaned_data.get("mobile"),
            user_type=form.cleaned_data.get("user_type"),
        )

        # --- Address Save ---
        address = address_form.save(commit=False)
        address.user = user   # ForeignKey User
        address.save()

        # --- Auto Login ---
        user = authenticate(email=email, password=password)
        if user:
            login(request, user)

        messages.success(request, "🎉 Account created successfully and address added!")
        return redirect("home")

    return render(request, "userauths/sign-up.html", {
        "form": form,
        "address_form": address_form,
    })




def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect("home")

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)  # email se kaam karega
            if user is not None:
                login(request, user)
                messages.success(request, "You are logged in")
                next_url = request.GET.get("next", "home")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid email or password")
        else:
            messages.error(request, "Please fill out all fields correctly")
    else:
        form = LoginForm()

    return render(request, "userauths/sign-in.html", {"form": form})

def logout_view(request):
    logout(request)
    # 🛒 Cart ko bhi clear kar do
    if "cart_id" in request.session:
        del request.session["cart_id"]

    messages.success(request, "You have been logged out. Cart cleared!")
    return redirect("userauths:sign-in")
