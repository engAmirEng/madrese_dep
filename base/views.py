from django.db.models import fields
from .forms import StudentForm, AchievementForm
from django.urls import reverse
from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404, HttpResponseRedirect
from django.http import Http404, request
from .models import Achievement, Student
from . import extentions
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.contrib import messages

def is_member(user, group_namme):
    return user.groups.filter(name=f'{group_namme}').exists()



def error_400(request, exception):
        data = {}
        return render(request,'errors/error400.html', data)
def error_403(request, exception):
        data = {}
        return render(request,'errors/error403.html', data)
def error_404(request, exception):
        data = {}
        return render(request,'errors/error404.html', data)
def error_503(request, exception):
        data = {}
        return render(request,'errors/error503  .html', data)


@require_http_methods(["GET", "POST"])
def index(request):
    achievement_list = get_list_or_404(Achievement, is_main=True)
    if request.method == "GET":
        content = {
            "achievement":achievement_list
        }
        # return render(request, "base/index.html", content)
        return render(request, "base/modiran_frame/index_detail.html", content)
        # return render(request, "base/modiran_frame/update_form.html", content)
        # return render(request,'errors/error503.html')
    elif request.method == "POST":
        searched_obj = []
        for i in achievement_list:
            if request.POST["title"]  in i.title and request.POST["first_name"]  in i.owner.first_name \
                and request.POST["last_name"]  in i.owner.last_name and request.POST["level"]  in i.level\
                    and request.POST["year"] in str(i.year):

                searched_obj.append(i)
        content = {
            "achievement":searched_obj
        }
        return render(request, "base/modiran_frame/index_detail.html", content)


def detail(request, id):
    content = {
        "achievement":get_object_or_404(Achievement, id=id),
    }
    return render(request, "base/modiran_frame/index_detail.html", content)


@login_required
@require_GET
def confirm_deny(request, model_name, refId, id):
    obj = get_object_or_404(Achievement, refrence_id=refId, id=id)
    if "confirm" in model_name:
        if refId == 0:
            obj.modify_level = request.user.groups.all()[0].name
            obj.is_main = True if request.user.groups.all()[0].name == "manager" else False
            obj.refrence_id = obj.id if request.user.groups.all()[0].name == "manager" else 0
            obj.save()
        elif not obj.is_deleted:
            main_obj = get_object_or_404(Achievement, refrence_id=refId, is_main=True)
            obj.modify_level = request.user.groups.all()[0].name
            obj.is_main = True if request.user.groups.all()[0].name == "manager" else False
            obj.save()
            main_obj.is_main = False if request.user.groups.all()[0].name == "manager" else True
            main_obj.save()
            messages.success(request, "با موفقیت اعمال شد")
            if request.user.groups.all()[0].name == "manager":
                main_obj.delete()
                messages.success(request, "با موفقیت جایگزین شد")
        elif obj.is_deleted:
            main_obj = get_object_or_404(Achievement, refrence_id=refId, is_main=True)
            obj.delete()
            main_obj.delete()
            messages.success(request, "با موفقیت اعمال شد")
    elif "deny" in model_name:
        obj.delete()
        messages.success(request, "درخواست تغییرات رد شد")
    return HttpResponseRedirect(reverse("base:manage", kwargs={"model_name":"confirm_achievement"}))


@login_required
def manage(request, model_name=""):
    content = {}
    if request.method == "GET":
        if model_name == "achievement":
            content = {
                "achievement": Achievement.objects.filter(is_main=True)
                }
        elif model_name == "student":
            content = {
                "student":Student.objects.all()
                }
        elif model_name == "index":
            pass
        elif model_name == "confirm_achievement":
            if request.user.groups.all()[0].name == "manager":
                content = {
                    "achievement": Achievement.objects.filter(is_main=False, modify_level__in=["manager", "mentor"])
                    }
            elif request.user.groups.all()[0].name == "mentor":
                if request.user.has_perm("base.parvareshi_mentor"):
                    content = {
                        "achievement": Achievement.objects.filter(is_main=False, modify_level__in=["mentor", "student"], 
                        field="پرورشی")
                        }
                elif request.user.has_perm("base.pazhooheshi_mentor"):
                    content = {
                        "achievement": Achievement.objects.filter(is_main=False, modify_level__in=["mentor", "student"], 
                        field="پژوهشی")
                        }
                elif request.user.has_perm("base.varzeshi_mentor"):
                    content = {
                        "achievement": Achievement.objects.filter(is_main=False, modify_level__in=["mentor", "student"], 
                        field="ورزشی")
                        }
                elif request.user.has_perm("base.amoozeshi_mentor"):
                    content = {
                        "achievement": Achievement.objects.filter(is_main=False, modify_level__in=["mentor", "student"], 
                        field="آموزشی")
                        }
            elif request.user.groups.all()[0].name == "student":
                    content = {
                        "achievement": Achievement.objects.filter(is_main=False, modify_level__in=["student"])
                        }

        content.update({"date":timezone.now()})
        return render(request, "base/modiran_frame/managing.html", content)
    elif request.method == "POST":
        searched_obj = []
        if model_name == "achievement":
            for i in get_list_or_404(Achievement, is_main=True):
                if request.POST["owner"]  in f"{i.owner.first_name} + {i.owner.last_name}" and \
                    request.POST["title"] in i.title and request.POST["year"] in str(i.year) and \
                        request.POST["level"] in i.level and request.POST["field"] in i.field and \
                            request.POST["dore"] in i.dore and request.POST["video_link"] in i.video_link and\
                                request.POST["detail"] in i.detail:
                    searched_obj.append(i)
            content = {
                "achievement":searched_obj
            }
            return render(request, "base/modiran_frame/managing.html", content)
        elif model_name == "student":
            searched_year = int(request.POST["birthday"]) if request.POST["birthday"] else 1
            for i in Student.objects.all():
                birth = i.birthday.year if request.POST["birthday"] else 0
                if request.POST["first_name"]  in i.first_name and (request.POST["last_name"])  in i.last_name and \
                    searched_year > birth:
                    searched_obj.append(i)
            content = {
                "student":searched_obj
            }
            return render(request, "base/modiran_frame/managing.html", content)

@login_required
@require_GET
def delete(request, model_name, id):
    if model_name == "student":
        obj = get_object_or_404(Student, id=id)
    elif  model_name == "achievement":
        ref_obj = get_object_or_404(Achievement, refrence_id=id, is_main=True)
        new_obj = Achievement(owner=ref_obj.owner, title=ref_obj.title, year=ref_obj.year, field=ref_obj.field, 
                                level=ref_obj.level, dore=ref_obj.dore, pic=ref_obj.pic, video_link=ref_obj.video_link, 
                                detail=ref_obj.detail, is_deleted=True, modify_level=request.user.groups.all()[0].name)
    new_obj.refrence_id = ref_obj.refrence_id
    new_obj.is_deleted = True
    new_obj.modify_level = request.user.groups.all()[0].name
    new_obj.save()
    messages.success(request, "درخواست با موفقیت ثبت شد")
    return HttpResponseRedirect(reverse('base:manage', args=[model_name]))

@login_required
def form(request, model_name, id):
    request.POST._mutable = True
    if request.method == "GET":
        if model_name == "student":
            obj = get_object_or_404(Student, id=id)
            initial = {
                "first_name":obj.first_name, "last_name":obj.last_name, "birthday":obj.birthday, "photo":obj.photo
            }
            content = {
                "form":StudentForm(initial=initial)
            }
        elif model_name == "new_student":
            content = {
                "form":StudentForm(),
            }
        elif model_name == "achievement":
            obj = get_object_or_404(Achievement, refrence_id=id, is_main=True)
            initial = {
                "owner":obj.owner, "title":obj.title, "year":obj.year, "field":obj.field, "level":obj.level, 
                "dore":obj.dore, "video_link":obj.video_link, "detail":obj.detail, "pic":obj.pic
            }
            content = {
                "form":AchievementForm(initial=initial)
            }
        elif model_name == "new_achievement":
            content = {
                "form":AchievementForm()
            }
        content.update({"date":timezone.now()})
        return render(request,"base/modiran_frame/form.html", content)
    elif request.method == "POST":
        if model_name == "student":
            jy, jm, jd = request.POST["birthday"].split("/")
            miladi_y, miladi_m, miladi_d = extentions.jalali_to_gregorian(int(jy), int(jm) ,int(jd))
            request.POST["birthday"] = f"{miladi_y}-{miladi_m}-{miladi_d}"
            filled_form = StudentForm(request.POST, request.FILES, instance=get_object_or_404(Student, id=id))
            if filled_form.is_valid():
                filled_form.save()
                messages.success(request, "با موفقیت تغییر یافت.")
            else:
                messages.error(request, "خطا، اطلاعات وارد شده معتبر نمی باشد.")
            return HttpResponseRedirect(reverse("base:manage", kwargs={"model_name":model_name}))
        elif model_name == "new_student":
            jy, jm, jd = request.POST["birthday"].split("/")
            miladi_y, miladi_m, miladi_d = extentions.jalali_to_gregorian(int(jy), int(jm) ,int(jd))
            request.POST["birthday"] = f"{miladi_y}-{miladi_m}-{miladi_d}"
            filled_form = StudentForm(request.POST, request.FILES)
            if filled_form.is_valid():
                filled_form.save()
                messages.success(request, "دانش آموز با موفقیت اضافه شد.")
            else:
                messages.error(request, "خطا، اطلاعات وارد شده معتبر نمی باشد.")
            return HttpResponseRedirect(reverse("base:form", kwargs={"model_name":model_name, "id":id}))
        elif model_name == "achievement":
            request.POST["refrence_id"] = id
            request.POST["modify_level"] = request.user.groups.all()[0].name
            filled_form = AchievementForm(request.POST, request.FILES, \
                                            # instance=get_object_or_404(Achievement, id=id)
                                            )
            if filled_form.is_valid():
                filled_form.save()
                messages.success(request, "تغییرات با موفقیت ثبت و پس از تایید مسئول نهایی خواهد شد.")
            else:
                messages.error(request, "خطا، اطلاعات وارد شده معتبر نمی باشد.")
            return HttpResponseRedirect(reverse("base:manage", kwargs={"model_name":model_name}))
        elif model_name == "new_achievement":
            request.POST["refrence_id"] = id
            request.POST["modify_level"] = request.user.groups.all()[0].name
            filled_form = AchievementForm(request.POST, request.FILES)
            if filled_form.is_valid():
                filled_form.save()
                messages.success(request, "دست آورد این دانش آموز با موفقیت ثبت و پس از تایید مسول نهایی خواهد شد.")
            else:
                messages.error(request, "خطا، اطلاعات وارد شده معتبر نمی باشد.")
            return HttpResponseRedirect(reverse("base:form", kwargs={"model_name":model_name, "id":id}))
