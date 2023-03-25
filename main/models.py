from django.db import models

class Authors(models.Model):
    name = models.TextField()


class Categories(models.Model):
    name = models.TextField()

    def __str__(self) -> str:
        return self.name


class Article(models.Model):
    title = models.TextField()
    author = models.ManyToManyField(Authors, blank=True)
    date = models.DateTimeField()
    link = models.TextField()
    categories = models.ManyToManyField(Categories, blank=True)
    text = models.TextField()
    snippet = models.TextField()

    def __str__(self) -> str:
        return self.title

    def getCategories(self):
        return ", ".join([item.name for item in self.categories.all()])

    def getAuthors(self):
        return ", ".join([item.name for item in self.author.all()])