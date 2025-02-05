from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import torch
import sys

app = Flask(__name__)
CORS(app)  # Umożliwienie CORS dla aplikacji

def log_progress(message):
    print(message)  # Logowanie wiadomości
    sys.stdout.flush()  # Wymuszenie wypisania na standardowe wyjście

log_progress("Starting server initialization...")  # Informacja o rozpoczęciu inicjalizacji serwera
log_progress("Initializing model loading...")  # Informacja o rozpoczęciu ładowania modelu

try:
    model_name = "facebook/bart-large-cnn"  # Nazwa modelu do podsumowywania
    device = "cuda" if torch.cuda.is_available() else "cpu"  # Użycie GPU, jeśli dostępne
    
    log_progress(f"Loading model on {device}...")  # Informacja o ładowaniu modelu
    summarizer = pipeline(
        "summarization",  # Typ pipeline'u
        model=model_name,
        device=0 if torch.cuda.is_available() else -1  # Ustawienie urządzenia
    )
    log_progress("Model loaded successfully!")  # Informacja o pomyślnym załadowaniu modelu
    
except Exception as e:
    log_progress(f"Error during model loading: {str(e)}")  # Logowanie błędu podczas ładowania modelu
    raise

def load_item_context(item_type):
    try:
        # Mapowanie typów przedmiotów na pliki
        file_mapping = {
            'diamondpickaxe': 'diamond_pickaxe.txt',
            'whiskyglass': 'whisky_glass.txt',
            'veganfur': 'vegan_fur.txt',
            'studyguide': 'study_guide.txt',
            'lumberjackburger': 'lumberjack_burger.txt'
        }
        
        filename = file_mapping.get(item_type.lower())  # Pobranie nazwy pliku
        if not filename:
            raise ValueError(f"Unknown item type: {item_type}")  # Błąd, jeśli typ nieznany
            
        with open(f"items/{filename}", "r", encoding='utf-8') as file:
            return file.read()  # Zwrócenie zawartości pliku
    except Exception as e:
        print(f"Error loading item context: {e}")  # Logowanie błędu podczas ładowania kontekstu
        return None

def truncate_context(context, max_tokens=800):
    """Truncate context to fit within BART's limits, leaving room for prompt"""
    tokens = summarizer.tokenizer.encode(context)  # Tokenizacja kontekstu
    if len(tokens) > max_tokens:  # Sprawdzenie długości tokenów
        log_progress(f"Context too long ({len(tokens)} tokens). Truncating to {max_tokens} tokens.")  # Logowanie o zbyt długim kontekście
        tokens = tokens[:max_tokens]  # Skrócenie kontekstu
        context = summarizer.tokenizer.decode(tokens, skip_special_tokens=True)  # Dekodowanie tokenów
    else:
        log_progress(f"Context length: {len(tokens)} tokens")  # Logowanie długości kontekstu
    return context  # Zwrócenie przetworzonego kontekstu

def get_answer(context, question):
    try:
        # Truncate context if needed (leaving room for prompt and question)
        context = truncate_context(context)  # Skrócenie kontekstu, jeśli to konieczne
        
        prompt = f"""Please answer the following question about an item based only on the provided description.
        If the information is not in the description, respond with "Based on the description, I cannot answer this question."

        Item Description:
        {context}

        Question: {question}

        Answer:"""  # Przygotowanie promptu
        
        log_progress(f"\nProcessing prompt for question: {question}")  # Logowanie przetwarzania promptu
        
        # Sprawdź długość całego promptu
        prompt_tokens = len(summarizer.tokenizer.encode(prompt))  # Obliczenie długości tokenów promptu
        log_progress(f"Total prompt length: {prompt_tokens} tokens")  # Logowanie długości promptu
        
        if prompt_tokens > 1024:  # Sprawdzenie, czy długość promptu przekracza limit
            log_progress("Warning: Prompt exceeds model's maximum token limit")  # Logowanie ostrzeżenia
            return "Error: Input too long for processing"  # Zwrócenie błędu
        
        summary = summarizer(
            prompt,
            max_length=50,  # Maksymalna długość odpowiedzi
            min_length=10,  # Minimalna długość odpowiedzi
            do_sample=False,  # Wyłączenie próbkowania
            truncation=True  # Włączenie skracania
        )
        
        answer = summary[0]['summary_text'].strip()  # Otrzymanie odpowiedzi
        log_progress(f"Generated answer: {answer}")  # Logowanie wygenerowanej odpowiedzi
        
        if len(answer) < 5 or question.lower() in answer.lower():  # Sprawdzenie, czy odpowiedź jest sensowna
            return "Based on the description, I cannot answer this question."
            
        return answer  # Zwrócenie odpowiedzi
        
    except Exception as e:
        log_progress(f"Error in get_answer: {e}")  # Logowanie błędu w funkcji get_answer
        return "Sorry, I couldn't generate an answer at this time."  # Zwrócenie błędu

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json  # Odczytanie danych JSON
        log_progress(f"\nProcessing request for: {data['itemType']}")  # Logowanie przetwarzania żądania
        
        item_type = data.get('itemType')  # Pobranie typu przedmiotu
        question = data.get('question')  # Pobranie pytania
        
        if not item_type or not question:  # Sprawdzenie, czy wymagane parametry są obecne
            return jsonify({"error": "Missing itemType or question"}), 400
            
        context = load_item_context(item_type)  # Załadowanie kontekstu
        if not context:
            return jsonify({"error": "Could not load item context"}), 404
            
        answer = get_answer(context, question)  # Uzyskanie odpowiedzi
        return jsonify({"response": answer})  # Zwrócenie odpowiedzi
        
    except Exception as e:
        log_progress(f"Error occurred: {e}")  # Logowanie błędu
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()  # Uruchomienie serwera