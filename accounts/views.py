from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User, Group, Permission
from django.contrib import auth
from django.views.decorators.http import require_POST

def login_validation(request):
    pass

def login(request):
    if request.method == "POST":
        user = auth.authenticate(username=request.POST["username"], password=request.POST["password"]+"my_salt")
        if user is not None:
            auth.login(request, user)
            messages.success(request, "وارد شدید")
            return redirect("base:index")
        elif User.objects.filter(username=request.POST["username"]).exists():
            messages.error(request, "رمز عبور را صحیح وارد کنید")
        else:
            messages.error(request, "نام کاربری وارد شده ثبت نشده است")
        return redirect("accounts:login")
    elif request.method == "GET":
        return render(request, "accounts/login.html")


def reg_validation(request):
    status = True
    if User.objects.filter(username=request.POST["username"]).exists():
        messages.error(request, "نام کاربری وارد شده قبلا انخاب شده است!")
        status = False
    if User.objects.filter(email=request.POST["email"]).exists():
        messages.error(request, "این ایمیل در سیستم موجود است!")
        status = False
    if request.POST["password"] != request.POST["confirm_password"]:
        messages.error(request, "رمز های عبور وارد شده یکسان نیستند!")
        status = False
    return request, status


def register(request, position):
    if request.method == "POST":
        request, status = reg_validation(request)[0], reg_validation(request)[1]
        if status:
            user = User.objects.create_user(first_name=request.POST["first_name"], 
                                            last_name=request.POST["last_name"], username=request.POST["username"], 
                                            password=request.POST["password"]+"my_salt", 
                                            email=request.POST["email"], is_active=False)
            user.save()
            user.groups.add(Group.objects.get(name=position).id)
            if position == "mentor":
                user.user_permissions.add(Permission.objects.get(codename=request.POST["field_of_mentoring"]).id)
            messages.success(request, "ثبت نام شما با موفقیت ثبت شد، پس از تایید مدیر سیستم میتوانید وارد شوید")
            return redirect("base:index")
        else:
            return HttpResponseRedirect(reverse("accounts:register", kwargs={"position":position}))
    elif request.method == "GET":
        if position == "student":
            return render(request, "accounts/register.html")
        elif position == "mentor":
            return render(request, "accounts/register.html")
        elif position == "manager":
            return render(request, "accounts/register.html")


@require_POST
def logout(request):
    auth.logout(request)
    messages.info(request, "با موفقیت خارج شدید")
    return redirect("base:index")