from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import torch
import sys

app = Flask(__name__)
CORS(app)

def log_progress(message):
    print(message)
    sys.stdout.flush()

log_progress("Starting server initialization...")
log_progress("Initializing model loading...")

try:
    model_name = "facebook/bart-large-cnn"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    log_progress(f"Loading model on {device}...")
    summarizer = pipeline(
        "summarization",
        model=model_name,
        device=0 if torch.cuda.is_available() else -1
    )
    log_progress("Model loaded successfully!")
    
except Exception as e:
    log_progress(f"Error during model loading: {str(e)}")
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
        print(f"Error loading item context: {e}")
        return None

def truncate_context(context, max_tokens=800):
    """Truncate context to fit within BART's limits, leaving room for prompt"""
    tokens = summarizer.tokenizer.encode(context)
    if len(tokens) > max_tokens:
        log_progress(f"Context too long ({len(tokens)} tokens). Truncating to {max_tokens} tokens.")
        tokens = tokens[:max_tokens]
        context = summarizer.tokenizer.decode(tokens, skip_special_tokens=True)
    else:
        log_progress(f"Context length: {len(tokens)} tokens")
    return context

def get_answer(context, question):
    try:
        # Truncate context if needed (leaving room for prompt and question)
        context = truncate_context(context)
        
        prompt = f"""Please answer the following question about an item based only on the provided description.
        If the information is not in the description, respond with "Based on the description, I cannot answer this question."

        Item Description:
        {context}

        Question: {question}

        Answer:"""
        
        log_progress(f"\nProcessing prompt for question: {question}")
        
        # Sprawdź długość całego promptu
        prompt_tokens = len(summarizer.tokenizer.encode(prompt))
        log_progress(f"Total prompt length: {prompt_tokens} tokens")
        
        if prompt_tokens > 1024:
            log_progress("Warning: Prompt exceeds model's maximum token limit")
            return "Error: Input too long for processing"
        
        summary = summarizer(
            prompt,
            max_length=50,
            min_length=10,
            do_sample=False,
            truncation=True
        )
        
        answer = summary[0]['summary_text'].strip()
        log_progress(f"Generated answer: {answer}")
        
        if len(answer) < 5 or question.lower() in answer.lower():
            return "Based on the description, I cannot answer this question."
            
        return answer
        
    except Exception as e:
        log_progress(f"Error in get_answer: {e}")
        return "Sorry, I couldn't generate an answer at this time."

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        log_progress(f"\nProcessing request for: {data['itemType']}")
        
        item_type = data.get('itemType')
        question = data.get('question')
        
        if not item_type or not question:
            return jsonify({"error": "Missing itemType or question"}), 400
            
        context = load_item_context(item_type)
        if not context:
            return jsonify({"error": "Could not load item context"}), 404
            
        answer = get_answer(context, question)
        return jsonify({"response": answer})
        
    except Exception as e:
        log_progress(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()