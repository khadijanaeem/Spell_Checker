# Import necessary libraries and modules
from flask import Flask, render_template, request,jsonify, redirect, url_for, flash,session
from autocorrect import Speller
from language_tool_python import LanguageToolPublicAPI
import nltk
import random
import string
nltk.data.path.append(r"C:\\Users\\X1 EXTREME\\AppData\\Roaming\\nltk_data")

nltk.download('punkt')

from nltk.tokenize import word_tokenize

from nltk.corpus import wordnet,words
from nltk.tokenize import word_tokenize,sent_tokenize
from nltk.tag import pos_tag
from collections import Counter
import logging
from ngram_model import NGramModel
import re
import secrets
from nltk.metrics import edit_distance
from difflib import get_close_matches
from symspellpy.symspellpy import SymSpell, Verbosity
#import Levenshtein
#from spellchecker import SpellChecker
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('words')

bigramModel = NGramModel(n=2)
trigramModel =  NGramModel(3)

# Sample corpus from the JS version
with open('corpus.txt', 'r') as f:
    corpus_lines = f.readlines()

bigramModel.train(corpus_lines)
trigramModel.train(corpus_lines)


# Create a Flask application instance
app = Flask(__name__)

app.secret_key = '4f3d2f3c4a7e896fbd2d3a1b8e7a9f00'
spell = Speller(lang='en')
#speller1 = SpellChecker()
# Create a LanguageTool object for grammar and spell checking
tool = LanguageToolPublicAPI('en-US')
word_list = words.words()
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
    corrected_text = custom_grammar_correction(corrected_text)
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
    
def analyze_text(text):
    """Analyze text for spelling, grammar, punctuation, and synonyms"""
    
   # First spelling correction
    tokens = word_tokenize(text)
    corrected_tokens = [correct_spelling_word(word) for word in tokens]
    spelling_corrected_text = ' '.join(corrected_tokens)
    
    logger.info(f"After spelling correction: {spelling_corrected_text}")
    spelling_suggestions = []
    for i, word in enumerate(tokens):
        if word.lower() not in word_list and word.isalpha():
            suggestions = multiple_spelling_suggestions(word)
            if suggestions:
                spelling_suggestions.append((word, suggestions))
                logger.info(f"Spelling suggestions for '{word}': {suggestions}")
    
    # Grammar correction
    corrected_text, grammar_mistakes = correct_grammar(spelling_corrected_text)
    
    # Punctuation correction
    punctuation_corrected_text = correct_punctuation(corrected_text)
    
    # Tokenize and tag the corrected text
    tokens = word_tokenize(punctuation_corrected_text)
    tagged = pos_tag(tokens)
    
    logger.info(f"Tagged words (after punctuation correction): {tagged}")
    
    # Excluded words (for synonym extraction)
    EXCLUDE_WORDS = set([  # List of common excluded words like pronouns and auxiliary verbs
        'i', 'you', 'we', 'they', 'he', 'she', 'it', 'are', 'is', 'am', 'was', 'were',
        'be', 'being', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'shall', 'should', 'may', 'might', 'must', 'can', 'could',
        'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
        'me', 'him', 'them', 'us', 'who', 'whom', 'which', 'what', 'where', 'when', 'why', 'how','hello',
        'me','mine','name' ,'be','time','person','year','way','day','thing','man','world','life','hand',
        'part','child', 'eye','government','week', 'lion', 'tiger', 'bear', 'dog', 'cat', 'alligator', 'cricket', 
        'bird', 'wolf', 'mother', 'father', 'baby', 'child', 'toddler', 'teenager', 'grandmother', 'student', 'teacher', 'minister',
           ])
    
    synonyms = []
    for word, pos in tagged:
        word_lower = word.lower()
        
        if word_lower in EXCLUDE_WORDS:
            continue
        
        if pos.startswith(('JJ', 'RB', 'NN', 'VB')) or word_lower in COMMON_SYNONYMS:
            word_synonyms = get_synonyms(word_lower, pos)
            if word_synonyms:
                pos_name = {
                    'JJ': 'adjective',
                    'JJR': 'comparative adjective',
                    'JJS': 'superlative adjective',
                    'RB': 'adverb',
                    'RBR': 'comparative adverb',
                    'RBS': 'superlative adverb',
                    'NN': 'noun',
                    'NNS': 'plural noun',
                    'VB': 'verb (base form)',
                    'VBD': 'verb (past tense)',
                }.get(pos, pos)
                synonyms.append((word, pos_name, word_synonyms))
                logger.info(f"Found synonyms for '{word}' ({pos_name}): {word_synonyms}")
    
    stats = {
        'words': len(tokens),
        'grammar_mistakes': len(grammar_mistakes),
        'synonyms': len(synonyms)
    }
    
    logger.info(f"Analysis results: {stats}")
    
    return punctuation_corrected_text, grammar_mistakes, synonyms,spelling_suggestions,stats


def get_context(word, content):
    word_index = content.find(word)
    if word_index == -1:
        return ''
    
    start_index = max(0, word_index - 50)
    context = content[start_index:word_index]
    
    context_words = context.split()
    return ' '.join(context_words[-3:])


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
    session['username'] = 'Guest'
    flash("You're using the spell checker as a guest.")
    return redirect(url_for('spell_checker'))



# In-memory user store (use a database in production)
users = {}


# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if user already exists
        if username in users:
            flash('Username already exists! Please choose a different one.')
            return redirect(url_for('signup'))

        # Store user credentials
        users[username] = password
        flash('Signup successful! You can now work.')
        return redirect(url_for('spell_checker'))
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

        # Check if user exists and password is correct
        if username not in users:
            flash('Username not found. Please sign up first.')
            return redirect(url_for('signup'))

        if users[username] != password:
            flash('Incorrect password. Please try again.')
            return redirect(url_for('login'))

        flash('Login successful!')
        return redirect(url_for('spell_checker'))
    letters = []
    for i in range(50):
        letters.append({
            'char': random.choice(string.ascii_uppercase),
            'left': random.randint(0, 100),
            'size': round(random.uniform(1.2, 2.2), 2),
            'delay': round(i * 0.1, 2)
        })

    return render_template('login.html', letters=letters)

@app.route('/logout')
def logout():
    session.pop('username', None)
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
    action = request.form.get('action', 'check')  # "check", "grammar", or "synonyms"
    
    corrected_text = ""
    grammar_mistakes = []
    synonyms = []
    stats = {}
    contextual_errors = []
    spelling_suggestions=[]
    if action == 'check':
        corrected_text, grammar_mistakes, synonyms,spelling_suggestions, stats = analyze_text(text)
    elif action == 'grammar':
        corrected_text, grammar_mistakes, _, _ = analyze_text(text)
    elif action == 'synonyms':
        corrected_text, _, synonyms, _ = analyze_text(text)

    return render_template('index.html', 
                           corrected_text=corrected_text,
                           grammar_mistakes=grammar_mistakes,
                           synonyms=synonyms,
                           spelling_suggestions=spelling_suggestions,
                           stats=stats,
                           contextual_errors=contextual_errors,
                           action=action)


# Run the Flask application if the script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
