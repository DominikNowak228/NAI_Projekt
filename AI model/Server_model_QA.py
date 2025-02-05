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
    model_name = "deepset/roberta-base-squad2"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    log_progress(f"Loading QA model on {device}...")
    qa_pipeline = pipeline(
        "question-answering",
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
            
        with open(f"./items/{filename}", "r", encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error loading item context: {e}")
        return None

def get_answer(context, question):
    try:
        log_progress(f"\nProcessing question: {question}")
        
        tokens = qa_pipeline.tokenizer.encode(context)
        if len(tokens) > 450:
            log_progress(f"Context too long ({len(tokens)} tokens). Truncating...")
            tokens = tokens[:450]
            context = qa_pipeline.tokenizer.decode(tokens, skip_special_tokens=True)
        
        result = qa_pipeline(
            question=question,
            context=context,
            max_answer_len=50,
            handle_impossible_answer=True
        )
        
        log_progress(f"Answer score: {result['score']:.2f}")
        
        if result['score'] < 0.1:
            return "Nie mam wystarczających informacji, aby odpowiedzieć na to pytanie."
            
        answer = result['answer'].strip()
        log_progress(f"Generated answer: {answer}")
        
        if len(answer) < 2 or question.lower() in answer.lower():
            return "Nie jestem pewien odpowiedzi na to pytanie."
            
        # Prosta, ale kompletna odpowiedź
        return answer
        
    except Exception as e:
        log_progress(f"Error in get_answer: {e}")
        return "Przepraszam, wystąpił problem z przetworzeniem Twojego pytania."

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
    app.run(port=5000)  # Używamy innego portu niż index.py 