"""Per-abbreviation majority and TF-IDF + Logistic Regression baselines."""
from collections import Counter, defaultdict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC


def field(example, name):
    return getattr(example, name) if hasattr(example, name) else example[name]


class MajorityBaseline:
    def fit(self, examples):
        counts = defaultdict(Counter)
        for row in examples:
            counts[field(row, "target_abbreviation")][field(row, "gold_sense")] += 1
        if not counts:
            raise ValueError("cannot fit majority baseline on empty data")
        self.label_by_abbr = {
            abbr: sorted(counter.items(), key=lambda item: (-item[1], item[0]))[0][0]
            for abbr, counter in counts.items()
        }
        self.confidence_by_abbr = {
            abbr: max(counter.values()) / sum(counter.values()) for abbr, counter in counts.items()
        }
        return self

    def predict_one(self, example):
        abbr = field(example, "target_abbreviation")
        if abbr not in self.label_by_abbr:
            raise ValueError(f"unseen abbreviation in majority model: {abbr}")
        return self.label_by_abbr[abbr], self.confidence_by_abbr[abbr]

    def predict(self, examples):
        return [self.predict_one(row) for row in examples]


class TfidfLogisticRegression:
    def __init__(self, *, ngram_range=(1, 2), min_df=1, sublinear_tf=True,
                 C=1.0, max_iter=2000, class_weight=None, seed=20261026):
        self.vectorizer_params = dict(ngram_range=tuple(ngram_range), min_df=min_df,
                                      sublinear_tf=sublinear_tf)
        self.classifier_params = dict(C=C, max_iter=max_iter,
                                      class_weight=class_weight, random_state=seed)

    def fit(self, examples):
        by_abbr = defaultdict(list)
        for row in examples:
            by_abbr[field(row, "target_abbreviation")].append(row)
        if not by_abbr:
            raise ValueError("cannot fit Logistic Regression on empty data")
        self.models = {}
        for abbr, rows in sorted(by_abbr.items()):
            labels = [field(row, "gold_sense") for row in rows]
            if len(set(labels)) < 2:
                raise ValueError(f"training split has fewer than two senses for {abbr}")
            vectorizer = TfidfVectorizer(**self.vectorizer_params)
            features = vectorizer.fit_transform([field(row, "text") for row in rows])
            classifier = LogisticRegression(**self.classifier_params)
            classifier.fit(features, labels)
            self.models[abbr] = (vectorizer, classifier)
        return self

    def predict_one(self, example):
        abbr = field(example, "target_abbreviation")
        if abbr not in self.models:
            raise ValueError(f"unseen abbreviation in Logistic Regression model: {abbr}")
        vectorizer, classifier = self.models[abbr]
        distribution = classifier.predict_proba(vectorizer.transform([field(example, "text")]))[0]
        best = int(distribution.argmax())
        return str(classifier.classes_[best]), float(distribution[best])

    def predict(self, examples):
        return [self.predict_one(row) for row in examples]


class TfidfLinearSVM:
    """Per-abbreviation TF-IDF + Linear SVM baseline."""

    def __init__(self, *, ngram_range=(1, 2), min_df=1, sublinear_tf=True,
                 C=1.0, class_weight=None, seed=20261026):
        self.vectorizer_params = dict(ngram_range=tuple(ngram_range), min_df=min_df,
                                      sublinear_tf=sublinear_tf)
        self.classifier_params = dict(C=C, class_weight=class_weight, random_state=seed)

    def fit(self, examples):
        by_abbr = defaultdict(list)
        for row in examples:
            by_abbr[field(row, "target_abbreviation")].append(row)
        if not by_abbr:
            raise ValueError("cannot fit Linear SVM on empty data")
        self.models = {}
        for abbr, rows in sorted(by_abbr.items()):
            labels = [field(row, "gold_sense") for row in rows]
            if len(set(labels)) < 2:
                raise ValueError(f"training split has fewer than two senses for {abbr}")
            vectorizer = TfidfVectorizer(**self.vectorizer_params)
            features = vectorizer.fit_transform([field(row, "text") for row in rows])
            classifier = LinearSVC(**self.classifier_params)
            classifier.fit(features, labels)
            self.models[abbr] = (vectorizer, classifier)
        return self

    def predict_one(self, example):
        abbr = field(example, "target_abbreviation")
        if abbr not in self.models:
            raise ValueError(f"unseen abbreviation in Linear SVM model: {abbr}")
        vectorizer, classifier = self.models[abbr]
        decision = classifier.decision_function(vectorizer.transform([field(example, "text")]))
        if len(classifier.classes_) == 2:
            margin = float(decision[0])
            best = 1 if margin > 0 else 0
            confidence = abs(margin)
        else:
            scores = decision[0]
            best = int(scores.argmax())
            confidence = float(scores[best])
        return str(classifier.classes_[best]), confidence

    def predict(self, examples):
        return [self.predict_one(row) for row in examples]
