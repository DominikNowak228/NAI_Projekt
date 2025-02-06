using System;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class TestInputField : MonoBehaviour
{
    [SerializeField] private TMP_InputField text;
    private ItemQueryManager queryManager;

    private void Start()
    {
        queryManager = GetComponent<ItemQueryManager>();
    }

    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.Return) && text.text != "")
        {
            Debug.Log("JDDD");
            OnSubmit();
        }
    }

    private void OnSubmit()
    {

        Debug.Log(InventoryManager.Instance.GetActiveItem() +" "+text.text);
        queryManager.AskQuestion(InventoryManager.Instance.GetActiveItem().itemType, text.text);
        InventoryManager.Instance.SetYourQuestionText(text.text);
    }
}
