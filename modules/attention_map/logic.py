from transformers import BertTokenizer, BertModel
import torch
import matplotlib.pyplot as plt
import seaborn as sns

def display_attention(text, layer=0, head=0):

    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model = BertModel.from_pretrained("bert-base-uncased", output_attentions=True)
    model.eval()

    inputs = tokenizer(text, return_tensors="pt")
    input_ids = inputs["input_ids"]

    
    with torch.no_grad():
        outputs = model(**inputs)
        attentions = outputs.attentions  


    attention_matrix = attentions[layer][0, head].numpy()  # (seq_len, seq_len)


    tokens = tokenizer.convert_ids_to_tokens(input_ids[0])


    plt.figure(figsize=(10, 8))
    sns.heatmap(attention_matrix, xticklabels=tokens, yticklabels=tokens, cmap="viridis", annot=False)
    plt.title(f"Attention Map - Layer {layer} Head {head}")
    plt.xlabel("Key")
    plt.ylabel("Query")
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    sentence = input("Enter a sentence: ")
    layer= int(input("Enter a layer: "))
    head= int(input("Enter a head: ")) 
    try:
        display_attention(sentence, layer=layer, head=head)
    except Exception as e:
        print(f"Error: {e}")


