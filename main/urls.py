from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from classifier import views as classifier_views
from main import views


urlpatterns = [
    path("", views.redirect),
    path("classificate", classifier_views.classificate),
    path("newfile", views.saveFileInDB),
    path("train", classifier.train),
    re_path(r"^articles/(?P<page>\d+)", views.index),
    re_path(r"^articles/text/(?P<id>.+)", views.getTextFromArticle),
    re_path(r"^articles/delete/(?P<id>.+)", views.removeArticle),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
