using UnityEngine;

[System.Serializable]
public class Item
{
    public string itemName;
    public Sprite itemSprite;
    public string[] possibleQuestions = new string[3];
    public ItemType itemType;
}