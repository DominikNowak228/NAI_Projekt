from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import torch
import sys

# Inicjalizacja aplikacji Flask
app = Flask(__name__)
CORS(app)  # Umożliwienie CORS dla aplikacji

def log_progress(message):
    print(message)  # Logowanie wiadomości
    sys.stdout.flush()  # Wymuszenie wypisania na standardowe wyjście

log_progress("Starting server initialization...")  # Informacja o rozpoczęciu inicjalizacji serwera
log_progress("Initializing model loading...")  # Informacja o rozpoczęciu ładowania modelu

try:
    model_name = "deepset/roberta-base-squad2"  # Nazwa modelu do zadawania pytań i odpowiedzi (QA)
    device = "cuda" if torch.cuda.is_available() else "cpu"  # Użycie GPU, jeśli dostępne
    
    log_progress(f"Loading QA model on {device}...")  # Informacja o ładowaniu modelu
    qa_pipeline = pipeline(
        "question-answering",  # Typ pipeline'u
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
            
        with open(f"./items/{filename}", "r", encoding='utf-8') as file:
            return file.read()  # Zwrócenie zawartości pliku
    except Exception as e:
        print(f"Error loading item context: {e}")  # Logowanie błędu podczas ładowania kontekstu
        return None

def get_answer(context, question):
    try:
        log_progress(f"\nProcessing question: {question}")  # Logowanie przetwarzania pytania
        
        tokens = qa_pipeline.tokenizer.encode(context)  # Tokenizacja kontekstu
        if len(tokens) > 450:  # Sprawdzenie długości tokenów
            log_progress(f"Context too long ({len(tokens)} tokens). Truncating...")  # Logowanie o zbyt długim kontekście
            tokens = tokens[:450]  # Skrócenie kontekstu
            context = qa_pipeline.tokenizer.decode(tokens, skip_special_tokens=True)  # Dekodowanie tokenów
        
        # Generowanie odpowiedzi za pomocą modelu QA
        result = qa_pipeline(
            question=question,
            context=context,
            max_answer_len=50,  # Maksymalna długość odpowiedzi
            handle_impossible_answer=True  # Obsługa pytań bez odpowiedzi
        )
        
        log_progress(f"Answer score: {result['score']:.2f}")  # Logowanie wyniku odpowiedzi
        
        if result['score'] < 0.1:  # Sprawdzenie wyniku odpowiedzi
            return "Nie mam wystarczających informacji, aby odpowiedzieć na to pytanie."  # Zwrócenie odpowiedzi, jeśli wynik jest zbyt niski
            
        answer = result['answer'].strip()  # Otrzymanie odpowiedzi
        log_progress(f"Generated answer: {answer}")  # Logowanie wygenerowanej odpowiedzi
        
        if len(answer) < 2 or question.lower() in answer.lower():  # Sprawdzenie, czy odpowiedź jest sensowna
            return "Nie jestem pewien odpowiedzi na to pytanie."
            
        return answer  # Zwrócenie odpowiedzi
        
    except Exception as e:
        log_progress(f"Error in get_answer: {e}")  # Logowanie błędu w funkcji get_answer
        return "Przepraszam, wystąpił problem z przetworzeniem Twojego pytania."  # Zwrócenie błędu

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
    app.run(port=5000)  # Uruchomienie serwera na porcie 5000