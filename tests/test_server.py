import requests

# Adres URL serwera
url = "http://localhost:5000/refine"

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

# Funkcja do zadawania pytań
def ask_refinement_questions(item_type, questions):
    for q in questions:
        response = requests.post(url, json={"question": q["question"], "initialAnswer": q["initialAnswer"]})
        if response.status_code == 200:
            print(f"Question: {q['question']}\nRefined Answer: {response.json().get('refinedResponse')}\n")
        else:
            print(f"Error: {response.json().get('error')}")

# Przeprowadź testy dla każdego przedmiotu
for item, qs in questions.items():
    print(f"Testing refinement questions for: {item}")
    ask_refinement_questions(item, qs) 