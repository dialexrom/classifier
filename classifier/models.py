import pandas as pd
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from pickle import dump, load
from application.settings import MODEL_PATH

"""Main module for training"""

class classifier:

    def __init__(self, model, vect, transformer):
        self.svcmodel = model
        self.transformer = transformer
        self.vectorizer = vect

    @classmethod
    def textPreparator(cls, text: str):
        tokenizer = RegexpTokenizer("\w+")
        words = tokenizer.tokenize(text.lower())
        significant_words = [
            word for word in words if word not in stopwords.words("english")
        ]
        lemmatizer = WordNetLemmatizer()
        lemms = [lemmatizer.lemmatize(word) for word in significant_words]
        return " ".join(lemms)
    
    @classmethod
    def loadFile(cls):
        model, vectorizer, transformer = load(open(MODEL_PATH, "rb"))
        return cls(model, vectorizer, transformer)

    @classmethod
    def createModelFromData(cls, texts: list):
        prepared_texts = [
            {"label": article.getCategories, "text": cls.textPreparator(article.text)}
            for article in texts
        ]
        data = pd.DataFrame(prepared_texts, dtype=object)
        count_vect = CountVectorizer()
        counts = count_vect.fit_transform(data["text"])
        transformer = TfidfTransformer().fit(counts)
        counts = transformer.transform(counts)
        model = cls.trainModel(counts, data["label"])
        dump((model, count_vect, transformer), open(MODEL_PATH, "wb"))
        return cls(model, count_vect, transformer)

    @classmethod
    def trainModel(cls, tf_idf: pd.Series, labels: pd.Series):
        X_train, X_test, y_train, y_test = train_test_split(
            tf_idf, labels, test_size=0.3, random_state=69
        )
        svcmodel = SVC(kernel="rbf", C=3)
        svcmodel.fit(X_train, y_train)
        return svcmodel

    def classificateText(self, text: str):
        prepared_text = self.textPreparator(text)
        df = pd.DataFrame({"text": [prepared_text]}, dtype=object)
        counts = self.transformer.transform(
            self.vectorizer.transform(df["text"])
        )
        return self.svcmodel.predict(counts)
