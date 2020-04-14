from ads_app import views
from django.urls import path
from django.conf.urls import handler404

app_name = 'ads_app'
urlpatterns = [
    path('', views.AdvertList.as_view(), name='advert-list'),
    path('id<int:pk>', views.advert_detail, name='advert-detail'),
    path('create', views.AdvertCreate.as_view(), name="advert-create"),
    path("update/<int:pk>", views.AdvertUpdate.as_view(), name="advert-update"),
    path("delete/<int:pk>", views.AdvertDelete.as_view(), name="advert-delete"),
    path("comment/create/<int:pk>", views.create_comment, name="comment-create"),
    path("comment/updateform/<int:pk>-<int:id>", views.comment_update_form, name="comment-update-form"),
    path("comment/update/<int:pk>-<int:id>", views.update_comment, name="comment-update"),
    path("comment/delete/<int:pk>-<int:id>", views.delete_comment, name="comment-delete"),
    path("comment/cancel/<int:pk>", views.cancel_comment, name="comment-cancel"),
]

handler404 = 'ads_app.views.error_404_view'
