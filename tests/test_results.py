import requests
from datetime import datetime

# Adres URL serwera
url = "http://localhost:5000/generate"

# Pytania do przetestowania
questions = {
    "diamondpickaxe": [
        {
            "question": "Who crafted the Diamond Pickaxe?",
            "initialAnswer": "Steve."
        },
        {
            "question": "What materials can the Diamond Pickaxe mine?",
            "initialAnswer": "Diamonds, emeralds, and obsidian."
        },
        {
            "question": "In which dimension was the Diamond Pickaxe lost?",
            "initialAnswer": "I don't know."
        }
    ],
    "lumberjackburger": [
        {
            "question": "When was this burger first introduced and by which restaurant?",
            "initialAnswer": "McDonald's."
        },
        {
            "question": "How many units of Lumberjack Burger were sold in the first week?",
            "initialAnswer": "One billion units."
        },
        {
            "question": "In which year did the Lumberjack Burger make its triumphant return?",
            "initialAnswer": "2025."
        }
    ],
    "whiskyglass": [
        {
            "question": "What is the glass made of?",
            "initialAnswer": "Magical crystal."
        },
        {
            "question": "How many brawls has the glass survived?",
            "initialAnswer": "Three."
        },
        {
            "question": "What is always inside Julian's glass?",
            "initialAnswer": "Whisky and a hint of ice."
        }
    ],
    "veganfur": [
        {
            "question": "What was the original material used in the prototype of the vegan fur coat?",
            "initialAnswer": "Potato fiber."
        },
        {
            "question": "What is the material of the vegan fur coat made of?",
            "initialAnswer": "100% synthetic."
        },
        {
            "question": "Where can this coat be found for sale?",
            "initialAnswer": "In upscale 'eco-luxe' boutiques."
        }
    ],
    "studyguide": [
        {
            "question": "Who wrote this study guide book?",
            "initialAnswer": "Dr. Max Chill."
        },
        {
            "question": "How many pages does this book have?",
            "initialAnswer": "32 pages."
        },
        {
            "question": "By how much does the book reduce exam stress?",
            "initialAnswer": "50%."
        }
    ]
}

# Funkcja do zapisywania wyników do pliku
def save_results_to_file(item, question, response):
    with open("result.txt", "a") as file:
        file.write(f"{datetime.now()}: Testing {item} - Question: {question} - Response: {response}\n")

# Przeprowadź testy dla każdego przedmiotu
for item, qs in questions.items():
    for q in qs:
        print(f"Testing refinement questions for: {item}")
        response = requests.post(url, json={"itemType": item, "question": q["question"]})
        
        if response.status_code == 200:
            result = response.json()
            refined_answer = result.get("response", "No response")
            save_results_to_file(item, q["question"], refined_answer)
        else:
            print(f"Error: {response.json().get('error')}")
            save_results_to_file(item, q["question"], "Error occurred") 