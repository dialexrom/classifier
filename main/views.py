from django.shortcuts import render
from django.http import HttpResponseRedirect
from lxml import etree
from .forms import filterForm, textForm
from .models import (
    Article,
    Authors,
    Categories,
)
import datetime
from re import search
from django.db.utils import OperationalError
from django.core.paginator import Paginator

# Create your views here.


def checkDB(table, items: list) -> list:
    return [
        table.objects.get_or_create(name=item)[0]
        for item in items
        if item != ""
    ]


def redirect(request):
    return HttpResponseRedirect("articles/1")


def index(request, num = 0):
    selected_label = request.GET.get("selected_label", None)
    direction_sort = request.GET.get("sorting", 0)
    if direction_sort not in {'0', '1'}:
        direction_sort = 0
    sort_by = "date" if int(direction_sort) else "-date"
    try:
        articles = Article.objects.filter(label=selected_label)
        articles = Article.objects.all()
        category = "ALL"
        pages = Paginator(list(articles.order_by(sort_by)), 10)
        page_obj = pages.get_page(num)
        return render(
            request,
            "index.html",
            {
                "articles": page_obj,
                "count": articles.count(),
                "filter_form": filterForm,
                "category": category,
            },
        )
    except OperationalError:
        return render(
            request,
            "errors.html",
            {"text": "No connection to database","code":503},
            status=503
        )


def parseFile(request, file):
    if not search("\.xml", file.name):
        return render(
            request,
            "errors.html",
            {"text": "incorrect file extention","code":422},
            status=422
        )
    # print('write',file)
    with open("schema.xsd", "r") as f:
        schema_root = etree.XML(f.read())
    parser = etree.XMLParser(schema=etree.XMLSchema(schema_root))
    try:
        tree = etree.parse(file, parser)
    except etree.XMLSyntaxError:
        return render(
            "errors.html",
            {"text": "Validation error","code":422},
            status=422
        )

    root = tree.getroot()
    title = root.findall(".//title")[0].text
    date_s = root.findall(".//publish_date")[0].text.replace(",", "") 
    date = datetime.datetime.strptime(date_s, "%B %d %Y").date().isoformat()
    link = root.findall(".//url")[0].text
    text = root.findall(".//text")[0].text
    snippet = text[0:350]

    categories = checkDB(
        Categories, [root.findall(".//categories/item")[0].text]
    )
    authors = checkDB(
        Authors, [item.text for item in root.findall(".//author")]
    )
    current_article = Article.objects.filter(title=title, text=text, date=date, snippet=snippet)
    if not current_article:
        current_article = Article(
         title=title, date=date, link=link, text=text, snippet=snippet
        )
        current_article.save()
        current_article.author.add(*[author.id for author in authors])
        current_article.categories.add(
            *[category.id for category in categories]
        )
    return HttpResponseRedirect("/")


def saveFileInDB(request):
    if request.method == "POST":
        file = request.FILES.get("name", None)
        if file:
            try:
                return parseFile(request, file)
            except OperationalError:
                return render(
                    request,
                    "errors.html",
                    {"text": "Отсутствует соединение с базой данных","code": 503},
                    status=503
                )
        return render(
            request,
            "errors.html",
            {"text": "Файл не выбран","code": 422},
            status=422
        )
    else:
        return render(request, "add_form.html")


def removeArticle(request, id):
    if not id:
        return render(
            request,
            "errors.html",
            {"text": "Atricle not chose","code": 422},
            status=422
        )
    if int(id) < 0:
        return render(
            request,
            "errors.html",
            {"text": "Wrong article id","code": 422},
            status=422
        )
    try:
        selected_article = Article.objects.get(id=id)
        if request.method == "POST":
            selected_article.delete()
            return render(request,
                "delete_res.html",
                {"title": selected_article.title}
            )
        else:
            return render(request,
                "delete_text_form.html",
                {"title": selected_article.title}
            )
    except OperationalError:
        return render(
            request,
            "errors.html",
            {"text": "No connection to database","code": 503},
            status=503
        )


def getTextFromArticle(request, id):
    if not id:
        return render(
            request,
            "errors.html",
            {"text": "Choose article!","code": 422},
            status=422
        )
    if int(id) < 0:
        return render(
            request,
            "errors.html",
            {"text": "Incorrect article id","code": 422},
            status=422
        )
    try:
        article = Article.objects.get(id=id)
        if request.method == "POST":
            new_text = request.POST.get("text")
            article.text = new_text
            article.save()
            return HttpResponseRedirect("/")
        else:
            form = textForm(initial={"text": article.text})
            return render(request, "text_form.html", {"form": form})
    except OperationalError:
        return render(
            request,
            "errors.html",
            {"text": "No connection to database","code": 503},
            status=503
        )

# import pathlib
# for filepath in pathlib.Path("C://Users//PC//project//xml_dir_di_travel//").glob('**/*'):
#     parseFile(filepath.absolute())
# parseFile("C://Users//PC//project//xml_dir_di_animals//3.xml")