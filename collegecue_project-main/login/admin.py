from django.contrib import admin # type: ignore
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # type: ignore
from django.contrib.auth.forms import UserChangeForm # type: ignore
from .models import CompanyInCharge,Consultant,UniversityInCharge,CustomUser,OTP, User,new_user,Forgot,Forgot2,Verify,Subscriber,Subscriber1
from .utils import is_superadmin

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser

class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm

    def save_model(self, request, obj, form, change):
        if not obj.pk and is_superadmin(request.user):
            obj.is_subadmin = True
        super().save_model(request, obj, form, change)


admin.site.register(CompanyInCharge)
admin.site.register(Consultant)
admin.site.register(UniversityInCharge)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(OTP)
admin.site.register(new_user)
admin.site.register(Forgot)
admin.site.register(Forgot2)
admin.site.register(Verify)
admin.site.register(Subscriber)
admin.site.register(Subscriber1)
admin.site.register(User)