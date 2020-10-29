from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

def signup(request):
    if request.user.is_authenticated:

        return redirect('community:index')

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('community:index')

    else:
        form = CustomUserCreationForm()

    context = {
        'form': form
    }

    return render(request, 'accounts/signup.html', context)



def login(request):
    if request.user.is_authenticated:
        return redirect('community:index')

    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect(request.GET.get('next') or 'community:index')

    else:
        form = AuthenticationForm()

    context = {
        'form': form
    }

    return render(request, 'accounts/login.html', context)


@login_required
def logout(request):
    auth_logout(request)

    return redirect('community:index')

@login_required
def profile(request, username):

    User = get_user_model()
    user = get_object_or_404(User, username=username )

    context={
        'person':user,

    }
    return render(request, 'accounts/profile.html', context)

@login_required
def follow(request, username ):
    you = get_object_or_404(get_user_model(), username=username )
    me = request.user

    if you != me :
        if you.followings.filter(pk=me.pk).exists():
            you.followings.remove(me)

        else:
            you.followings.add(me)

    return redirect('accounts:profile', you.username )




