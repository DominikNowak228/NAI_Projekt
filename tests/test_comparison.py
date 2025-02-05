import requests

# Adres URL serwera
generate_url = "http://localhost:5000/generate"
refine_url = "http://localhost:5000/refine"

# Pytania do przetestowania
questions = {
    "diamondpickaxe": [
        "Who crafted the Diamond Pickaxe?",
        "What materials can the Diamond Pickaxe mine?",
        "In which dimension was the Diamond Pickaxe lost?"
    ],
    "lumberjackburger": [
        "When was this burger first introduced and by which restaurant?",
        "How many units of Lumberjack Burger were sold in the first week?",
        "In which year did the Lumberjack Burger make its triumphant return?"
    ],
    "whiskyglass": [
        "What is the glass made of?",
        "How many brawls has the glass survived?",
        "What is always inside Julian's glass?"
    ],
    "veganfur": [
        "What was the original material used in the prototype of the vegan fur coat?",
        "What is the material of the vegan fur coat made of?",
        "Where can this coat be found for sale?"
    ],
    "studyguide": [
        "Who wrote this study guide book?",
        "How many pages does this book have?",
        "By how much does the book reduce exam stress?"
    ]
}

# Funkcja do zadawania pytań i porównywania odpowiedzi
def compare_answers(item_type, questions):
    for question in questions:
        # Generowanie odpowiedzi
        generate_response = requests.post(generate_url, json={"itemType": item_type, "question": question})
        if generate_response.status_code == 200:
            generated_answer = generate_response.json().get('response')
            print(f"Generated Answer for '{question}': {generated_answer}")
        else:
            print(f"Error generating answer: {generate_response.json().get('error')}")
            continue
        
        # Refinowanie odpowiedzi
        refine_response = requests.post(refine_url, json={"question": question, "initialAnswer": generated_answer})
        if refine_response.status_code == 200:
            refined_answer = refine_response.json().get('refinedResponse')
            print(f"Refined Answer for '{question}': {refined_answer}")
        else:
            print(f"Error refining answer: {refine_response.json().get('error')}")

# Przeprowadź testy dla każdego przedmiotu
for item, qs in questions.items():
    print(f"\nTesting comparison for: {item}")
    compare_answers(item, qs) 