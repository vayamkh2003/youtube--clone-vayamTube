from django.contrib import admin

from .models import Channel, Video, UserProfile, Comment

admin.site.register(Channel)
admin.site.register(Video)
admin.site.register(UserProfile)
admin.site.register(Comment)
