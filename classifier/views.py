"""Handle views here"""
from main.forms import textForm
from django.db.utils import OperationalError
from django.shortcuts import render
from main.models import Article
from django.http import HttpResponseRedirect
from .models import classifier


def train(request):
    global classifier
    try:
        classifier = classifier.createModelFromData(Article.objects.all())
    except OperationalError:
        render(
            request,
            "errors.html",
            {"text": "Отсутствует соединение с базой данных","code": 503},
            status=503
        )
    return render(request, "train_is_complete.html")


def classificate(request):
    if "classifier" not in globals():
        global classifier
        try:
            classifier = classifier.loadFile()
        except FileNotFoundError:
            code = 503
            return render(
                request,
                "errors.html",
                {"text": "Сначала обучите классификатор","code": code},
                status=code
            )
    if request.method == "POST":
        text = request.POST.get("text")
        result = classifier.classificateText(text)[0]
        res = {"ANIMALS": "Animals", "MAGAZINE": "Magazine", "TRAVEL":'Travel'}
        return render(request, "predict_res.html", {"category": res[result]})
    else:
        form = textForm()
        return render(request, "text_predict.html", {"form": form})
