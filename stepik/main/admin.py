from django.contrib import admin
from .models import Course, Video, LessonContainer, Learner, Category, Comment
from django import forms

class MyAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if request.user.groups.filter(name='teacher').exists():
            form.base_fields['is_published'].widget.attrs['disabled'] = True
        elif request.user.groups.filter(name='moderator').exists():
            form.base_fields['idUser'].widget.attrs['readonly'] = True    
        return form
    
admin.site.register(Video)
admin.site.register(LessonContainer)
admin.site.register(Category)
admin.site.register(Learner)
admin.site.register(Course, MyAdmin)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'body', 'post', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)
