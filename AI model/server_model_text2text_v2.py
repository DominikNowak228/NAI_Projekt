from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch
import sys
import time  # Import modułu time do pomiaru czasu

# Inicjalizacja aplikacji Flask
app = Flask(__name__)
CORS(app)  # Umożliwienie CORS dla aplikacji

# Konfiguracja modelu
MODEL_NAME = "google/flan-t5-base"  # Nazwa modelu NLP
MAX_CONTEXT_LENGTH = 512  # Maksymalna długość kontekstu w tokenach
MAX_ANSWER_LENGTH = 150  # Maksymalna długość odpowiedzi w tokenach
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"  # Użycie GPU, jeśli dostępne

def log_progress(message):
    print(message)  # Logowanie wiadomości
    sys.stdout.flush()  # Wymuszenie wypisania na standardowe wyjście

log_progress("Initializing AI server...")  # Informacja o rozpoczęciu inicjalizacji serwera

try:
    log_progress("Loading NLP model...")  # Informacja o ładowaniu modelu
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)  # Ładowanie tokenizera
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(DEVICE)  # Ładowanie modelu
    generator = pipeline(
        "text2text-generation",  # Typ pipeline'u do generowania tekstu
        model=model,
        tokenizer=tokenizer,
        device=0 if DEVICE == "cuda" else -1  # Ustawienie urządzenia
    )
    log_progress("Model loaded successfully!")  # Informacja o pomyślnym załadowaniu modelu
except Exception as e:
    log_progress(f"Model loading error: {str(e)}")  # Logowanie błędu podczas ładowania modelu
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
        log_progress(f"Context loading error: {e}")  # Logowanie błędu podczas ładowania kontekstu
        return None

def preprocess_context(context):
    # Tokenizacja kontekstu i skrócenie go do maksymalnej długości
    tokens = tokenizer.encode(context, max_length=MAX_CONTEXT_LENGTH, truncation=True)
    return tokenizer.decode(tokens, skip_special_tokens=True)  # Dekodowanie tokenów

def generate_answer(question, context):
    try:
        # Przygotowanie promptu dla modelu
        prompt = f"""Generate a factual answer to the question using only the context. 
Use complete sentences. If information is missing, say "I don't know".

Context: {context}

Question: {question}
Answer: According to the available information,"""  # Przygotowanie promptu

        # Generowanie odpowiedzi za pomocą modelu
        result = generator(
            prompt,
            max_length=MAX_ANSWER_LENGTH,  # Maksymalna długość odpowiedzi
            num_return_sequences=1,  # Liczba generowanych odpowiedzi
            temperature=0.7,  # Parametr kontrolujący losowość odpowiedzi
            repetition_penalty=1.0,  # Kara za powtarzanie się
            do_sample=True,  # Włączenie próbkowania
            top_k=30,  # Ograniczenie do 30 najlepszych tokenów
            top_p=0.9,  # Ograniczenie do tokenów o łącznym prawdopodobieństwie 90%
            clean_up_tokenization_spaces=True  # Czyszczenie spacji po tokenizacji
        )
        
        answer = result[0]['generated_text'].strip()  # Otrzymanie odpowiedzi
        answer = answer.replace("According to the available information,", "").strip()  # Usunięcie wstępu
        
        # Formatowanie odpowiedzi
        if answer.lower().startswith("the "):  # Jeśli odpowiedź zaczyna się od "the"
            answer = answer[0].upper() + answer[1:]  # Ustawienie wielkiej litery na początku
        elif answer:
            answer = answer[0].upper() + answer[1:].lower()  # Ustawienie wielkiej litery na początku
        
        if not answer.endswith('.'):  # Jeśli odpowiedź nie kończy się kropką
            answer += '.'  # Dodanie kropki na końcu
            
        return answer  # Zwrócenie odpowiedzi
        
    except Exception as e:
        log_progress(f"Generation error: {e}")  # Logowanie błędu podczas generowania odpowiedzi
        return "An error occurred while generating the answer."  # Zwrócenie komunikatu o błędzie

def generate_full_sentence_answer(question, initial_answer):
    """
    Ta funkcja otrzymuje oryginalne zapytanie oraz wygenerowaną wcześniej odpowiedź,
    a następnie tworzy dopracowaną odpowiedź w pełnym zdaniu.
    """
    try:
        # Przygotowanie promptu dla modelu
        prompt = f"""Based on the original question and the initial answer provided below,
please generate a refined, complete sentence that fully explains the answer. 
In your answer, make sure to include any relevant context from the question if needed.

Original Question: {question}

Initial Answer: {initial_answer}

Refined, complete sentence answer:"""  # Przygotowanie promptu dla dopracowanej odpowiedzi
        
        # Generowanie dopracowanej odpowiedzi
        result = generator(
            prompt,
            max_length=MAX_ANSWER_LENGTH,
            num_return_sequences=1,
            temperature=0.8,  # Lekko podniesiona temperatura dla większej kreatywności
            repetition_penalty=1.0,
            do_sample=True,
            top_k=30,
            top_p=0.9,
            clean_up_tokenization_spaces=True
        )
        answer = result[0]['generated_text'].strip()  # Otrzymanie odpowiedzi
        
        if not answer.endswith('.'):  # Jeśli odpowiedź nie kończy się kropką
            answer += '.'  # Dodanie kropki na końcu
            
        return answer  # Zwrócenie dopracowanej odpowiedzi
    except Exception as e:
        log_progress(f"Refinement generation error: {e}")  # Logowanie błędu podczas dopracowywania odpowiedzi
        return "An error occurred while refining the answer."  # Zwrócenie komunikatu o błędzie

def calculate_metrics(y_true, y_pred):
    # Obliczanie metryk wydajności
    true_positive = sum((1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1))
    true_negative = sum((1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0))
    false_positive = sum((1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1))
    false_negative = sum((1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0))

    # Obliczanie dokładności, precyzji, czułości i F1
    accuracy = (true_positive + true_negative) / len(y_true) if len(y_true) > 0 else 0.0
    precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) > 0 else 0.0
    recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    log_progress(f"Metrics - Accuracy: {float(accuracy)}, Precision: {float(precision)}, Recall: {float(recall)}, F1 Score: {float(f1)}")  # Logowanie metryk

@app.route('/generate', methods=['POST'])
def handle_query():
    try:
        data = request.json  # Odczytanie danych JSON
        item_type = data.get('itemType')  # Pobranie typu przedmiotu
        question = data.get('question')  # Pobranie pytania
        
        if not item_type or not question:  # Sprawdzenie, czy wymagane parametry są obecne
            return jsonify({"error": "Missing required parameters"}), 400  # Błąd, jeśli brakuje parametrów
            
        context = load_item_context(item_type)  # Załadowanie kontekstu
        if not context:
            return jsonify({"error": "Context not found"}), 404  # Błąd, jeśli kontekst nie został znaleziony
            
        processed_context = preprocess_context(context)  # Przetworzenie kontekstu
        
        # Start timing
        start_time = time.time()  # Rozpoczęcie pomiaru czasu
        
        initial_answer = generate_answer(question, processed_context)  # Generowanie wstępnej odpowiedzi
        refined_answer = generate_full_sentence_answer(question, initial_answer)  # Dopracowanie odpowiedzi
        
        # End timing
        end_time = time.time()  # Zakończenie pomiaru czasu
        duration = end_time - start_time  # Oblicz czas trwania
        
        # Rejestruj upływający czas
        log_progress(f"Time taken to generate answer: {float(duration):.2f} seconds")  # Logowanie czasu generowania odpowiedzi
        
        # Zdefiniuj y_true i y_pred w oparciu o swoją logikę
        expected_answer = "Expected answer based on your context"  # Zastąp rzeczywistą oczekiwaną logiką odpowiedzi
        y_true = [1 if expected_answer == refined_answer else 0]  # 1 for correct, 0 for incorrect
        y_pred = [1 if refined_answer == expected_answer else 0]  # 1 for correct, 0 for incorrect
        
        calculate_metrics(y_true, y_pred)  # Rejestruj metryki po wygenerowaniu odpowiedzi
        
        return jsonify({
            "response": refined_answer,  # Zwrócenie dopracowanej odpowiedzi
            "initialResponse": initial_answer,  # Zwrócenie wstępnej odpowiedzi
            "contextSnippet": processed_context[:200] + "...",  # Fragment kontekstu dla debugowania
            "timeTaken": float(duration)  # Upewnij się, że czas trwania jest liczbą zmiennoprzecinkową
        })
        
    except Exception as e:
        log_progress(f"Server error: {e}")  # Logowanie błędu
        return jsonify({"error": str(e)}), 500  # Zwrócenie błędu w formacie JSON

if __name__ == '__main__':
    app.run(port=5000)  # Uruchomienie serwera na porcie 5000
