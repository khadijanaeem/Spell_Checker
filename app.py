# Import necessary libraries and modules
from flask import Flask, render_template, request,jsonify, redirect, url_for, flash,session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from autocorrect import Speller
from language_tool_python import LanguageToolPublicAPI
import nltk
import random
import string
import sqlite3
from symspellpy.symspellpy import SymSpell, Verbosity

nltk.data.path.append(r"C:\\Users\\X1 EXTREME\\AppData\\Roaming\\nltk_data")

nltk.download('punkt')

from nltk.tokenize import word_tokenize

from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize,sent_tokenize
from nltk.tag import pos_tag
from collections import Counter
import logging
from ngram_model import NGramModel
import re
import secrets
from nltk.metrics import edit_distance
from difflib import get_close_matches
import Levenshtein
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
from nltk.corpus import words
nltk.download('words')
word_list = words.words()

bigramModel = NGramModel(n=2)
trigramModel =  NGramModel(n=3)

# Sample corpus from the JS version
with open('corpus.txt', 'r') as f:
    corpus_lines = f.readlines()

bigramModel.train(corpus_lines)
trigramModel.train(corpus_lines)


# Create a Flask application instance
app = Flask(__name__)

app.secret_key = '4f3d2f3c4a7e896fbd2d3a1b8e7a9f00'
spell = Speller(lang='en')
# Create a LanguageTool object for grammar and spell checking
tool = LanguageToolPublicAPI('en-US')
# Add the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'abc'
db = SQLAlchemy(app)

# Profile
class profile(db.Model):
    userName = db.Column(db.String(120), primary_key=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)

# Custom Dicitionary
class custom_dictionary(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userName = db.Column(db.String(120), nullable=False)
    word = db.Column(db.String(120), nullable=False)
    



with app.app_context():
    db.create_all()


def custom_grammar_correction(text):
    """
    Custom grammar check function to address issues not caught by LanguageTool.
    This includes:
    - Sentence fragmentation
    - Inconsistent verb tenses
    - Comma splices
    - Wordiness and filler words
    - Ambiguous pronouns
    - Inconsistent punctuation
    """
    corrected_text = text
    corrected_text = re.sub(r'\b[Dd]o you liking\b', 'Do you like', corrected_text)
    corrected_text = re.sub(r'\b[Dd]o you playing\b', 'Are you playing', corrected_text)
    # 1. Fix sentence fragmentation (Detect 'and then she.' type fragments)
    corrected_text = re.sub(r'(\w+)\.\s+And\s+then\s+(\w+)', r'\1. \2', corrected_text)

    # 2. Fix inconsistent verb tenses (Correct "I like to did science" to "I like to do science")
    # We specifically fix cases like "I like to did" which is incorrect
    corrected_text = re.sub(r'\bI like to did\b', 'I like to do', corrected_text)

    # 3. Fix comma splice issues (Detect common run-on sentences)
    corrected_text = re.sub(r'(\w+), (\w+)', r'\1; \2', corrected_text)

    # 4. Address wordiness/filler words (Remove unnecessary fillers like 'really', 'just')
    filler_words = ['really', 'just', 'very', 'actually']
    for word in filler_words:
        corrected_text = re.sub(r'\b' + word + r'\b', '', corrected_text)

    # 5. Fix ambiguous pronouns (In a complex case, more context would be needed for disambiguation)
    # Simple approach: Check for pronouns like "he", "she", "it" without a clear noun reference
    corrected_text = re.sub(r'\b(he|she|it)\b', 'they', corrected_text)

    # 6. Fix inconsistent punctuation (Check for misplaced commas and semicolons)
    corrected_text = re.sub(r'(\w+), (\w+)', r'\1; \2', corrected_text)
    
    # Final cleanup for any extra spaces or formatting issues
    corrected_text = ' '.join(corrected_text.split())

    return corrected_text

def correct_grammar(text):
    """Check and correct grammatical errors using LanguageTool"""
    # Use LanguageTool to find grammar mistakes
    errors = tool.check(text)
    # Get the corrected text from LanguageTool
    corrected_text = tool.correct(text)

    # Prepare a summary of grammar mistakes
    grammar_mistakes = []
    for error in errors:
        grammar_mistakes.append({
            'message': error.message,
            'context': error.context,
            'replacements': error.replacements
        })

    logger.info(f"Grammar corrections made: {grammar_mistakes}")
    
    return corrected_text, grammar_mistakes
# Custom dictionary of common words and their synonyms
COMMON_SYNONYMS = {
    
    'angry': ['furious', 'irate', 'enraged', 'mad', 'livid'],
    'brave': ['courageous', 'fearless', 'bold', 'valiant', 'heroic'],
    'calm': ['peaceful', 'tranquil', 'serene', 'placid', 'composed'],
    'dangerous': ['risky', 'hazardous', 'perilous', 'unsafe', 'treacherous'],
    'eager': ['keen', 'enthusiastic', 'anxious', 'excited', 'zealous'],
    'famous': ['renowned', 'celebrated', 'notable', 'well-known', 'illustrious'],
    'generous': ['charitable', 'benevolent', 'kind', 'openhanded', 'philanthropic'],
    'happy': ['joyful', 'cheerful', 'content', 'delighted', 'gleeful'],
    'intelligent': ['smart', 'bright', 'clever', 'brainy', 'knowledgeable'],
    'jealous': ['envious', 'covetous', 'resentful', 'green-eyed', 'grudging'],
    'kind': ['benevolent', 'compassionate', 'gentle', 'considerate', 'sympathetic'],
    'lazy': ['idle', 'slothful', 'indolent', 'lethargic', 'inactive'],
    'mysterious': ['enigmatic', 'cryptic', 'puzzling', 'unfathomable', 'arcane'],
    'nervous': ['anxious', 'apprehensive', 'tense', 'edgy', 'restless'],
    'optimistic': ['hopeful', 'positive', 'upbeat', 'sanguine', 'confident'],
    'polite': ['courteous', 'respectful', 'well-mannered', 'civil', 'gracious'],
    'quiet': ['silent', 'hushed', 'muted', 'soft-spoken', 'reserved'],
    'rude': ['impolite', 'disrespectful', 'ill-mannered', 'crude', 'insolent'],
    'strong': ['powerful', 'sturdy', 'robust', 'forceful', 'mighty'],
    'tired': ['weary', 'fatigued', 'exhausted', 'drained', 'sleepy'],
    'ugly': ['unattractive', 'hideous', 'unsightly', 'repulsive', 'grotesque'],
    'vivid': ['bright', 'brilliant', 'intense', 'radiant', 'luminous'],
    'warm': ['hot', 'heated', 'balmy', 'toasty', 'cozy'],
    'young': ['youthful', 'juvenile', 'adolescent', 'immature', 'fresh'],
    'zealous': ['enthusiastic', 'eager', 'passionate', 'fervent', 'ardent'],
    'beautiful': ['pretty', 'lovely', 'gorgeous', 'stunning', 'attractive', 'charming', 'elegant'],
    'pretty': ['beautiful', 'lovely', 'attractive', 'charming', 'cute', 'good-looking'],
    'fast': ['quick', 'rapid', 'swift', 'speedy', 'brisk', 'hasty'],
    'slow': ['sluggish', 'leisurely', 'unhurried', 'gradual', 'delayed'],
    'happy': ['joyful', 'cheerful', 'delighted', 'pleased', 'content', 'glad'],
    'sad': ['unhappy', 'depressed', 'downcast', 'gloomy', 'melancholy'],
    'big': ['large', 'huge', 'enormous', 'gigantic', 'massive', 'colossal'],
    'small': ['little', 'tiny', 'miniature', 'petite', 'compact'],
    'good': ['excellent', 'great', 'wonderful', 'superb', 'outstanding', 'fantastic'],
    'bad': ['poor', 'terrible', 'awful', 'horrible', 'dreadful'],
    'smart': ['intelligent', 'clever', 'bright', 'brilliant', 'wise'],
    'dumb': ['stupid', 'unintelligent', 'foolish', 'silly', 'idiotic'],
    'rich': ['wealthy', 'affluent', 'prosperous', 'well-off', 'loaded'],
    'poor': ['impoverished', 'needy', 'destitute', 'broke', 'unfortunate'],
    'strong': ['powerful', 'mighty', 'forceful', 'sturdy', 'tough'],
    'weak': ['feeble', 'frail', 'fragile', 'delicate', 'powerless'],
    'old': ['aged', 'elderly', 'ancient', 'vintage', 'antique'],
    'new': ['fresh', 'modern', 'recent', 'novel', 'contemporary'],
    'clean': ['spotless', 'immaculate', 'pristine', 'tidy', 'neat'],
    'dirty': ['filthy', 'soiled', 'unclean', 'grimy', 'stained'],
    'easy': ['simple', 'effortless', 'uncomplicated', 'straightforward'],
    'hard': ['difficult', 'challenging', 'tough', 'complicated', 'complex'],
    'funny': ['humorous', 'amusing', 'comical', 'hilarious', 'entertaining'],
    'serious': ['solemn', 'grave', 'earnest', 'sober', 'thoughtful'],
    'loud': ['noisy', 'boisterous', 'deafening', 'thunderous', 'raucous'],
    'quiet': ['silent', 'hushed', 'muted', 'soft', 'peaceful'],
    'bright': ['shining', 'brilliant', 'radiant', 'luminous', 'glowing'],
    'dark': ['dim', 'gloomy', 'shadowy', 'murky', 'obscure'],
    'hot': ['warm', 'heated', 'scorching', 'boiling', 'sizzling'],
    'cold': ['chilly', 'freezing', 'frigid', 'icy', 'frosty'],
    'wet': ['damp', 'moist', 'soaked', 'soggy', 'drenched'],
    'dry': ['arid', 'parched', 'dehydrated', 'desiccated', 'thirsty'],
    'soft': ['gentle', 'tender', 'delicate', 'mild', 'pliable'],
    'hard': ['firm', 'solid', 'rigid', 'stiff', 'tough'],
    'sweet': ['sugary', 'honeyed', 'delicious', 'pleasant', 'lovely'],
    'sour': ['tart', 'acidic', 'bitter', 'sharp', 'tangy'],
    'tall': ['high', 'lofty', 'towering', 'elevated', 'statuesque'],
    'short': ['small', 'little', 'petite', 'diminutive', 'compact'],
    'fat': ['overweight', 'plump', 'chubby', 'obese', 'heavy'],
    'thin': ['slim', 'slender', 'lean', 'skinny', 'svelte'],
    'young': ['youthful', 'juvenile', 'adolescent', 'immature', 'fresh'],
    'brave': ['courageous', 'fearless', 'bold', 'heroic', 'valiant'],
    'cowardly': ['fearful', 'timid', 'faint-hearted', 'spineless', 'chicken'],
    'kind': ['benevolent', 'compassionate', 'generous', 'caring', 'thoughtful'],
    'mean': ['cruel', 'unkind', 'nasty', 'malicious', 'spiteful'],
    'honest': ['truthful', 'sincere', 'frank', 'candid', 'genuine'],
    'dishonest': ['deceitful', 'untruthful', 'fraudulent', 'corrupt', 'deceptive'],
    'polite': ['courteous', 'respectful', 'well-mannered', 'civil', 'gracious'],
    'rude': ['impolite', 'disrespectful', 'uncivil', 'crude', 'insolent'],
    'patient': ['tolerant', 'understanding', 'forbearing', 'calm', 'composed'],
    'impatient': ['restless', 'eager', 'anxious', 'agitated', 'fidgety'],
    'generous': ['giving', 'charitable', 'benevolent', 'unselfish', 'liberal'],
    'stingy': ['miserly', 'greedy', 'selfish', 'tightfisted', 'cheap'],
    'friendly': ['amiable', 'sociable', 'affable', 'cordial', 'warm'],
    'unfriendly': ['hostile', 'antagonistic', 'cold', 'aloof', 'distant'],
    'lazy': ['idle', 'slothful', 'indolent', 'inactive', 'lethargic'],
    'active': ['energetic', 'dynamic', 'vigorous', 'lively', 'spirited'],
    'calm': ['peaceful', 'tranquil', 'serene', 'placid', 'composed'],
    'angry': ['furious', 'enraged', 'irate', 'mad', 'outraged'],
    'busy': ['occupied', 'engaged', 'active', 'industrious', 'diligent'],
    'free': ['available', 'unoccupied', 'unrestricted', 'liberated', 'unbound'],
    'safe': ['secure', 'protected', 'guarded', 'shielded', 'harmless'],
    'dangerous': ['risky', 'hazardous', 'perilous', 'unsafe', 'threatening'],
    'healthy': ['fit', 'well', 'robust', 'strong', 'vigorous'],
    'sick': ['ill', 'unwell', 'ailing', 'diseased', 'infected'],
     'tired': ['weary', 'exhausted', 'fatigued', 'sleepy', 'drowsy'],
    'energetic': ['lively', 'animated', 'active', 'spirited', 'vibrant'],
    'shy': ['bashful', 'timid', 'introverted', 'reserved', 'withdrawn'],
    'confident': ['self-assured', 'bold', 'self-reliant', 'assertive', 'certain'],
    'cheap': ['inexpensive', 'affordable', 'economical', 'budget', 'low-cost'],
    'expensive': ['costly', 'pricey', 'high-priced', 'lavish', 'luxurious'],
    'noisy': ['loud', 'boisterous', 'raucous', 'clamorous', 'rowdy'],
    'silent': ['quiet', 'hushed', 'mute', 'soundless', 'tranquil'],
    'simple': ['basic', 'plain', 'straightforward', 'uncomplicated', 'easy'],
    'complex': ['complicated', 'intricate', 'elaborate', 'detailed', 'involved'],
    'broken': ['damaged', 'cracked', 'shattered', 'fractured', 'wrecked'],
    'fixed': ['repaired', 'mended', 'restored', 'corrected', 'reconditioned'],
    'angry': ['furious', 'irate', 'mad', 'livid', 'enraged'],
    'happy': ['joyful', 'gleeful', 'content', 'merry', 'elated'],
    'beautiful': ['stunning', 'gorgeous', 'pretty', 'lovely', 'charming'],
    'ugly': ['unattractive', 'hideous', 'unsightly', 'unappealing', 'grotesque'],
    'easy': ['simple', 'effortless', 'straightforward', 'basic', 'light'],
    'difficult': ['hard', 'challenging', 'tough', 'arduous', 'demanding'],
    'fun': ['enjoyable', 'entertaining', 'amusing', 'delightful', 'exciting'],
    'boring': ['dull', 'tedious', 'uninteresting', 'monotonous', 'dry'],
    'helpful': ['useful', 'beneficial', 'advantageous', 'supportive', 'valuable'],
    'useless': ['pointless', 'worthless', 'ineffective', 'futile', 'unproductive'],
    'warm': ['hot', 'heated', 'cozy', 'balmy', 'toasty'],
    'cool': ['chilly', 'cold', 'refreshing', 'crisp', 'brisk'],
    'important': ['crucial', 'vital', 'essential', 'significant', 'necessary'],
    'unimportant': ['insignificant', 'trivial', 'minor', 'inconsequential', 'irrelevant'],
    'funny': ['amusing', 'comical', 'witty', 'hilarious', 'entertaining'],
    'serious': ['sober', 'grave', 'earnest', 'thoughtful', 'intense'],
    'early': ['premature', 'beforehand', 'in advance', 'prompt', 'ahead'],
    'late': ['tardy', 'belated', 'delayed', 'overdue', 'behind'],
    'strong': ['powerful', 'mighty', 'forceful', 'muscular', 'robust'],
    'fragile': ['delicate', 'brittle', 'breakable', 'frail', 'weak'],
    'safe': ['secure', 'protected', 'guarded', 'sheltered', 'risk-free'],
    'risky': ['dangerous', 'hazardous', 'perilous', 'uncertain', 'unsafe'],
    'real': ['authentic', 'genuine', 'actual', 'true', 'legitimate'],
    'fake': ['false', 'phony', 'counterfeit', 'bogus', 'fraudulent'],
    'creative': ['imaginative', 'innovative', 'original', 'artistic', 'inventive'],
    'boring': ['dull', 'tedious', 'unexciting', 'unimaginative', 'stale'],
    'careful': ['cautious', 'alert', 'attentive', 'watchful', 'prudent'],
    'careless': ['reckless', 'negligent', 'thoughtless', 'irresponsible', 'sloppy'],
    'bright': ['vivid', 'shiny', 'radiant', 'glowing', 'dazzling'],
    'dull': ['dim', 'drab', 'lackluster', 'faint', 'muted'],
    'thick': ['dense', 'bulky', 'chunky', 'fat', 'solid'],
    'thin': ['slim', 'lean', 'slender', 'narrow', 'skinny'],
    'sharp': ['pointed', 'keen', 'razor-edged', 'piercing', 'acute'],
    'blunt': ['dull', 'rounded', 'unsharpened', 'flat', 'direct'],
    'friendly': ['kind', 'amiable', 'welcoming', 'cordial', 'pleasant'],
    'hostile': ['unfriendly', 'aggressive', 'antagonistic', 'bitter', 'offensive'],
    'neat': ['tidy', 'orderly', 'organized', 'clean', 'well-kept'],
    'messy': ['untidy', 'disorganized', 'cluttered', 'chaotic', 'dirty'],
    'brave': ['fearless', 'courageous', 'valiant', 'heroic', 'bold'],
    'cowardly': ['timid', 'fearful', 'spineless', 'faint-hearted', 'gutless'],
    'open': ['unlocked', 'accessible', 'available', 'exposed', 'unsealed'],
    'closed': ['shut', 'sealed', 'locked', 'secure', 'barred'],
    'rare': ['uncommon', 'infrequent', 'unusual', 'exceptional', 'unique'],
    'common': ['frequent', 'usual', 'ordinary', 'regular', 'routine'],
    'modern': ['contemporary', 'current', 'up-to-date', 'recent', 'new'],
    'ancient': ['old', 'historic', 'antique', 'archaic', 'primitive'],
    'honest': ['truthful', 'sincere', 'genuine', 'trustworthy', 'upright'],
    'deceitful': ['dishonest', 'lying', 'untruthful', 'fraudulent', 'insincere'],
    'loyal': ['faithful', 'devoted', 'true', 'reliable', 'dependable'],
    'disloyal': ['unfaithful', 'betraying', 'untrustworthy', 'fickle', 'treacherous'],
    'clever': ['smart', 'intelligent', 'witty', 'resourceful', 'ingenious'],
    'silly': ['foolish', 'ridiculous', 'absurd', 'goofy', 'nonsensical'],
    'valuable': ['precious', 'priceless', 'costly', 'important', 'worthy'],
    'worthless': ['valueless', 'useless', 'trivial', 'insignificant', 'cheap']
}

def get_synonyms(word, pos):
    """Get synonyms for a word based on its part of speech"""
    word = word.lower()
    synonyms = set()
    
    # First check our custom dictionary
    if word in COMMON_SYNONYMS:
        synonyms.update(COMMON_SYNONYMS[word])
        logger.info(f"Found custom synonyms for '{word}': {COMMON_SYNONYMS[word]}")
    
    # Map NLTK POS tags to WordNet POS tags
    pos_map = {
        'JJ': wordnet.ADJ,
        'JJR': wordnet.ADJ,
        'JJS': wordnet.ADJ,
        'RB': wordnet.ADV,
        'RBR': wordnet.ADV,
        'RBS': wordnet.ADV,
        'NN': wordnet.NOUN,
        'NNS': wordnet.NOUN,
        'VB': wordnet.VERB,
        'VBD': wordnet.VERB,
        'VBG': wordnet.VERB,
        'VBN': wordnet.VERB,
        'VBP': wordnet.VERB,
        'VBZ': wordnet.VERB,
    }
    
    # First try getting synonyms with POS
    wn_pos = pos_map.get(pos, None)
    try:
        if wn_pos:
            synsets = wordnet.synsets(word, pos=wn_pos)
        else:
            synsets = wordnet.synsets(word)

        # If no synsets found, fallback to general synsets
        if not synsets:
            synsets = wordnet.synsets(word)

        for syn in synsets:
            for lemma in syn.lemmas():
                synonym = lemma.name().replace('_', ' ')
                if synonym.lower() != word:
                    synonyms.add(synonym)

        logger.info(f"Found WordNet synonyms for '{word}': {list(synonyms)}")
    except Exception as e:
        logger.error(f"Error getting WordNet synonyms for '{word}': {str(e)}")
    
    # Limit to 5 synonyms
    return list(synonyms)[:5]

def correct_punctuation(text):
    """Correct common punctuation mistakes"""
    # Ensure there's a space after commas, periods, exclamation marks, question marks if missing
    text = re.sub(r'([,.!?])([^\s])', r'\1 \2', text)  # Add space after punctuation if missing

    # Remove multiple spaces between words
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space

    # Remove leading or trailing spaces
    text = text.strip()

    # Remove spaces before punctuation (e.g., "Hello , world" -> "Hello, world")
    text = re.sub(r'\s([,.!?])', r'\1', text)  # Remove spaces before punctuation

    # Handle case where multiple punctuation marks occur together (e.g., "Hello!!" -> "Hello!!")
    text = re.sub(r'([.!?])\1+', r'\1', text)  # Replace repeated punctuation marks with one

    logger.info(f"After punctuation correction: {text}")
    return text

# Create SymSpell object
sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)

# Load dictionary
dictionary_path = "frequency_dictionary_en_82_765.txt"
term_index = 0  # column of word
count_index = 1  # column of frequency
sym_spell.load_dictionary(dictionary_path, term_index, count_index)
english_vocab = set(words.words())

def multiple_spelling_suggestions(word, max_suggestions=5):
    suggestions = sym_spell.lookup(word, Verbosity.ALL, max_edit_distance=2)
    unique_terms = list(dict.fromkeys(s.term for s in suggestions))
    clean_terms = [term for term in unique_terms if term in english_vocab]
    return clean_terms[:max_suggestions] if clean_terms else [word]

def correct_spelling_word(word):
    suggestions = sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=2)
    return suggestions[0].term if suggestions else word
def analyze_text(text, current_user=None):
    """Analyze text for spelling, grammar, punctuation, and synonyms"""

    # 1. Get user-defined custom words from database
    user_custom_words = set()
    if current_user:
        custom_words = custom_dictionary.query.filter_by(userName=current_user).all()
        user_custom_words = {entry.word.lower() for entry in custom_words}

    # 2. Tokenize and correct spelling
    tokens = word_tokenize(text)
    corrected_tokens = [correct_spelling_word(preserve_contractions(word)) for word in tokens]
    #corrected_tokens = [correct_spelling_word(word) for word in tokens]
    spelling_corrected_text = ' '.join(corrected_tokens)

    logger.info(f"After spelling correction: {spelling_corrected_text}")

    # 3. Collect spelling suggestions
    spelling_suggestions = []
    for i, word in enumerate(tokens):
        word_lower = word.lower()
        if word_lower in user_custom_words:
            continue  # Skip custom dictionary words

        if word_lower not in word_list and word.isalpha():
            suggestions = multiple_spelling_suggestions(word)
            if suggestions:
                spelling_suggestions.append((word, suggestions))
                logger.info(f"Spelling suggestions for '{word}': {suggestions}")

    # 4. Grammar correction
    corrected_text, grammar_mistakes = correct_grammar(spelling_corrected_text)

    # 5. Punctuation correction
    punctuation_corrected_text = correct_punctuation(corrected_text)

    # 6. Tokenize & POS tag
    tokens = word_tokenize(punctuation_corrected_text)
    tagged = pos_tag(tokens)

    logger.info(f"Tagged words (after punctuation correction): {tagged}")

    # 7. Synonym Extraction
    EXCLUDE_WORDS = set([...])  # your list of excluded words (same as before)

    synonyms = []
    for word, pos in tagged:
        word_lower = word.lower()

        if word_lower in EXCLUDE_WORDS or word_lower in user_custom_words:
            continue  # Skip excluded and custom words

        if pos.startswith(('JJ', 'RB', 'NN', 'VB')) or word_lower in COMMON_SYNONYMS:
            word_synonyms = get_synonyms(word_lower, pos)
            if word_synonyms:
                pos_name = {
                    'JJ': 'adjective', 'JJR': 'comparative adjective', 'JJS': 'superlative adjective',
                    'RB': 'adverb', 'RBR': 'comparative adverb', 'RBS': 'superlative adverb',
                    'NN': 'noun', 'NNS': 'plural noun',
                    'VB': 'verb (base form)', 'VBD': 'verb (past tense)',
                }.get(pos, pos)
                synonyms.append((word, pos_name, word_synonyms))
                logger.info(f"Found synonyms for '{word}' ({pos_name}): {word_synonyms}")

    # 8. Stats
    stats = {
        'words': len(tokens),
        'grammar_mistakes': len(grammar_mistakes),
        'synonyms': len(synonyms)
    }

    logger.info(f"Analysis results: {stats}")

    return punctuation_corrected_text, grammar_mistakes, synonyms, spelling_suggestions, stats


def get_context(word, content):
    word_index = content.find(word)
    if word_index == -1:
        return ''
    
    start_index = max(0, word_index - 50)
    context = content[start_index:word_index]
    
    context_words = context.split()
    return ' '.join(context_words[-3:])

def preserve_contractions(word):
    contractions = {
        "im": "I'm",
        "ive": "I've",
        "id": "I'd",
        "ill": "I'll",
        "dont": "don't",
        "doesnt": "doesn't",
        "didnt": "didn't",
        "cant": "can't",
        "couldnt": "couldn't",
        "shouldnt": "shouldn't",
        "wouldnt": "wouldn't",
        "wont": "won't",
        "wasnt": "wasn't",
        "werent": "weren't",
        "arent": "aren't",
        "isnt": "isn't",
        "havent": "haven't",
        "hasnt": "hasn't",
        "hadnt": "hadn't",
        "lets": "let's",
        "whos": "who's",
        "whats": "what's",
        "heres": "here's",
        "theres": "there's",
        "itll": "it'll",
        "youre": "you're",
        "theyre": "they're",
        "weve": "we've",
        "youve": "you've",
        "theyve": "they've",
        "wholl": "who'll",
        "shes": "she's",
        "hes": "he's",
        "thats": "that's",
        "aint": "ain't"
    }
    return contractions.get(word.lower(), word)

import re

def process_contextual_corrections(text, trigram_model):
    tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
    corrected_words = []
    context_window = []
    corrections = []

    for i, token in enumerate(tokens):
        lower_token = token.lower()

        # Add to context window
        if re.match(r"\w+", token):
            context_window.append(lower_token)
            if len(context_window) > 5:
                context_window.pop(0)

        # Check contextual accuracy if enough context
        if len(context_window) >= 3:
            context = ' '.join(context_window[:-1])
            probability = trigram_model.get_probability(context, lower_token)

            if probability < 0.01 and probability != 0:
                suggestions = trigram_model.get_next_word_candidates(context, top_n=5)
                
                if suggestions and suggestions[0] != lower_token:
                    # Capitalize suggestion if original token was capitalized
                    corrected = suggestions[0]
                    if token[0].isupper():
                        corrected = corrected.capitalize()

                    corrected_words.append(corrected)
                    corrections.append({
                        'original': token,
                        'suggestions': suggestions,
                        'position': i,
                        'type': 'contextual'
                    })
                    continue  # skip adding the original token
        corrected_words.append(token)

    corrected_text = ''.join([
        word if re.match(r"[^\w\s]", word) else f" {word}"
        for word in corrected_words
    ]).strip()

    return {
        
        'corrected_text': corrected_text,
        'contextual_corrections': corrections
    }


@app.route('/guest', methods=['POST'])
def guest_access():
    session['isGuest'] = 'T'
    flash("You're using the spell checker as a guest.")
    return redirect(url_for('to_home'))
   # return redirect(url_for('spell_checker'))



@app.route('/admin')
def admin():
    user_count = profile.query.count()
    users = profile.query.with_entities(profile.userName, profile.email).all()

    return render_template('admin.html', user_count=user_count, users=users)
# In-memory user store (use a database in production)
users = {'admin':123,
         'khadija' :1234,
         'zoya':1234,
         'hisaan':1234
         }


# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email=request.form['email']
        if profile.query.filter((profile.userName == username) | (profile.email == email)).first():
           flash("Oops!Username or email already exists.")
           return redirect(url_for('signup'))
        else:
            newUser = profile(userName = username, password = password, email = email)
            db.session.add(newUser)
            db.session.commit()
            session['username'] = username
            session['isGuest'] = 'F'
            return redirect(url_for('to_home'))
        #return redirect(url_for('spell_checker'))

    letters = []
    for i in range(50):
        letters.append({
            'char': random.choice(string.ascii_uppercase),
            'left': random.randint(0, 100),
            'size': round(random.uniform(1.2, 2.2), 2),
            'delay': round(i * 0.1, 2)
        })

    return render_template('signup.html',letters=letters)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
         # Admin login check (before DB)
        if username == 'admin' and password == '123':  # password should be str, not int
            session['admin_logged_in'] = True
            flash('Welcome Admin!')
            return redirect(url_for('admin'))

        user = profile.query.filter_by(userName=username).first()

        # Check if user exists and password is correct
        if username not in users:
            flash('Username not found. Please sign up first.')
            return redirect(url_for('signup'))

        if users[username] != password:
            flash('Incorrect password. Please try again.')
            return redirect(url_for('login'))
        
       
        else :
            flash('Login successful!')
            session['username'] = username
            session['isGuest'] = 'F'
            return redirect(url_for('to_home'))
            #return redirect(url_for('spell_checker'))
        
    letters = []
    for i in range(50):
        letters.append({
            'char': random.choice(string.ascii_uppercase),
            'left': random.randint(0, 100),
            'size': round(random.uniform(1.2, 2.2), 2),
            'delay': round(i * 0.1, 2)
        })

    return render_template('login.html', letters=letters)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))


# Define a route for the root URL ('/') that renders an HTML template
@app.route('/')
def index():
    return  redirect(url_for('login'))




@app.route('/spellchecker')
def spell_checker():
    return render_template('index.html', corrected_text='', session=session)

@app.route('/spell', methods=['POST'])
def spell_check():
    text = request.form['text']
    username = session.get('username') 
    action = request.form.get('action', 'check')  # "check", "grammar", or "synonyms"
    
    corrected_text = ""
    grammar_mistakes = []
    synonyms = []
    stats = {}
    contextual_errors = []

    if action == 'check':
        corrected_text, grammar_mistakes, synonyms,spelling_suggestions, stats = analyze_text(text,current_user=username)
      #  corrected_text, grammar_mistakes, synonyms, stats = analyze_text(text)
    elif action == 'grammar':
        corrected_text, grammar_mistakes, _, _ ,stats= analyze_text(text,current_user=username)
    elif action == 'synonyms':
        corrected_text, _, synonyms,spelling_suggestions,stats  = analyze_text(text,current_user=username)

    corrected_text, grammar_mistakes, synonyms,spelling_suggestions, stats = analyze_text(text,current_user=username)
    return render_template('index.html', 
                           corrected_text=corrected_text,
                           grammar_mistakes=grammar_mistakes,
                           synonyms=synonyms,
                           spelling_suggestions=spelling_suggestions,
                           stats=stats,
                           contextual_errors=contextual_errors,
                           action=action)




# Add or Remove words from custom dictionary
@app.route('/editCustomDictionary', methods=['GET', 'POST'])
def editCustomDictionary():
    if session['isGuest'] == 'F':
        userName = session.get('username')
        if request.method == 'POST':
            word = request.form['customWord']
            if word:
                if request.form['submit'] == 'Add Word':
                        newWord = custom_dictionary(userName=userName, word=word)
                        db.session.add(newWord)
                        db.session.commit()
                elif request.form['submit'] == 'Delete Word':
                    deletedWord = custom_dictionary.query.filter_by(userName=userName, word=word).first()
                    if not deletedWord:
                        flash('This word does not exist in your dictionary!')
                    else:
                        db.session.delete(deletedWord)
                        db.session.commit()
        return redirect(url_for('to_customDictionary'))
    else:
        return redirect(url_for('to_guest_customDictionary'))
    
# Change email
@app.route('/changeEmail', methods=['GET', 'POST'])
def changeEmail():
    userName = session.get('username')
    email =request.form.get('mail')
    if request.method == 'POST':
        entry = profile.query.filter_by(userName=userName).first()
        if entry:
            entry.email = email
            db.session.commit()
        else:
            flash("Oops! Something went wrong.")
    return redirect(url_for('to_settings'))

# Change password
@app.route('/changePassword', methods=['GET', 'POST'])
def changePassword():
    userName = session.get('username')
    old_pwd = request.form.get('oldPassword')
    new_pwd = request.form.get('newPassword')
    confirm_pwd = request.form.get('confirmPassword')
    if request.method == 'POST':
        entry = profile.query.filter_by(userName=userName).first()
        if entry:
            if entry.password == old_pwd and new_pwd == confirm_pwd:
                entry.password = new_pwd
                db.session.commit()
            else:
                flash('Error! Incorrect old password or passwords do not match.')
        else:
            flash("Oops! Something went wrong.")
    return redirect(url_for('to_settings'))



# Load home.html
@app.route('/to_home', methods=['GET', 'POST'])
def to_home():
    return render_template('home.html')




# Load customDictionary.html/guest_customDictionary.html
@app.route('/to_customDictionary', methods=['GET', 'POST'])
def to_customDictionary():
    if session['isGuest'] == 'T':
       return render_template('guest_customDictionary.html')
    userName = session.get('username')
    words = custom_dictionary.query.filter_by(userName=userName).all()
    return render_template('customDictionary.html', wordList=[w.word for w in words])

# Load settings.html/guest_settings.html
@app.route('/to_settings', methods=['GET', 'POST'])
def to_settings():
   return render_template('settings.html')


# Run the Flask application if the script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
