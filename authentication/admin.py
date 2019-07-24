'''The admin module'''
from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    '''Customizes the admin interface'''
    list_display = ['username', 'email', 'is_active',
                    'is_verified', 'is_staff', 'is_superuser'
                    ]
    list_filter = ('is_superuser', 'is_staff', 'is_active', 'is_verified')
    # fields = [('email', 'username'),
    #           ('is_staff', 'is_superuser'), ('is_verified', 'is_active')]
    fieldsets = (
        ('Personal info', {
            'fields': ('email', 'username')
        }),
        ('Role details', {
            'fields': ('is_staff', 'is_superuser')
        }),
        ('Active status', {
            'fields': ('is_verified', 'is_active')
        })
    )


admin.site.register(User, UserAdmin)
admin.site.site_header = "Fadhila"
admin.site.site_title = "Fadhila"
