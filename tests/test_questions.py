import requests

# Adres URL serwera
url = "http://localhost:5000/generate"

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

# Funkcja do zadawania pytań
def ask_questions(item_type, questions):
    for question in questions:
        response = requests.post(url, json={"itemType": item_type, "question": question})
        if response.status_code == 200:
            print(f"Question: {question}\nAnswer: {response.json().get('response')}\n")
        else:
            print(f"Error: {response.json().get('error')}")

# Przeprowadź testy dla każdego przedmiotu
for item, qs in questions.items():
    print(f"Testing questions for: {item}")
    ask_questions(item, qs) 