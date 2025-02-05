from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch
import sys

app = Flask(__name__)
CORS(app)

# Configuration
MODEL_NAME = "google/flan-t5-base"
MAX_CONTEXT_LENGTH = 512
MAX_ANSWER_LENGTH = 150
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def log_progress(message):
    print(message)
    sys.stdout.flush()

log_progress("Initializing AI server...")

try:
    log_progress("Loading NLP model...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(DEVICE)
    generator = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        device=0 if DEVICE == "cuda" else -1
    )
    log_progress("Model loaded successfully!")
except Exception as e:
    log_progress(f"Model loading error: {str(e)}")
    raise

def load_item_context(item_type):
    try:
        file_mapping = {
            'diamondpickaxe': 'diamond_pickaxe.txt',
            'whiskyglass': 'whisky_glass.txt',
            'veganfur': 'vegan_fur.txt',
            'studyguide': 'study_guide.txt',
            'lumberjackburger': 'lumberjack_burger.txt'
        }
        
        filename = file_mapping.get(item_type.lower())
        if not filename:
            raise ValueError(f"Unknown item type: {item_type}")
            
        with open(f"items/{filename}", "r", encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        log_progress(f"Context loading error: {e}")
        return None

def preprocess_context(context):
    tokens = tokenizer.encode(context, max_length=MAX_CONTEXT_LENGTH, truncation=True)
    return tokenizer.decode(tokens, skip_special_tokens=True)

def generate_answer(question, context):
    try:
        prompt = f"""Generate a factual answer to the question using only the context. 
Use complete sentences. If information is missing, say "I don't know".

Context: {context}

Question: {question}
Answer: According to the available information,"""

        result = generator(
            prompt,
            max_length=MAX_ANSWER_LENGTH,
            num_return_sequences=1,
            temperature=0.7,
            repetition_penalty=1.0,
            do_sample=True,
            top_k=30,
            top_p=0.9,
            clean_up_tokenization_spaces=True
        )
        
        answer = result[0]['generated_text'].strip()
        answer = answer.replace("According to the available information,", "").strip()
        
        # Formatting rules
        if answer.lower().startswith("the "):
            answer = answer[0].upper() + answer[1:]
        elif answer:
            answer = answer[0].upper() + answer[1:].lower()
        
        if not answer.endswith('.'):
            answer += '.'
            
        return answer
        
    except Exception as e:
        log_progress(f"Generation error: {e}")
        return "An error occurred while generating the answer."

@app.route('/generate', methods=['POST'])
def handle_query():
    try:
        data = request.json
        item_type = data.get('itemType')
        question = data.get('question')
        
        if not item_type or not question:
            return jsonify({"error": "Missing required parameters"}), 400
            
        context = load_item_context(item_type)
        if not context:
            return jsonify({"error": "Context not found"}), 404
            
        processed_context = preprocess_context(context)
        answer = generate_answer(question, processed_context)
        
        return jsonify({
            "response": answer,
            "contextSnippet": processed_context[:200] + "..."  # For debugging
        })
        
    except Exception as e:
        log_progress(f"Server error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)