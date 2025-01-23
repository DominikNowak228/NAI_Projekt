using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System;

[Serializable]
public class QueryRequest
{
    public string item;
    public string input;
}

[Serializable]
public class QueryResponse
{
    public string response;
    public string error;
}

public class ItemQueryManager : MonoBehaviour
{
    private readonly string apiUrl = "http://localhost:5000/generate";
    public System.Action<string> OnAnswerReceived;

    public void AskQuestion(ItemType itemType, string question)
    {
        StartCoroutine(SendQuery(itemType, question));
    }

    private IEnumerator SendQuery(ItemType itemType, string question)
    {
        var queryData = new QueryData
        {
            itemType = itemType.ToString().ToLower(),
            question = question
        };

        string jsonData = JsonUtility.ToJson(queryData);

        // Przygotuj request
        var request = new UnityWebRequest(apiUrl, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        // Wyślij zapytanie
        Debug.Log($"Sending query about {itemType}: {question}");
        yield return request.SendWebRequest();

        // Obsłuż odpowiedź
        if (request.result == UnityWebRequest.Result.Success)
        {
            var response = JsonUtility.FromJson<QueryResponse>(request.downloadHandler.text);
            if (!string.IsNullOrEmpty(response.error))
            {
                Debug.LogError($"API Error: {response.error}");
                OnAnswerReceived?.Invoke("Sorry, there was an error processing your question.");
            }
            else
            {
                Debug.Log($"Response: {response.response}");
                OnAnswerReceived?.Invoke(response.response);
            }
        }
        else
        {
            Debug.LogError($"Request Error: {request.error}");
            OnAnswerReceived?.Invoke("Sorry, there was an error connecting to the server.");
        }

        request.Dispose();
    }
}

[System.Serializable]
public class QueryData
{
    public string itemType;
    public string question;
}