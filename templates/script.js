document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const editor = document.getElementById('editor');
    const checkSpellingBtn = document.getElementById('checkSpellingBtn');
    const clearBtn = document.getElementById('clearBtn');
    const copyBtn = document.getElementById('copyBtn');
    const wordCountEl = document.getElementById('wordCount');
    const charCountEl = document.getElementById('charCount');
    const spellingResults = document.getElementById('spellingResults');
    const correctionsList = document.getElementById('corrections-list');
    const grammarList = document.getElementById('grammar-list');
    const synonymModal = document.getElementById('synonymModal');
    const synonymWord = document.getElementById('synonymWord');
    const synonymList = document.getElementById('synonymList');
    const closeModal = document.querySelector('.close');

    // Event Listeners
    editor.addEventListener('input', updateWordAndCharCount);
    checkSpellingBtn.addEventListener('click', checkSpelling);
    clearBtn.addEventListener('click', clearEditor);
    copyBtn.addEventListener('click', copyToClipboard);
    closeModal.addEventListener('click', closeModalHandler);
    window.addEventListener('click', (e) => {
        if (e.target === synonymModal) {
            closeModalHandler();
        }
    });

    // Initialize word and char count
    updateWordAndCharCount();

    // Dictionary for basic spell checking (standalone mode)
    const dictionary = new Set([
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
        "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
        "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further",
        "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's",
        "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is",
        "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not",
        "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
        "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's",
        "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
        "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
        "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
        "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll",
        "you're", "you've", "your", "yours", "yourself", "yourselves",
        "hello", "world", "example", "text", "spelling", "grammar", "error", "correction", "website", "application",
        "check", "correct", "suggest", "synonym", "word", "sentence", "paragraph", "document", "edit", "paste", "copy",
        "clear", "highlight", "detection", "language", "processing", "natural", "algorithm", "feature", "interface",
        "user", "responsive", "design", "modern", "simple", "easy", "fast", "efficient", "accurate", "reliable",
        "beautiful", "day",
        "pretty", "gorgeous", "lovely", "attractive", "stunning", "wonderful", "nice", "pleasant",
        "happy", "sad", "angry", "excited", "tired", "sleepy", "energetic", "lazy", "busy",
        "big", "small", "huge", "tiny", "large", "little", "massive", "miniature",
        "good", "bad", "great", "terrible", "awesome", "awful", "excellent", "poor",
        "hot", "cold", "warm", "cool", "freezing", "boiling", "mild", "chilly",
        "new", "old", "ancient", "modern", "fresh", "stale", "recent", "vintage",
        "clean", "dirty", "spotless", "filthy", "tidy", "messy", "neat", "cluttered",
        "bright", "dark", "dim", "shiny", "dull", "brilliant", "gloomy", "radiant",
        "quiet", "loud", "noisy", "silent", "peaceful", "chaotic", "calm", "rowdy",
        "rich", "poor", "wealthy", "expensive", "cheap", "valuable", "worthless", "priceless",
        "smart", "clever", "intelligent", "wise", "brilliant", "dumb", "stupid", "foolish",
        "strong", "weak", "powerful", "feeble", "mighty", "fragile", "sturdy", "delicate",
        "fast", "slow", "quick", "rapid", "swift", "sluggish", "speedy", "leisurely",
        "hard", "soft", "firm", "gentle", "rough", "smooth", "tender", "harsh",
        "young", "old", "youthful", "aged", "mature", "juvenile", "elderly", "ancient",
        "tall", "short", "high", "low", "towering", "tiny", "gigantic", "microscopic",
        "wide", "narrow", "broad", "slim", "thick", "thin", "slender", "fat",
        "deep", "shallow", "profound", "superficial", "thorough", "basic", "complex", "simple",
        "dry", "wet", "moist", "arid", "damp", "soaked", "parched", "dripping",
        "sweet", "sour", "bitter", "spicy", "tasty", "bland", "delicious", "disgusting", "run",
         "walk", "jump", "swim", "fly", "sit", "stand", "talk", "listen", "eat", "drink", "write",
          "read", "sleep", "think", "know", "understand", "learn", "teach", "build", "create", "break", 
          "fix", "drive", "ride","home", "school", "college", "university", "office", "park", "market", 
          "store", "mall", "cinema", "beach", "mountain", "desert", "forest", "village", "city", "country", 
          "continent","man", "woman", "child", "teacher", "student", "doctor", "engineer", "developer", 
          "designer", "writer", "singer", "actor", "friend", "enemy", "boss", "employee","man", "woman", 
          "child", "teacher", "student", "doctor", "engineer", "developer", "designer", "writer", "singer", 
          "actor", "friend", "enemy", "boss", "employee","today", "tomorrow", "yesterday", "morning",
           "afternoon", "evening", "night", "day", "week", "month", "year", "minute", "hour", "second", 
           "decade", "century","love", "hate", "joy", "fear", "anger", "peace", "hope", "despair", 
           "confidence", "nervous", "bored", "excited", "anxious", "calm", "grateful", "jealous",
           "apple", "banana", "orange", "grape", "mango", "bread", "rice", "pizza", "burger",
            "coffee", "tea", "water", "milk", "juice", "cake", "chocolate","book", "pen", "phone",
             "laptop", "car", "bike", "chair", "table", "window", "door", "key", "bottle", "bag", 
             "watch", "glasses", "camera"

    ]);

    // Common misspellings and their corrections
    const commonMisspellings = {
        "teh": "the",
        "recieve": "receive",
        "wierd": "weird",
        "accomodate": "accommodate",
        "occurence": "occurrence",
        "definately": "definitely",
        "seperate": "separate",
        "suprise": "surprise",
        "thier": "their",
        "alot": "a lot",
        "cant": "can't",
        "dont": "don't",
        "isnt": "isn't",
        "wouldnt": "wouldn't",
        "couldnt": "couldn't",
        "shouldnt": "shouldn't",
        "wont": "won't",
        "havent": "haven't",
        "arent": "aren't",
        "wasnt": "wasn't",
        "didnt": "didn't",
        "doesnt": "doesn't",
        "adress": "address",
        "agressive": "aggressive",
        "arguement": "argument",
        "basicly": "basically",
        "begining": "beginning",
        "beleive": "believe",
        "buisness": "business",
        "calender": "calendar",
        "comming": "coming",
        "concious": "conscious",
        "consistant": "consistent",
        "decieve": "deceive",
        "embarass": "embarrass",
        "enviroment": "environment",
        "existance": "existence",
        "excersize": "exercise",
        "facinating": "fascinating",
        "finaly": "finally",
        "foriegn": "foreign",
        "freind": "friend",
        "garantee": "guarantee",
        "goverment": "government",
        "gratefull": "grateful",
        "happend": "happened",
        "harrass": "harass",
        "heirarchy": "hierarchy",
        "humourous": "humorous",
        "imediately": "immediately",
        "independant": "independent",
        "inteligent": "intelligent",
        "interupt": "interrupt",
        "jist": "gist",
        "knowlege": "knowledge",
        "labratory": "laboratory",
        "liason": "liaison",
        "lonly": "lonely",
        "maintainance": "maintenance",
        "medeval": "medieval",
        "miniscule": "minuscule",
        "mispell": "misspell",
        "neccessary": "necessary",
        "noticable": "noticeable",
        "ocassion": "occasion",
        "occuring": "occurring",
        "omision": "omission",
        "oppertunity": "opportunity",
        "paralel": "parallel",
        "perseverence": "perseverance",
        "pharoah": "pharaoh",
        "playwrite": "playwright",
        "posession": "possession",
        "preceed": "precede",
        "prefered": "preferred",
        "propoganda": "propaganda",
        "publically": "publicly",
        "questionaire": "questionnaire",
        "realy": "really",
        "refered": "referred",
        "refering": "referring",
        "religous": "religious",
        "remeber": "remember",
        "resistence": "resistance",
        "resturant": "restaurant",
        "rythm": "rhythm",
        "seige": "siege",
        "sence": "sense",
        "sentance": "sentence",
        "seperately": "separately",
        "speach": "speech",
        "strenght": "strength",
        "succesful": "successful",
        "tommorow": "tomorrow",
        "tounge": "tongue",
        "twelth": "twelfth",
        "untill": "until",
        "vacume": "vacuum",
        "vehical": "vehicle",
        "wierdly": "weirdly",
        "wether": "whether",
        "wich": "which",
        "withold": "withhold",
        "yatch": "yacht",
        "yourselfs": "yourselves",
        "accross": "across",
        "affraid": "afraid",
        "beggining": "beginning",
        "catagory": "category",
        "comited": "committed",
        "delimeter": "delimiter",
        "dependant": "dependent",
        "dissapoint": "disappoint",
        "divsion": "division",
        "dominent": "dominant",
        "embarased": "embarrassed"
    };
    

    // Common grammar rules (very simplified)
    const grammarRules = [
        { pattern: /\bi am\b/gi, replacement: "I am" },
        { pattern: /\byour wrong\b/gi, replacement: "you're wrong" },
        { pattern: /\btheir going\b/gi, replacement: "they're going" },
        { pattern: /\bits a\b/gi, replacement: "it's a" },
        { pattern: /\btheir is\b/gi, replacement: "there is" },
        { pattern: /\bthier\b/gi, replacement: "their" },
        { pattern: /\bcould of\b/gi, replacement: "could have" },
        { pattern: /\bshould of\b/gi, replacement: "should have" },
        { pattern: /\bwould of\b/gi, replacement: "would have" },
        { pattern: /\bain't\b/gi, replacement: "is not" },
        { pattern: /\bi aint\b/gi, replacement: "I am not" },
        { pattern: /\bwas you\b/gi, replacement: "were you" },
        { pattern: /\bi seen\b/gi, replacement: "I saw" },
        { pattern: /\bi done\b/gi, replacement: "I did" },
        { pattern: /\bthere house\b/gi, replacement: "their house" },
        { pattern: /\bto many\b/gi, replacement: "too many" },
        { pattern: /\bto much\b/gi, replacement: "too much" },
        { pattern: /\bwould of been\b/gi, replacement: "would have been" },
        { pattern: /\bcould of been\b/gi, replacement: "could have been" },
        { pattern: /\byour welcome\b/gi, replacement: "you're welcome" },
        { pattern: /\bwho's car\b/gi, replacement: "whose car" },
        { pattern: /\bit's color\b/gi, replacement: "its color" },
        { pattern: /\bits going\b/gi, replacement: "it's going" },
        { pattern: /\byour the\b/gi, replacement: "you're the" },
        { pattern: /\bit dont\b/gi, replacement: "it doesn't" },
        { pattern: /\bdidnt\b/gi, replacement: "didn't" },
        { pattern: /\bcant\b/gi, replacement: "can't" },
        { pattern: /\bdoesnt\b/gi, replacement: "doesn't" },
        { pattern: /\bwasnt\b/gi, replacement: "wasn't" },
        { pattern: /\bwerent\b/gi, replacement: "weren't" },
        { pattern: /\bhasnt\b/gi, replacement: "hasn't" },
        { pattern: /\bhadnt\b/gi, replacement: "hadn't" },
        { pattern: /\bwhos\b/gi, replacement: "whose" },
        { pattern: /\bwich\b/gi, replacement: "which" },
        { pattern: /\btheres\b/gi, replacement: "there's" },
        { pattern: /\bheres\b/gi, replacement: "here's" },
        { pattern: /\bwheres\b/gi, replacement: "where's" },
        { pattern: /\bwhens\b/gi, replacement: "when's" },
        { pattern: /\bwhats\b/gi, replacement: "what's" },
        { pattern: /\bhows\b/gi, replacement: "how's" },
        { pattern: /\bitll\b/gi, replacement: "it'll" },
        { pattern: /\bitd\b/gi, replacement: "it'd" },
        { pattern: /\bhe's\b/gi, replacement: "he is" },
        { pattern: /\bshe's\b/gi, replacement: "she is" },
        { pattern: /\bi'm\b/gi, replacement: "I am" },
        { pattern: /\btheyre\b/gi, replacement: "they're" },
        { pattern: /\bwe're\b/gi, replacement: "we are" },
        { pattern: /\bweve\b/gi, replacement: "we've" },
        { pattern: /\bit's\b/gi, replacement: "it's" },
        { pattern: /\btheyve\b/gi, replacement: "they've" },
        { pattern: /\byouve\b/gi, replacement: "you've" },
        { pattern: /\bshouldnt\b/gi, replacement: "shouldn't" },
        { pattern: /\bcouldnt\b/gi, replacement: "couldn't" },
        { pattern: /\bwont\b/gi, replacement: "won't" },
        { pattern: /\barent\b/gi, replacement: "aren't" },
        { pattern: /\bshes\b/gi, replacement: "she's" },
        { pattern: /\bhes\b/gi, replacement: "he's" },
        { pattern: /\bit was me\b/gi, replacement: "it was I" },
        { pattern: /\bi feel good\b/gi, replacement: "I feel well" },
        { pattern: /\bbetween you and i\b/gi, replacement: "between you and me" },
        { pattern: /\bin regards to\b/gi, replacement: "in regard to" },
        { pattern: /\batleast\b/gi, replacement: "at least" },
        { pattern: /\ba lot\b/gi, replacement: "a lot" },
        { pattern: /\bnoone\b/gi, replacement: "no one" },
        { pattern: /\bmore better\b/gi, replacement: "better" },
        { pattern: /\bmore worse\b/gi, replacement: "worse" },
        { pattern: /\bmost best\b/gi, replacement: "best" },
        { pattern: /\bmost worst\b/gi, replacement: "worst" },
        { pattern: /\bmost unique\b/gi, replacement: "unique" },
        { pattern: /\bmost perfect\b/gi, replacement: "perfect" },
        { pattern: /\beach other\b/gi, replacement: "each other" },
        { pattern: /\bone and the same\b/gi, replacement: "one and the same thing" },
        { pattern: /\bcould care less\b/gi, replacement: "couldn't care less" },
        { pattern: /\ball of the sudden\b/gi, replacement: "all of a sudden" },
        { pattern: /\byour not\b/gi, replacement: "you're not" },
        { pattern: /\bless people\b/gi, replacement: "fewer people" },
        { pattern: /\bless items\b/gi, replacement: "fewer items" },
        { pattern: /\bamount of people\b/gi, replacement: "number of people" },
        { pattern: /\bamount of items\b/gi, replacement: "number of items" },
        { pattern: /\bnone are\b/gi, replacement: "none is" },
        { pattern: /\bi could care less\b/gi, replacement: "I couldn't care less" },
        { pattern: /\bclose proximity\b/gi, replacement: "proximity" },
        { pattern: /\bactual fact\b/gi, replacement: "fact" },
        { pattern: /\badvance notice\b/gi, replacement: "notice" },
        { pattern: /\bbasic fundamentals\b/gi, replacement: "fundamentals" },
        { pattern: /\bfree gift\b/gi, replacement: "gift" },
        { pattern: /\brevert back\b/gi, replacement: "revert" },
        { pattern: /\bexact same\b/gi, replacement: "same" },
        { pattern: /\bvery unique\b/gi, replacement: "unique" },
        { pattern: /\babsolutely essential\b/gi, replacement: "essential" },
        { pattern: /\bmyself and John\b/gi, replacement: "John and I" },
        { pattern: /\bme and John\b/gi, replacement: "John and I" },
        { pattern: /\bhim and I\b/gi, replacement: "he and I" },
        { pattern: /\bher and I\b/gi, replacement: "she and I" },
        { pattern: /\bme and her\b/gi, replacement: "she and I" },
        { pattern: /\bhe dont\b/gi, replacement: "he doesn't" },
        { pattern: /\bshe dont\b/gi, replacement: "she doesn't" },
        { pattern: /\byou was\b/gi, replacement: "you were" },
        { pattern: /\bainy\b/gi, replacement: "ain't" },
        
    { pattern: /\btheir not\b/gi, replacement: "they're not" },
    { pattern: /\byou is\b/gi, replacement: "you are" },
    { pattern: /\bhe are\b/gi, replacement: "he is" },
    { pattern: /\bshe are\b/gi, replacement: "she is" },
    { pattern: /\bit are\b/gi, replacement: "it is" },
    { pattern: /\bthem is\b/gi, replacement: "they are" },
    { pattern: /\bthey was\b/gi, replacement: "they were" },
    { pattern: /\bwe was\b/gi, replacement: "we were" },
    { pattern: /\bwe is\b/gi, replacement: "we are" },
    { pattern: /\bis they\b/gi, replacement: "are they" },
    { pattern: /\bis we\b/gi, replacement: "are we" },
    { pattern: /\bis you\b/gi, replacement: "are you" },
    { pattern: /\bdo not has\b/gi, replacement: "does not have" },
    { pattern: /\bhe do\b/gi, replacement: "he does" },
    { pattern: /\bshe do\b/gi, replacement: "she does" },
    { pattern: /\bit do\b/gi, replacement: "it does" },
    { pattern: /\bthey does\b/gi, replacement: "they do" },
    { pattern: /\bwe does\b/gi, replacement: "we do" },
    { pattern: /\byou does\b/gi, replacement: "you do" },
    { pattern: /\bme is\b/gi, replacement: "I am" },
    { pattern: /\bgone missing\b/gi, replacement: "gone" },
    { pattern: /\breturn back\b/gi, replacement: "return" },
    { pattern: /\bin my opinion i think\b/gi, replacement: "I think" },
    { pattern: /\bas per my opinion\b/gi, replacement: "in my opinion" },
    { pattern: /\btwo twins\b/gi, replacement: "twins" },
    { pattern: /\bfalse pretense\b/gi, replacement: "pretense" },
    { pattern: /\bfinal conclusion\b/gi, replacement: "conclusion" },
    { pattern: /\bfree gift\b/gi, replacement: "gift" },
    { pattern: /\bnew innovation\b/gi, replacement: "innovation" },
    { pattern: /\bI have went\b/gi, replacement: "I have gone" },
    { pattern: /\bhe have\b/gi, replacement: "he has" },
    { pattern: /\bshe have\b/gi, replacement: "she has" },
    { pattern: /\bit have\b/gi, replacement: "it has" },
    { pattern: /\bhas went\b/gi, replacement: "has gone" },
    { pattern: /\bhave ate\b/gi, replacement: "have eaten" },
    { pattern: /\bi seen\b/gi, replacement: "I saw" },
    { pattern: /\byou was\b/gi, replacement: "you were" },
    { pattern: /\bif i was\b/gi, replacement: "if I were" },
    { pattern: /\bif he was\b/gi, replacement: "if he were" },
    { pattern: /\bif she was\b/gi, replacement: "if she were" },
    { pattern: /\bif it was\b/gi, replacement: "if it were" },
    { pattern: /\bamount of people\b/gi, replacement: "number of people" },
    { pattern: /\bamount of books\b/gi, replacement: "number of books" },
    { pattern: /\bi wish i was\b/gi, replacement: "I wish I were" },
    { pattern: /\bhis self\b/gi, replacement: "himself" },
    { pattern: /\bher self\b/gi, replacement: "herself" },
    { pattern: /\bmy self\b/gi, replacement: "myself" },
    { pattern: /\btheir selfs\b/gi, replacement: "themselves" },
    { pattern: /\beach of them are\b/gi, replacement: "each of them is" },
    { pattern: /\bnone of them are\b/gi, replacement: "none of them is" },
    { pattern: /\bi didn't knew\b/gi, replacement: "I didn't know" },
    { pattern: /\bhe didn't went\b/gi, replacement: "he didn't go" },
    { pattern: /\bshe didn't seen\b/gi, replacement: "she didn't see" },
    { pattern: /\bit didn't ate\b/gi, replacement: "it didn't eat" },
    { pattern: /\bwould had\b/gi, replacement: "would have" },
    { pattern: /\bshould had\b/gi, replacement: "should have" },
    { pattern: /\bcould had\b/gi, replacement: "could have" },
    { pattern: /\bhad went\b/gi, replacement: "had gone" },
    { pattern: /\bhas drank\b/gi, replacement: "has drunk" },
    { pattern: /\bhave drank\b/gi, replacement: "have drunk" },
    { pattern: /\bhas began\b/gi, replacement: "has begun" },
    { pattern: /\bhave began\b/gi, replacement: "have begun" },
    { pattern: /\bi use to\b/gi, replacement: "I used to" },
    { pattern: /\bused too\b/gi, replacement: "used to" },
    { pattern: /\bcould use to\b/gi, replacement: "could get used to" },
    { pattern: /\bi rather\b/gi, replacement: "I'd rather" },
    { pattern: /\bi'd of\b/gi, replacement: "I'd have" },
    { pattern: /\bi had of\b/gi, replacement: "I had" },
    { pattern: /\bit had of\b/gi, replacement: "it had" },
    { pattern: /\bthese ones\b/gi, replacement: "these" },
    { pattern: /\bthose ones\b/gi, replacement: "those" },
    { pattern: /\bthis here\b/gi, replacement: "this" },
    { pattern: /\bthat there\b/gi, replacement: "that" },
    { pattern: /\btry and\b/gi, replacement: "try to" },
    { pattern: /\bwait on\b/gi, replacement: "wait for" },
    { pattern: /\boff of\b/gi, replacement: "off" },
    { pattern: /\bin to\b/gi, replacement: "into" },
    { pattern: /\banyways\b/gi, replacement: "anyway" },
    { pattern: /\banywho\b/gi, replacement: "anyhow" },
    { pattern: /\bfunner\b/gi, replacement: "more fun" },
    { pattern: /\bmore prettier\b/gi, replacement: "prettier" },
    { pattern: /\bmore faster\b/gi, replacement: "faster" },
    { pattern: /\bmore slower\b/gi, replacement: "slower" },
    { pattern: /\bmost smartest\b/gi, replacement: "smartest" },
    { pattern: /\bmost fastest\b/gi, replacement: "fastest" },
    { pattern: /\bmost simplest\b/gi, replacement: "simplest" },
    { pattern: /\bmost cheapest\b/gi, replacement: "cheapest" },
    { pattern: /\beveryone have\b/gi, replacement: "everyone has" },
    { pattern: /\bsomebody have\b/gi, replacement: "somebody has" },
    { pattern: /\banybody have\b/gi, replacement: "anybody has" },
    { pattern: /\bnobody have\b/gi, replacement: "nobody has" },
    { pattern: /\beverybody have\b/gi, replacement: "everybody has" },
    { pattern: /\bnothing are\b/gi, replacement: "nothing is" },
    { pattern: /\bsomething are\b/gi, replacement: "something is" },
    { pattern: /\banything are\b/gi, replacement: "anything is" }
    ];
    

    // Levenshtein Distance Implementation
    function levenshteinDistance(a, b) {
        // Create a matrix of size (a.length+1) x (b.length+1)
        const matrix = Array(b.length + 1).fill().map(() => Array(a.length + 1).fill(0));
        
        // Initialize the first row and column
        for (let i = 0; i <= a.length; i++) matrix[0][i] = i;
        for (let j = 0; j <= b.length; j++) matrix[j][0] = j;
        
        // Fill the matrix using dynamic programming
        for (let j = 1; j <= b.length; j++) {
            for (let i = 1; i <= a.length; i++) {
                // If the characters match, no operation is needed
                const substitutionCost = a[i - 1] === b[j - 1] ? 0 : 1;
                
                // Calculate the minimum cost of operations (deletion, insertion, substitution)
                matrix[j][i] = Math.min(
                    matrix[j][i - 1] + 1, // deletion
                    matrix[j - 1][i] + 1, // insertion
                    matrix[j - 1][i - 1] + substitutionCost // substitution
                );
                
                // Consider transposition (for adjacent characters swapped)
                if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) {
                    matrix[j][i] = Math.min(matrix[j][i], matrix[j - 2][i - 2] + 1);
                }
            }
        }
        
        // Return the minimum edit distance
        return matrix[b.length][a.length];
    }
    
    // Find closest words using Levenshtein distance
    function findSimilarWords(word, wordList, maxDistance = 2, maxResults = 5) {
        const results = [];
        
        for (const candidate of wordList) {
            // Skip if the candidate is the same as the word
            if (candidate === word) continue;
            
            // Calculate the edit distance
            const distance = levenshteinDistance(word.toLowerCase(), candidate.toLowerCase());
            
            // Include if within maxDistance
            if (distance <= maxDistance) {
                results.push({
                    word: candidate,
                    distance: distance
                });
            }
        }
        
        // Sort by distance (ascending) and return the top maxResults
        return results
            .sort((a, b) => a.distance - b.distance)
            .slice(0, maxResults)
            .map(result => result.word);
    }

    // N-gram Model Implementation
    class NGramModel {
        constructor(n = 2) {
            this.n = n; // n-gram size (default: bigram)
            this.nGrams = {}; // storage for n-grams
            this.wordFreq = {}; // word frequencies
            this.totalWords = 0; // total word count for probability calculations
        }
        
        // Convert text into tokens
        tokenize(text) {
            // Clean the text and split into words
            return text.toLowerCase()
                .replace(/[^\w\s']|_/g, " ")
                .replace(/\s+/g, " ")
                .trim()
                .split(/\s+/);
        }
        
        // Train the model on a corpus
        train(corpus) {
            // Process each text segment in the corpus
            for (const text of corpus) {
                const tokens = this.tokenize(text);
                
                // Update word frequencies
                for (const token of tokens) {
                    this.wordFreq[token] = (this.wordFreq[token] || 0) + 1;
                    this.totalWords++;
                }
                
                // Create n-grams
                for (let i = 0; i <= tokens.length - this.n; i++) {
                    // Get the context (n-1 words) and the target word
                    const context = tokens.slice(i, i + this.n - 1).join(" ");
                    const target = tokens[i + this.n - 1];
                    
                    // Initialize if needed
                    if (!this.nGrams[context]) {
                        this.nGrams[context] = {};
                    }
                    
                    // Update target count for this context
                    this.nGrams[context][target] = (this.nGrams[context][target] || 0) + 1;
                }
            }
        }
        
        // Get probability of a word given a context
        getProbability(context, word) {
            const contextWords = context.toLowerCase().split(/\s+/).slice(-this.n + 1).join(" ");
            
            // If context not in model, return word frequency probability
            if (!this.nGrams[contextWords]) {
                return (this.wordFreq[word] || 0) / this.totalWords;
            }
            
            // Calculate context total
            const contextTotal = Object.values(this.nGrams[contextWords])
                .reduce((sum, count) => sum + count, 0);
            
            // Return probability
            return (this.nGrams[contextWords][word] || 0) / contextTotal;
        }
        
        // Get most likely words to follow a context
        getNextWordCandidates(context, count = 5) {
            const contextWords = context.toLowerCase().split(/\s+/).slice(-this.n + 1).join(" ");
            
            // If context not in model, return most frequent words
            if (!this.nGrams[contextWords]) {
                return Object.entries(this.wordFreq)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, count)
                    .map(entry => entry[0]);
            }
            
            // Get words and their counts for this context
            return Object.entries(this.nGrams[contextWords])
                .sort((a, b) => b[1] - a[1])
                .slice(0, count)
                .map(entry => entry[0]);
        }
        
        // Detect contextual errors based on probability
        detectContextualErrors(text, thresholdProbability = 0.01) {
            const tokens = this.tokenize(text);
            const errors = [];
            
            // Need at least n tokens to check context
            if (tokens.length < this.n) return errors;
            
            // Check each word with its context
            for (let i = this.n - 1; i < tokens.length; i++) {
                const context = tokens.slice(i - (this.n - 1), i).join(" ");
                const word = tokens[i];
                
                // Skip if word is not in vocabulary
                if (!this.wordFreq[word]) continue;
                
                const probability = this.getProbability(context, word);
                
                // If probability is very low, it might be contextually wrong
                if (probability < thresholdProbability) {
                    const suggestions = this.getNextWordCandidates(context);
                    
                    errors.push({
                        word: word,
                        position: i,
                        context: context,
                        suggestions: suggestions
                    });
                }
            }
            
            return errors;
        }
    }
    
    // Sample corpus for training n-gram model
    const sampleCorpus = [
        "The quick brown fox jumps over the lazy dog",
        "I am going to the store to buy some groceries",
        "The weather is nice today but it might rain tomorrow",
        "She sells seashells by the seashore",
        "To be or not to be that is the question",
        "All that glitters is not gold",
        "The early bird catches the worm",
        "A picture is worth a thousand words",
        "Actions speak louder than words",
        "You can't judge a book by its cover",
        "Don't count your chickens before they hatch",
        "The pen is mightier than the sword",
        "When in Rome do as the Romans do",
        "Fortune favors the bold",
        "Time flies like an arrow fruit flies like a banana",
        "I have been to London many times but I have never seen the queen",
        "The cat sat on the mat and watched the mouse",
        "We should go to the beach when the weather is nice",
        "Please turn off the lights before you leave the room",
        "I would like to have a cup of coffee with some sugar and milk",
        "He is reading a book about the history of ancient civilizations",
        "They are planning to visit Paris next summer",
        "She has been studying French for three years",
        "My brother plays the guitar in a rock band",
        "We need to buy some bread milk and eggs from the supermarket",
        "The children are playing in the garden",
        "This restaurant serves the best pizza in town",
        "I usually wake up at seven o'clock in the morning",
        "She always wears elegant clothes to work",
        "He drives a blue car that he bought last year",
        "We should finish this project by the end of the week",
        "They live in a beautiful house near the lake",
        "The movie was so boring that I fell asleep",
        "I like to listen to music while I'm working",
        "She painted a beautiful picture of the mountains",
        "He told me that he would arrive at eight o'clock",
        "We are going to celebrate his birthday next weekend",
        "The train was delayed because of the bad weather",
        "I need to call my doctor to make an appointment",
        "They decided to postpone the meeting until next Monday"
    ];
    
    // Extended corpus - more sentences for better n-gram modeling
    const extendedCorpus = [
        // Additional common sentences
        "Please send me the report as soon as possible",
        "We need to discuss this matter in private",
        "I think we should consider all the options before making a decision",
        "The concert was amazing, the band played all their hit songs",
        "She graduated from university with a degree in computer science",
        "He spends most of his free time reading books and watching movies",
        "They are considering buying a new house in the suburbs",
        "We should book our flights and hotel for the summer vacation",
        "The company is planning to expand its operations overseas",
        "I prefer tea to coffee, especially in the morning",
        "The museum has a new exhibition of contemporary art",
        "He asked me to help him with his homework",
        "She speaks three languages fluently: English, French, and Spanish",
        "We need to find a solution to this problem as soon as possible",
        "The restaurant offers a wide variety of vegetarian dishes",
        "They have been married for twenty years and have three children",
        "I forgot to bring my umbrella and it started to rain",
        "She plays tennis every weekend with her friends",
        "He works for a multinational company as a software engineer",
        "We should leave early to avoid the traffic",
        "The book was so interesting that I couldn't put it down",
        "They decided to renovate their kitchen last summer",
        "I need to buy a new laptop because mine is getting old",
        "She invited all her friends to her birthday party",
        "He prefers to walk to work instead of taking the bus",
        "We enjoyed the vacation despite the bad weather",
        "The hotel room had a beautiful view of the ocean",
        "I have an appointment with the dentist next Tuesday",
        "She always wanted to learn how to play the piano",
        "He bought a new car last month, it's very fuel-efficient",
        // Add more sentences here as needed
    ];
    
    // Combine all corpus data
    const fullCorpus = [...sampleCorpus, ...extendedCorpus];
    
    // Initialize and train the n-gram model
    const bigramModel = new NGramModel(2);
    const trigramModel = new NGramModel(3);
    
    // Train models with the corpus
    bigramModel.train(fullCorpus);
    trigramModel.train(fullCorpus);

    // Create a more comprehensive dictionary by extracting words from corpus
    const corpus_words = new Set();
    for (const text of fullCorpus) {
        const words = text.toLowerCase().replace(/[^\w\s']|_/g, " ").split(/\s+/);
        for (const word of words) {
            if (word) corpus_words.add(word);
        }
    }
    
    // Convert dictionary and corpus words to a combined array for Levenshtein distance checks
    const dictionaryArray = [...new Set([...dictionary, ...corpus_words])];
    
    // Functions
    function updateWordAndCharCount() {
        const text = editor.textContent || '';
        const charCount = text.length;
        const wordCount = text.trim() === '' ? 0 : text.trim().split(/\s+/).length;
        
        wordCountEl.textContent = `${wordCount} ${wordCount === 1 ? 'word' : 'words'}`;
        charCountEl.textContent = `${charCount} ${charCount === 1 ? 'character' : 'characters'}`;
    }

    function checkSpelling() {
        try {
            const text = editor.textContent || '';
            
            if (text.trim() === '') {
                alert('Please enter some text to check.');
                return;
            }
            
            // Show loading state
            checkSpellingBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Checking...';
            checkSpellingBtn.disabled = true;
            
            // Process text with advanced algorithms (more resource-intensive)
            setTimeout(() => {
                const result = processTextAdvanced(text);
                displaySpellingResults(result);
                
                // Reset button state
                checkSpellingBtn.innerHTML = '<i class="fas fa-check"></i> Check Spelling';
                checkSpellingBtn.disabled = false;
            }, 500);
            
        } catch (error) {
            console.error('Error checking spelling:', error);
            alert(`Error checking spelling: ${error.message}`);
            
            // Reset button state
            checkSpellingBtn.innerHTML = '<i class="fas fa-check"></i> Check Spelling';
            checkSpellingBtn.disabled = false;
        }
    }

    function processTextAdvanced(text) {
        // Tokenize the text (split into words preserving punctuation)
        const tokens = text.split(/(\s+|[.,!?;:'"()])/);
        const corrections = [];
        const grammarIssues = [];
        const correctedWords = [];
        let contextWindow = [];
        
        // Process each token
        tokens.forEach((token, index) => {
            // Skip whitespace and punctuation
            if (!token.trim() || /^[.,!?;:'"()]+$/.test(token)) {
                correctedWords.push(token);
                return;
            }
            
            // Add to context window for n-gram analysis
            if (/\w/.test(token)) {
                contextWindow.push(token.toLowerCase());
                if (contextWindow.length > 5) contextWindow.shift(); // Keep last 5 words
            }
            
            const lowerToken = token.toLowerCase();
            
            // Check for common misspellings first
            if (commonMisspellings[lowerToken]) {
                let suggestion = commonMisspellings[lowerToken];
                
                // Preserve capitalization
                if (token[0] === token[0].toUpperCase()) {
                    suggestion = suggestion.charAt(0).toUpperCase() + suggestion.slice(1);
                }
                
                corrections.push({
                    original: token,
                    suggestions: [suggestion, ...findSimilarWords(lowerToken, dictionaryArray, 2, 4)],
                    position: index
                });
                
                correctedWords.push(token);
            }
            // Check against dictionary
            else if (/^[a-z]+$/i.test(token) && token.length > 1 && !dictionary.has(lowerToken)) {
                // Find similar words using Levenshtein distance
                const similarWords = findSimilarWords(lowerToken, dictionaryArray, 2, 5);
                
                corrections.push({
                    original: token,
                    suggestions: similarWords,
                    position: index
                });
                
                correctedWords.push(token);
            }
            // The word is valid but check for contextual errors if we have enough context
            else if (contextWindow.length >= 3 && /^[a-z]+$/i.test(token)) {
                // Get context without the current word
                const context = contextWindow.slice(0, -1).join(" ");
                
                // Use trigram model for context analysis
                if (contextWindow.length >= 3) {
                    const probability = trigramModel.getProbability(context, lowerToken);
                    
                    // If probability is very low, it might be contextually wrong
                    if (probability < 0.01 && probability !== 0) {
                        // Get more suitable words for this context
                        const suggestions = trigramModel.getNextWordCandidates(context, 5);
                        
                        // Only suggest if we have alternatives and the word isn't the first suggestion
                        if (suggestions.length > 0 && suggestions[0] !== lowerToken) {
                            corrections.push({
                                original: token,
                                suggestions: suggestions,
                                position: index,
                                type: "contextual" // Mark as contextual error
                            });
                        }
                    }
                }
                
                correctedWords.push(token);
            }
            else {
                correctedWords.push(token);
            }
        });
        
        // Check grammar with rules
        const fullText = text;
        grammarRules.forEach(rule => {
            const matches = [...fullText.matchAll(rule.pattern)];
            matches.forEach(match => {
                // Skip if there's a context pattern and it doesn't match
                if (rule.contextPattern && !rule.contextPattern.test(fullText.slice(Math.max(0, match.index - 20), match.index + match[0].length + 20))) {
                    return;
                }
                
                grammarIssues.push({
                    type: "grammar",
                    issue: `Possible grammar error: ${match[0]}`,
                    position: match.index,
                    suggestion: typeof rule.replacement === 'function' ? 
                        rule.replacement(match[0]) : rule.replacement
                });
            });
        });
        
        // Return combined results
        return {
            original_text: text,
            corrected_text: correctedWords.join(''),
            corrections: corrections,
            grammar_issues: grammarIssues
        };
    }

    function displaySpellingResults(data) {
        // Clear previous results
        correctionsList.innerHTML = '';
        grammarList.innerHTML = '';
        
        // Display spelling corrections
        if (data.corrections && data.corrections.length > 0) {
            // Group corrections by type
            const standardCorrections = data.corrections.filter(c => !c.type);
            const contextualCorrections = data.corrections.filter(c => c.type === "contextual");
            
            // Standard spelling errors
            if (standardCorrections.length > 0) {
                const spellingHeader = document.createElement('h4');
                spellingHeader.textContent = 'Spelling Suggestions';
                correctionsList.appendChild(spellingHeader);
                
                standardCorrections.forEach(correction => {
                    const correctionItem = document.createElement('div');
                    correctionItem.className = 'correction-item';
                    correctionItem.dataset.originalWord = correction.original;
                    
                    correctionItem.innerHTML = `
                        <div>
                            <span class="original-word">${correction.original}</span>
                            <div class="suggestion-list">
                                ${correction.suggestions.map(suggestion => 
                                    `<span class="suggestion" data-word="${correction.original}" data-replacement="${suggestion}">${suggestion}</span>`
                                ).join('')}
                            </div>
                        </div>
                    `;
                    
                    correctionsList.appendChild(correctionItem);
                });
            }
            
            // Contextual errors
            if (contextualCorrections.length > 0) {
                const contextHeader = document.createElement('h4');
                contextHeader.textContent = 'Contextual Word Suggestions';
                contextHeader.style.marginTop = '20px';
                correctionsList.appendChild(contextHeader);
                
                contextualCorrections.forEach(correction => {
                    const correctionItem = document.createElement('div');
                    correctionItem.className = 'correction-item contextual';
                    correctionItem.dataset.originalWord = correction.original;
                    
                    correctionItem.innerHTML = `
                        <div>
                            <span class="original-word">${correction.original}</span>
                            <p class="context-info">This word might not fit the context.</p>
                            <div class="suggestion-list">
                                ${correction.suggestions.map(suggestion => 
                                    `<span class="suggestion" data-word="${correction.original}" data-replacement="${suggestion}">${suggestion}</span>`
                                ).join('')}
                            </div>
                        </div>
                    `;
                    
                    correctionsList.appendChild(correctionItem);
                });
            }
            
            // Add event listeners to suggestions
            document.querySelectorAll('.suggestion').forEach(suggestionEl => {
                suggestionEl.addEventListener('click', function() {
                    const word = this.getAttribute('data-word');
                    const replacement = this.getAttribute('data-replacement');
                    replaceWord(word, replacement);
                    
                    // Find and remove the correction item containing this suggestion
                    const correctionItem = this.closest('.correction-item');
                    if (correctionItem) {
                        correctionItem.remove();
                    }
                    
                    // If no more corrections, hide the results panel
                    if (correctionsList.querySelectorAll('.correction-item').length === 0) {
                        spellingResults.classList.add('hidden');
                    }
                });
            });
        } else {
            correctionsList.innerHTML = '<p>No spelling issues found.</p>';
        }
        
        // Display grammar issues
        if (data.grammar_issues && data.grammar_issues.length > 0) {
            const grammarHeader = document.createElement('h3');
            grammarHeader.textContent = 'Grammar Suggestions';
            grammarList.appendChild(grammarHeader);
            
            data.grammar_issues.forEach(issue => {
                const grammarItem = document.createElement('div');
                grammarItem.className = 'grammar-item';
                
                grammarItem.innerHTML = `
                    <div>
                        <p><strong>Issue:</strong> ${issue.issue}</p>
                        <p><strong>Suggestion:</strong> ${issue.suggestion}</p>
                    </div>
                `;
                
                grammarList.appendChild(grammarItem);
            });
        }
        
        // Show results panel
        spellingResults.classList.remove('hidden');
        
        // Highlight misspelled words in the editor
        highlightMisspelledWords(data.corrections);
    }

    function highlightMisspelledWords(corrections) {
        if (!corrections || corrections.length === 0) return;
        
        // Get the editor's content
        let content = editor.textContent;
        editor.innerHTML = '';
        
        // Create a map of words to highlight
        const wordsToHighlight = new Map();
        corrections.forEach(correction => {
            wordsToHighlight.set(correction.original, {
                suggestions: correction.suggestions,
                type: correction.type || 'spelling'
            });
        });
        
        // Split the content by spaces and wrap misspelled words
        const words = content.split(/(\s+|[.,!?;:'"()])/);
        
        words.forEach(word => {
            if (wordsToHighlight.has(word)) {
                const span = document.createElement('span');
                span.textContent = word;
                span.className = wordsToHighlight.get(word).type === 'contextual' ? 
                    'contextual-error' : 'misspelled';
                span.dataset.suggestions = JSON.stringify(wordsToHighlight.get(word).suggestions);
                span.addEventListener('dblclick', showSynonyms);
                editor.appendChild(span);
            } else {
                editor.appendChild(document.createTextNode(word));
            }
        });
    }

    function showSynonyms(event) {
        const word = event.target.textContent.toLowerCase();
        synonymWord.textContent = word;
        
        try {
            let synonymCandidates = new Set();
            const context = getContext(word);
            
            // Get contextual suggestions
            if (context && trigramModel.totalWords > 0) {
                const contextSuggestions = trigramModel.getNextWordCandidates(context, 5);
                contextSuggestions.forEach(s => synonymCandidates.add(s));
            }
            
            // Find similar adjectives if the word is in our adjective list
            const allWords = Array.from(dictionary);
            const similarWords = findSimilarWords(word, allWords, 2, 10);
            similarWords.forEach(s => synonymCandidates.add(s));
            
            // Additional synonyms for adjectives (using predefined groups)
            const adjectiveGroups = {
                beautiful: ["pretty", "gorgeous", "lovely", "attractive", "stunning", "wonderful", "elegant", "charming", "graceful", "radiant"],
                good: ["great", "excellent", "wonderful", "fantastic", "amazing", "superb", "outstanding", "terrific", "marvelous", "splendid"],
                bad: ["terrible", "awful", "poor", "horrible", "dreadful", "unpleasant", "atrocious", "abysmal", "lousy", "inferior"],
                big: ["large", "huge", "massive", "gigantic", "enormous", "colossal", "immense", "tremendous", "vast", "monumental"],
                small: ["tiny", "little", "miniature", "compact", "microscopic", "petite", "diminutive", "minuscule", "mini", "wee"],
                happy: ["joyful", "cheerful", "delighted", "pleased", "content", "glad", "merry", "jovial", "elated", "thrilled"],
                sad: ["unhappy", "depressed", "gloomy", "melancholy", "sorrowful", "downcast", "disheartened", "dejected", "despondent", "miserable"],
                fast: ["quick", "rapid", "swift", "speedy", "brisk", "hasty", "fleet", "expeditious", "accelerated", "hurried"],
                slow: ["sluggish", "leisurely", "gradual", "unhurried", "languid", "deliberate", "plodding", "measured", "relaxed", "easygoing"],
                smart: ["intelligent", "clever", "bright", "brilliant", "sharp", "wise", "astute", "brainy", "quick-witted", "perceptive"],
                strong: ["powerful", "mighty", "forceful", "sturdy", "robust", "muscular", "tough", "vigorous", "potent", "solid"],
                weak: ["feeble", "frail", "fragile", "delicate", "powerless", "impotent", "helpless", "vulnerable", "debilitated", "enervated"],
                hot: ["warm", "heated", "scorching", "blazing", "burning", "fiery", "sizzling", "sweltering", "torrid", "boiling"],
                cold: ["chilly", "cool", "freezing", "frigid", "icy", "frosty", "arctic", "glacial", "wintry", "nippy"],
                new: ["fresh", "recent", "modern", "contemporary", "current", "novel", "innovative", "up-to-date", "brand-new", "latest"],
                old: ["ancient", "aged", "elderly", "antique", "vintage", "mature", "senior", "timeworn", "hoary", "archaic"],
                clean: ["spotless", "immaculate", "pristine", "tidy", "neat", "sanitary", "hygienic", "unsoiled", "unsullied", "pure"],
                dirty: ["filthy", "soiled", "grimy", "stained", "unclean", "messy", "muddy", "dusty", "squalid", "polluted"]
            };
            
            // If the word is an adjective, add its synonyms
            for (const [key, synonyms] of Object.entries(adjectiveGroups)) {
                if (word === key || synonyms.includes(word)) {
                    synonyms.forEach(s => synonymCandidates.add(s));
                    adjectiveGroups[key].forEach(s => synonymCandidates.add(s));
                }
            }
            
            // Remove the original word from candidates
            synonymCandidates.delete(word);
            
            // Clear previous synonyms
            synonymList.innerHTML = '';
            
            if (synonymCandidates.size > 0) {
                Array.from(synonymCandidates).forEach(synonym => {
                    const synonymItem = document.createElement('div');
                    synonymItem.className = 'synonym-item';
                    synonymItem.textContent = synonym;
                    
                    synonymItem.addEventListener('click', function() {
                        // Preserve capitalization if the original word started with uppercase
                        let replacement = synonym;
                        if (word[0] === word[0].toUpperCase()) {
                            replacement = synonym.charAt(0).toUpperCase() + synonym.slice(1);
                        }
                        
                        replaceWord(word, replacement);
                        closeModalHandler();
                    });
                    
                    synonymList.appendChild(synonymItem);
                });
            } else {
                synonymList.innerHTML = '<p>No synonyms found for this word.</p>';
            }
            
            // Show the modal
            synonymModal.style.display = 'block';
            
        } catch (error) {
            console.error('Error finding synonyms:', error);
            synonymList.innerHTML = '<p>Error finding synonyms.</p>';
            synonymModal.style.display = 'block';
        }
    }
    
    // Helper to get context for a word
    function getContext(word) {
        const content = editor.textContent;
        const wordIndex = content.indexOf(word);
        
        if (wordIndex === -1) return '';
        
        // Get up to 20 characters before the word
        const startIndex = Math.max(0, wordIndex - 50);
        const context = content.slice(startIndex, wordIndex);
        
        // Extract the last few words for context
        const contextWords = context.split(/\s+/).slice(-3);
        return contextWords.join(' ');
    }

    function replaceWord(word, replacement) {
        // Try to find the word in misspelled or contextual spans
        const misspelledSpans = document.querySelectorAll('.misspelled, .contextual-error');
        let replaced = false;
        
        for (const span of misspelledSpans) {
            if (span.textContent === word) {
                // Replace just this instance
                span.outerHTML = replacement;
                replaced = true;
                break; // Only replace the first occurrence
            }
        }
        
        // If we couldn't find the word in highlighted spans, try a general replacement
        if (!replaced) {
            const content = editor.innerHTML;
            const wordRegex = new RegExp(`<span class="(misspelled|contextual-error)"[^>]*>${word}</span>`, 'g');
            editor.innerHTML = content.replace(wordRegex, replacement);
        }
        
        // Improved sentence capitalization logic
        let content = editor.innerHTML;
        
        // First, convert all text to lowercase
        content = content.toLowerCase();
        
        // Split into sentences more accurately (handling multiple spaces and newlines)
        const sentences = content.split(/([.!?]+[\s\n]+)/g);
        let modifiedContent = '';
        
        sentences.forEach((part, index) => {
            if (index % 2 === 0) { // This is a sentence part
                // Find the first letter in the sentence
                const match = part.match(/[a-z]/i);
                if (match) {
                    const pos = match.index;
                    // Capitalize only the first letter, keep the rest lowercase
                    modifiedContent += part.slice(0, pos) + 
                                     part.charAt(pos).toUpperCase() + 
                                     part.slice(pos + 1);
                } else {
                    modifiedContent += part;
                }
            } else { // This is a separator part (.!? followed by spaces)
                modifiedContent += part;
            }
        });
        
        // Handle the first sentence if content doesn't start with a separator
        if (modifiedContent.length > 0) {
            const firstLetterMatch = modifiedContent.match(/[a-z]/i);
            if (firstLetterMatch) {
                const pos = firstLetterMatch.index;
                modifiedContent = modifiedContent.slice(0, pos) + 
                                modifiedContent.charAt(pos).toUpperCase() + 
                                modifiedContent.slice(pos + 1);
            }
        }
        
        editor.innerHTML = modifiedContent;
        
        // Update word and character count
        updateWordAndCharCount();
        
        // Remove all correction items for this word
        document.querySelectorAll(`.correction-item[data-original-word="${word}"]`).forEach(item => {
            item.remove();
        });
        
        // Check if there are any more corrections
        const remainingCorrections = document.querySelectorAll('.misspelled, .contextual-error');
        if (remainingCorrections.length === 0) {
            // If no more corrections, hide the results panel
            spellingResults.classList.add('hidden');
        }
    }

    function closeModalHandler() {
        synonymModal.style.display = 'none';
    }

    function clearEditor() {
        editor.innerHTML = '';
        spellingResults.classList.add('hidden');
        updateWordAndCharCount();
    }

    function copyToClipboard() {
        const text = editor.textContent;
        
        if (text.trim() === '') {
            alert('Nothing to copy.');
            return;
        }
        
        // Create a temporary textarea element
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        
        // Select and copy the text
        textarea.select();
        document.execCommand('copy');
        
        // Remove the temporary textarea
        document.body.removeChild(textarea);
        
        // Show a success message
        const originalHTML = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        
        setTimeout(() => {
            copyBtn.innerHTML = originalHTML;
        }, 2000);
    }
});
