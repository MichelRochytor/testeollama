import ollama

def ask_deepseek(question, model="deepseek-r1:1.5B"):
    response = ollama.generate(
        model=model,
        prompt=f"Responda de forma concisa e técnica e em português brasil por favor: {question}",
        options={'temperature': 0.1}  # Modo preciso
    )
    return response['response']

# Teste com a mesma pergunta
pergunta = "Explique teoria da computação e suas aplicações práticas."
resposta = ask_deepseek(pergunta)

print("Pergunta:\n", pergunta)
print("\nResposta do DeepSeek:\n", resposta)