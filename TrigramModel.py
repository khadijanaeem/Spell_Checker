import re
from collections import defaultdict, Counter
import math

class TrigramModel:
    def __init__(self):
        self.trigram_counts = defaultdict(Counter)
        self.bigram_counts = defaultdict(Counter)
        self.vocabulary = set()
        self.sentences_set = set()

    def tokenize(self, text):
        return re.findall(r"\b\w+\b", text.lower())

    def train(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                clean_line = line.strip()
                if not clean_line:
                    continue
                self.sentences_set.add(clean_line.lower())
                tokens = ["<s>", "<s>"] + self.tokenize(clean_line) + ["</s>"]
                self.vocabulary.update(tokens)

                for i in range(len(tokens) - 2):
                    trigram = (tokens[i], tokens[i+1], tokens[i+2])
                    bigram = (tokens[i], tokens[i+1])
                    self.trigram_counts[bigram][tokens[i+2]] += 1
                    self.bigram_counts[bigram] += Counter()

    def get_probability(self, context, word):
        bigram = tuple(context)
        if bigram in self.trigram_counts:
            total = sum(self.trigram_counts[bigram].values())
            word_count = self.trigram_counts[bigram][word]
            if total > 0:
                return word_count / total
        return 0.0

    def suggest_replacement(self, context, word):
        bigram = tuple(context)
        if bigram in self.trigram_counts:
            suggestions = self.trigram_counts[bigram].most_common(5)
            return [w for w, _ in suggestions if w != word]
        return []

    def correct_sentence(self, sentence):
        # Check if it's an exact match with training data
        if sentence.lower() in self.sentences_set:
            return sentence, []

        tokens = ["<s>", "<s>"] + self.tokenize(sentence) + ["</s>"]
        corrected = tokens[:2]
        suggestions_report = []

        for i in range(2, len(tokens)):
            context = [tokens[i-2], tokens[i-1]]
            word = tokens[i]
            prob = self.get_probability(context, word)

            if prob < 0.01 and word not in ["</s>"]:
                alternatives = self.suggest_replacement(context, word)
                if alternatives:
                    suggestions_report.append({
                        "word": word,
                        "context": f"{context[0]} {context[1]}",
                        "suggestions": alternatives
                    })
                    corrected.append(alternatives[0])  # Replace with top suggestion
                else:
                    corrected.append(word)
            else:
                corrected.append(word)

        final_sentence = " ".join(corrected[2:-1])
        return final_sentence, suggestions_report


# === Example usage ===
if __name__ == "__main__":
    model = TrigramModel()
    model.train("corpus.txt")  # <-- your file with ~100 correct sentences

    # Input sentence with contextual errors
    user_input = "There friend is always late"
    corrected_sentence, report = model.correct_sentence(user_input)

    print("Original:", user_input)
    print("Corrected:", corrected_sentence)
    if report:
        for err in report:
            print(f"\nWord '{err['word']}' seems unusual in context '{err['context']}'")
            print("Suggestions:", ", ".join(err["suggestions"]))
    else:
        print("No contextual errors detected.")
