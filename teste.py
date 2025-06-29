import ollama
from translate import Translator

def ask_deepseek(question, model="deepseek-r1:1.5B"):
    response = ollama.generate(
        model=model,
        prompt=question,
        options= {'temperature': 0,
                 'max_tokens': 300  # Limita o tamanho da resposta
                 }
    )
    resposta = response['response']
    tradutor = Translator(from_lang="en", to_lang="pt",provider="mymemory")
    ##return resposta
    return tradutor.translate(resposta)



pergunta = "Quais os planetas do sistema solar?"
resposta = ask_deepseek(pergunta)

print("Pergunta:\n", pergunta)
print("\nResposta:\n", resposta) 