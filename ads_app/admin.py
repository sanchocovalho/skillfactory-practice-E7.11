from django.contrib import admin
from ads_app.models import Comment, Category, Advert

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Advert)
class AdvertAdmin(admin.ModelAdmin):
	pass