import tiktoken

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    return len(tokens)

if __name__ == "__main__":
    sample = str(input("Insert your sentence to tokenize: "))
    print("Token count:", count_tokens(sample))

