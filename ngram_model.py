import re
from collections import defaultdict, Counter

class NGramModel:
    def __init__(self, n=2):
        self.n = n
        self.n_grams = defaultdict(Counter)
        self.word_freq = Counter()
        self.total_words = 0

    def tokenize(self, text):
        text = text.lower()
        text = re.sub(r"[^\w\s']", ' ', text)
        text = re.sub(r"\s+", ' ', text).strip()
        return text.split()

    def train(self, corpus):
        for text in corpus:
            tokens = self.tokenize(text)
            self.word_freq.update(tokens)
            self.total_words += len(tokens)

            for i in range(len(tokens) - self.n + 1):
                context = ' '.join(tokens[i:i + self.n - 1])
                target = tokens[i + self.n - 1]
                self.n_grams[context][target] += 1

    def get_probability(self, context, word):
        context = ' '.join(self.tokenize(context)[-self.n + 1:])
        if context not in self.n_grams:
            return self.word_freq[word] / self.total_words if word in self.word_freq else 0.0

        context_total = sum(self.n_grams[context].values())
        return self.n_grams[context][word] / context_total if word in self.n_grams[context] else 0.0

    def get_next_word_candidates(self, context, count=5):
        context = ' '.join(self.tokenize(context)[-self.n + 1:])
        if context not in self.n_grams:
            return [word for word, _ in self.word_freq.most_common(count)]

        return [word for word, _ in self.n_grams[context].most_common(count)]

    def detect_contextual_errors(self, text, threshold=0.01):
        tokens = self.tokenize(text)
        if len(tokens) < self.n:
            return []

        errors = []
        for i in range(self.n - 1, len(tokens)):
            context = ' '.join(tokens[i - self.n + 1:i])
            word = tokens[i]
            prob = self.get_probability(context, word)

            if prob < threshold:
                suggestions = self.get_next_word_candidates(context)
                errors.append({
                    'word': word,
                    'position': i,
                    'context': context,
                    'suggestions': suggestions
                })
        return errors
