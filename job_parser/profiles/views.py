from django.shortcuts import render, redirect
from .models import Profile, User
from .forms import ProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def profile(request, username):
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)

    if request.method == "POST":
        form = ProfileForm(request.POST)

        if form.is_valid():
            profile.city = form.cleaned_data["city"].lower()
            profile.job = form.cleaned_data["job"].lower()
            profile.subscribe = form.cleaned_data["subscribe"]
            profile.save()
            messages.success(request, "Вы подписались на рассылку вакансий")
            return redirect("profiles:profile", username=username)
    else:
        default_data = {
            "city": profile.city,
            "job": profile.job,
            "subscribe": profile.subscribe,
        }

        form = ProfileForm(initial=default_data)

    return render(request, "users/profile.html", {"form": form, "user": user})
