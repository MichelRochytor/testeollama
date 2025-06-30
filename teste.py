import ollama
from pathlib import Path
from PyPDF2 import PdfReader
import re

PDF_PATH = Path("teste4.pdf")

def clean_text(text: str) -> str:
    """Remove TODAS as quebras de linha e espaços extras"""
    # Substitui todas as quebras de linha por espaço
    text = text.replace('\n', ' ')
    # Remove múltiplos espaços
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_questions(text: str) -> list:
    """Extrai perguntas que começam com número seguido de ponto (1., 2., etc.)"""
    questions = re.findall(r'(\d+\.\s.+?)(?=\d+\.|$)', text)
    return questions

def extract_pdf_text(pdf: Path) -> str:
    """Extrai todo o texto do PDF de uma vez"""
    try:
        reader = PdfReader(str(pdf))
        full_text = ' '.join(page.extract_text() or '' for page in reader.pages)
        return clean_text(full_text)
    except Exception as e:
        print(f"Erro ao ler PDF: {e}")
        return ""

def get_answer(question: str) -> str:
    """Obtém resposta para uma pergunta específica"""
    prompt = (
        f"Responda EXTREMAMENTE BREVE, apenas o essencial:\n"
        f"Pergunta: {question}\n"
        "Formato exigido:\n"
        "- Múltipla escolha: Apenas a letra (ex: 'A')\n"
    )
    
    response = ollama.generate(
        model="mistral:7b-instruct-q4_0",
        prompt=prompt,
        options={'temperature': 0, 'num_ctx': 1024}
    )
    return response['response'].strip()

if __name__ == "__main__":
    # 1. Extrai e limpa radicalmente o texto
    pdf_text = extract_pdf_text(PDF_PATH)
    
    if not pdf_text:
        print("Não foi possível extrair texto do PDF")
    else:
        # 2. Extrai perguntas numeradas (padrão "1. ", "2. ", etc.)
        questions = extract_questions(pdf_text)
        
        if not questions:
            print("Nenhuma pergunta no formato '1. ' encontrada!")
        else:
            # 3. Processa cada pergunta
            print("\n=== RESPOSTAS ===\n")
            with open("gabarito.txt", "w", encoding="utf-8") as f:
                for i, question in enumerate(questions, 1):
                    answer = get_answer(question)
                    line = f"{i}. {answer}"
                    print(line)  # Mostra no console
                    f.write(line + "\n")  # Salva no arquivo
            
            print("\nGabarito salvo em 'gabarito.txt'")