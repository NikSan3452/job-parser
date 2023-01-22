from django.shortcuts import render, redirect
from .models import Profile, User
from .forms import ProfileForm
from django.contrib.auth.decorators import login_required


@login_required
def profile(request, username):
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)

    if request.method == "POST":
        form = ProfileForm(request.POST)

        if form.is_valid():
            profile.city = form.cleaned_data["city"]
            profile.job = form.cleaned_data["job"]
            profile.subscribe = form.cleaned_data["subscribe"]
            profile.save()
            return redirect("profiles:profile", username=username)
    else:
        default_data = {"city": profile.city, "job": profile.job}
        form = ProfileForm(initial=default_data)

    return render(request, "users/profile.html", {"form": form, "user": user})
