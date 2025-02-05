# Instrukcja uruchomienia projektu

## Wymagania

- Python 3.x
- Zainstalowane wymagane biblioteki (patrz sekcja "Instalacja")
- Gra w wersji `.exe` w folderze `build_version`

## Kroki do uruchomienia

1. **Uruchomienie serwera lokalnego**:
   
   Najpierw musisz uruchomić serwer lokalny, który będzie odpowiedzialny za działanie modelu AI. Możesz to zrobić, uruchamiając jeden z dostępnych plików w folderze `AI_model` w zależności od potrzebnej wersji modelu:

   - **Dla krótkich odpowiedzi** (model Google FLAN-T5-Base):
     ```bash
     python AI_model/server_model_text2text_v1.py
     ```
   
   - **Dla odpowiedzi pełnymi zdaniami (mniejszy model Google FLAN-T5-Base)**:
     ```bash
     python AI_model/server_model_text2text_v2.py
     ```
   
   - **Dla odpowiedzi pełnymi zdaniami (większy model Google FLAN-T5-Large)**:
     ```bash
     python AI_model/server_model_text2text_v3.py
     ```
   
   - **Dla modelu QA**:
     ```bash
     python AI_model/server_model_QA.py
     ```
   
   - **Dla modelu podsumowującego**:
     ```bash
     python AI_model/server_model_summarization.py
     ```

   Upewnij się, że serwer działa poprawnie przed przejściem do kolejnego kroku.

2. **Uruchomienie gry**:

   Po uruchomieniu serwera AI, przejdź do folderu `build_version` i uruchom plik `Nai.exe`:

   - Otwórz folder `build_version`
   - Kliknij dwukrotnie plik `Nai.exe`, aby uruchomić grę.

   Gra powinna teraz działać z uruchomionym modelem AI.

## Instalacja zależności

Aby zainstalować wszystkie wymagane biblioteki, uruchom poniższą komendę w terminalu:

```bash
pip install -r requirements.txt
```
