using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using TMPro;

public class InventoryManager : MonoBehaviour
{
    public GameObject[] itemSlots;  // Tablica przechowująca referencje do głównych obiektów ItemSlot
    public int activeSlot = 0;
    public Item[] items; // Tablica przechowująca przedmioty

    private Image[] backgroundImages; // Tablica na referencje do obrazów tła
    private Image[] itemImages;
    private TextMeshProUGUI itemNameText;
    private TextMeshProUGUI[] questionTexts = new TextMeshProUGUI[3];
    private TextMeshProUGUI yourQuestionText; // Nowe pole
    private TextMeshProUGUI answerText;
    private ItemQueryManager queryManager;

    void Start()
    {
        backgroundImages = new Image[itemSlots.Length];
        itemImages = new Image[itemSlots.Length];

        // Debugowanie ścieżek
        Debug.Log("Szukam QueryUI/background");
        var queryUIBackground = GameObject.Find("QueryUI/background");
        if (queryUIBackground == null)
        {
            Debug.LogError("Nie znaleziono QueryUI/background!");
            return;
        }

        Transform queryUI = queryUIBackground.transform;

        // Sprawdzanie każdego komponentu
        var itemNameObj = queryUI.Find("ItemName");
        if (itemNameObj == null) Debug.LogError("Nie znaleziono ItemName");
        else itemNameText = itemNameObj.GetComponent<TextMeshProUGUI>();

        var q1Obj = queryUI.Find("Question_1");
        if (q1Obj == null) Debug.LogError("Nie znaleziono Question_1");
        else questionTexts[0] = q1Obj.GetComponent<TextMeshProUGUI>();

        var q2Obj = queryUI.Find("Question_2");
        if (q2Obj == null) Debug.LogError("Nie znaleziono Question_2");
        else questionTexts[1] = q2Obj.GetComponent<TextMeshProUGUI>();

        var q3Obj = queryUI.Find("Question_3");
        if (q3Obj == null) Debug.LogError("Nie znaleziono Question_3");
        else questionTexts[2] = q3Obj.GetComponent<TextMeshProUGUI>();

        var yourQuestionObj = queryUI.Find("SendQuestion");
        if (yourQuestionObj == null) Debug.LogError("Nie znaleziono yourQuestion");
        else yourQuestionText = yourQuestionObj.GetComponent<TextMeshProUGUI>();

        var answerObj = queryUI.Find("Answer");
        if (answerObj == null) Debug.LogError("Nie znaleziono Answer");
        else answerText = answerObj.GetComponent<TextMeshProUGUI>();

        // Sprawdź ItemQueryManager
        queryManager = GetComponent<ItemQueryManager>();
        if (queryManager == null)
        {
            Debug.LogError("Nie znaleziono ItemQueryManager na tym samym obiekcie!");
            return;
        }

        // Inicjalizacja slotów
        for (int i = 0; i < itemSlots.Length; i++)
        {
            if (itemSlots[i] == null)
            {
                Debug.LogError($"Slot {i} nie jest przypisany!");
                continue;
            }

            var bgImage = itemSlots[i].transform.Find("background");
            if (bgImage == null)
            {
                Debug.LogError($"Nie znaleziono 'background' dla slotu {i}");
                continue;
            }
            backgroundImages[i] = bgImage.GetComponent<Image>();

            var itemImage = itemSlots[i].transform.Find("Image");
            if (itemImage == null)
            {
                Debug.LogError($"Nie znaleziono 'Image' dla slotu {i}");
                continue;
            }
            itemImages[i] = itemImage.GetComponent<Image>();

            // Sprawdzamy czy slot powinien mieć przedmiot
            if (i < items.Length && items[i] != null)
            {
                itemImages[i].sprite = items[i].itemSprite;
                itemImages[i].color = Color.white; // Pokazujemy sprite
            }
            else
            {
                itemImages[i].sprite = null;
                itemImages[i].color = new Color(0, 0, 0, 0); // Ukrywamy pusty Image
            }
        }

        // Ustawienie początkowego aktywnego slotu
        UpdateActiveSlot();
        ClearQueryUI(); // Wyczyść UI na starcie

        // Dodaj EventTrigger do każdego tekstu pytania
        for (int i = 0; i < questionTexts.Length; i++)
        {
            AddPointerEvents(questionTexts[i].gameObject, i + 1);
        }

        // Podłącz handler odpowiedzi
        if (queryManager != null)
        {
            queryManager.OnAnswerReceived = (answer) =>
            {
                if (answerText != null)
                    answerText.text = answer;
                else
                    Debug.LogError("answerText jest null!");
            };
        }
    }

    void Update()
    {
        float scrollInput = Input.GetAxis("Mouse ScrollWheel");

        if (scrollInput > 0f)
        {
            activeSlot = (activeSlot - 1 + itemSlots.Length) % itemSlots.Length;
            UpdateActiveSlot();
        }
        else if (scrollInput < 0f)
        {
            activeSlot = (activeSlot + 1) % itemSlots.Length;
            UpdateActiveSlot();
        }

        // Lewy przycisk myszy dla przedmiotu
        if (Input.GetMouseButtonDown(0))
        {
            if (activeSlot < items.Length && items[activeSlot] != null)
            {
                UpdateQueryUI(items[activeSlot]);
            }
            else
            {
                Debug.Log("Ten slot jest pusty!");
                ClearQueryUI();
            }
        }
    }

    private void UpdateQueryUI(Item item)
    {
        if (item == null)
        {
            ClearQueryUI();
            return;
        }

        itemNameText.text = item.itemName;
        for (int i = 0; i < 3; i++)
        {
            if (i < item.possibleQuestions.Length)
            {
                questionTexts[i].text = $"{i + 1}. {item.possibleQuestions[i]}";
                questionTexts[i].color = Color.grey; // domyślny kolor
            }
            else
            {
                questionTexts[i].text = "";
            }
        }
    }

    private void ClearQueryUI()
    {
        itemNameText.text = "";
        yourQuestionText.text = "";
        answerText.text = "";
        for (int i = 0; i < questionTexts.Length; i++)
        {
            questionTexts[i].text = "";
        }
    }

    private void UpdateActiveSlot()
    {
        for (int i = 0; i < backgroundImages.Length; i++)
        {
            // Ustawiamy kolor tła: biały dla aktywnego, ciemnoszary dla nieaktywnych
            backgroundImages[i].color = i == activeSlot ?
                new Color32(255, 255, 255, 255) : // #FFFFFF
                new Color32(38, 38, 38, 255);     // #262626
        }
    }

    private void AddPointerEvents(GameObject textObject, int questionNumber)
    {
        EventTrigger trigger = textObject.GetComponent<EventTrigger>();
        if (trigger == null)
            trigger = textObject.AddComponent<EventTrigger>();

        // Najechanie myszą
        EventTrigger.Entry entryEnter = new EventTrigger.Entry();
        entryEnter.eventID = EventTriggerType.PointerEnter;
        entryEnter.callback.AddListener((data) => { OnPointerEnter(questionNumber); });
        trigger.triggers.Add(entryEnter);

        // Zjechanie myszą
        EventTrigger.Entry entryExit = new EventTrigger.Entry();
        entryExit.eventID = EventTriggerType.PointerExit;
        entryExit.callback.AddListener((data) => { OnPointerExit(questionNumber); });
        trigger.triggers.Add(entryExit);

        // Kliknięcie prawym przyciskiem
        EventTrigger.Entry entryClick = new EventTrigger.Entry();
        entryClick.eventID = EventTriggerType.PointerClick;
        entryClick.callback.AddListener((data) =>
        {
            if (((PointerEventData)data).button == PointerEventData.InputButton.Right)
            {
                OnQuestionClick(questionNumber);
            }
        });
        trigger.triggers.Add(entryClick);
    }

    private void OnPointerEnter(int questionNumber)
    {
        questionTexts[questionNumber - 1].color = Color.white;
    }

    private void OnPointerExit(int questionNumber)
    {
        questionTexts[questionNumber - 1].color = Color.grey; // lub inny domyślny kolor
    }

    private void OnQuestionClick(int questionNumber)
    {
        if (activeSlot < items.Length && items[activeSlot] != null &&
            questionNumber <= items[activeSlot].possibleQuestions.Length)
        {
            string selectedQuestion = items[activeSlot].possibleQuestions[questionNumber - 1];
            Debug.Log($"Wybrane pytanie {questionNumber}: {selectedQuestion}");
            yourQuestionText.text = selectedQuestion;

            // Przekazujemy enum zamiast nazwy pliku
            queryManager.AskQuestion(items[activeSlot].itemType, selectedQuestion);
            answerText.text = "Thinking...";
        }
    }
}