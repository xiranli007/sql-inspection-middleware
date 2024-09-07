
from django.contrib import admin
from django.urls import path
from sqlquery import views 

urlpatterns = [
    path("admin/", admin.site.urls),
    path("",views.home) # if the client hit this path, this url will initiate home function in the view
]
