"""
Translation Service for AI-Based Recommendations Engine
Provides automatic translation capabilities for multiple languages
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import googletrans
from googletrans import Translator
import traceback

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5000", "http://127.0.0.1:5000", "http://localhost", "http://127.0.0.1", "http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:*", "http://127.0.0.1:*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize translator
translator = Translator()

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'bn': 'Bengali'
}

@app.route('/translate', methods=['POST'])
def translate_text():
    """Translate text to specified language"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data or 'target_lang' not in data:
            return jsonify({'error': 'Missing text or target_lang in request'}), 400
        
        text = data['text']
        target_lang = data['target_lang']
        
        # Validate target language
        if target_lang not in SUPPORTED_LANGUAGES:
            return jsonify({'error': f'Unsupported language. Supported languages: {list(SUPPORTED_LANGUAGES.keys())}'}), 400
        
        # Translate text
        result = translator.translate(text, dest=target_lang)
        
        return jsonify({
            'translated_text': result.text,
            'source_lang': result.src,
            'target_lang': target_lang
        })
        
    except Exception as e:
        print(f"Translation error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/translate_batch', methods=['POST'])
def translate_batch():
    """Translate multiple texts to specified language"""
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data or 'target_lang' not in data:
            return jsonify({'error': 'Missing texts or target_lang in request'}), 400
        
        texts = data['texts']
        target_lang = data['target_lang']
        
        # Validate target language
        if target_lang not in SUPPORTED_LANGUAGES:
            return jsonify({'error': f'Unsupported language. Supported languages: {list(SUPPORTED_LANGUAGES.keys())}'}), 400
        
        # Translate all texts with retry mechanism
        translated_texts = []
        for text in texts:
            try:
                # Skip empty texts
                if not text or not text.strip():
                    translated_texts.append({
                        'original': text,
                        'translated': text,
                        'source_lang': 'unknown'
                    })
                    continue
                
                # Try to translate with retry mechanism
                max_retries = 3
                translation_success = False
                last_error = None
                
                for attempt in range(max_retries):
                    try:
                        result = translator.translate(text, dest=target_lang)
                        translated_texts.append({
                            'original': text,
                            'translated': result.text,
                            'source_lang': result.src
                        })
                        translation_success = True
                        break  # Success, exit retry loop
                    except Exception as e:
                        last_error = e
                        if attempt < max_retries - 1:  # Not the last attempt
                            # Wait a bit before retrying
                            import time
                            time.sleep(0.1)
                        
                if not translation_success:
                    # If all retries failed, keep original text
                    print(f"Translation failed after {max_retries} attempts for text '{text}': {last_error}")
                    translated_texts.append({
                        'original': text,
                        'translated': text,  # Keep original if translation fails
                        'source_lang': 'unknown',
                        'error': str(last_error)
                    })
            except Exception as e:
                print(f"Translation error for text '{text}': {e}")
                translated_texts.append({
                    'original': text,
                    'translated': text,  # Keep original if translation fails
                    'source_lang': 'unknown',
                    'error': str(e)
                })
        
        return jsonify({
            'translations': translated_texts,
            'target_lang': target_lang
        })
        
    except Exception as e:
        print(f"Batch translation error: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Translation service error: {str(e)}'}), 500

@app.route('/languages', methods=['GET'])
def get_supported_languages():
    """Get list of supported languages"""
    return jsonify(SUPPORTED_LANGUAGES)

if __name__ == '__main__':
    print("Starting Translation Service...")
    print(f"Supported languages: {SUPPORTED_LANGUAGES}")
    app.run(debug=True, host='0.0.0.0', port=5001)