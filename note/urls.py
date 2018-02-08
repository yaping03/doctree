"""note URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
# from django.urls import include, url
from doctree import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('doctree/<str:title>', views.doctree, name='doctree'),
    path('docmerge', views.docmerge, name='docmerge'),
    path('knowledge/<int:kid>', views.knowledge, name="knowledge"),
    path('kwmerge', views.kwmerge, name="kwmerge"),
    path('kwlist', views.kwlist, name='kwlist'),
    path('l5list', views.l5list, name='l5list'),
    path('show_relationship/<str:title>', views.show_relationship, name='show_relationship'),
    path('rejectlist', views.rejectlist, name='rejectlist'),
    path('booklist', views.booklist, name='booklist'),
    path('linkmissing', views.linkmissing, name='linkmissing'),
    path('lawlist/', views.lawlist,name="lawlist"),
    path('lawtitle/<int:law_id>', views.law_title,name="lawtitle"),
    path('provision/<int:law_id>/<str:types>/<int:parent_id>',views.provision_view,name="provision"),
    path('knowledge/<int:kid>/add', views.add_knowledge, name="knowledge_add"),
    path('knowledge/<int:kid>/edit', views.edit_knowledge, name="knowledge_edit"),
    path('export_file',views.export_file, name="export_file"),
    path('h4add',views.add_h4, name="add_h4"),
    path('bookchapter/<int:bid>',views.book_chapter, name="book_chapter"),
]
