# Advanced Grammar and Spell Checker

A powerful web application that checks grammar, spelling, and suggests synonyms for adjectives and adverbs in your text.

## Features

- Grammar and spelling checking
- Synonym suggestions for adjectives and adverbs
- Modern and user-friendly interface
- Real-time text analysis
- Statistics about your text (word count, corrections, synonyms found)

## Prerequisites

Before running the application, make sure you have the following installed:

1. Python 3.8 or higher
2. Java Runtime Environment (JRE) - Required for LanguageTool
3. pip (Python package manager)

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
```

2. Activate the virtual environment:
- On Windows:
```bash
venv\Scripts\activate
```
- On macOS/Linux:
```bash
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure you're in the project directory and your virtual environment is activated

2. Start the Flask application:
```bash
python app.py
```

3. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Enter your text in the text area
2. Click the "Check & Improve" button
3. View the results:
   - Corrected text with grammar and spelling fixes
   - Suggested synonyms for adjectives and adverbs
   - Text statistics

## Example

Input:
```
The beautiful sunset was very fast and the sky looked pretty.
```

Output will show:
- Grammar and spelling corrections
- Synonyms for "beautiful" (pretty, lovely, gorgeous, stunning, attractive)
- Synonyms for "fast" (quick, rapid, swift, speedy, brisk)
- Synonyms for "pretty" (beautiful, lovely, attractive, charming, cute)

## Dependencies

- Flask==3.0.2
- language-tool-python==2.7.1
- nltk==3.8.1

## Troubleshooting

If you encounter any issues:

1. Make sure Java is installed and in your system PATH
2. Check that all dependencies are installed correctly
3. Ensure you're using Python 3.8 or higher
4. Try clearing the NLTK cache if you encounter download issues:
```bash
rm -rf ~/.cache/language_tool_python
```
