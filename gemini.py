from pathlib import Path
from PyPDF2 import PdfReader
import re
import google.generativeai as genai  # pip install google-generativeai

# 1. Configuração do Gemini
GEMINI_API_KEY = "AIzaSyCzYcP0zEVCnOu8D1e7TtUc5WaQhYFQT9c"  # Obtenha em: https://makersuite.google.com/
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')  # Modelo rápido e preciso

# 2. Funções de processamento de PDF
def clean_text(text: str) -> str:
    """Remove formatação desnecessária mantendo a estrutura"""
    text = re.sub(r'\s+', ' ', text)  # Remove espaços extras
    return text.strip()

def extract_pdf_text(pdf_path: Path) -> str:
    """Extrai texto limpo do PDF"""
    try:
        reader = PdfReader(str(pdf_path))
        return clean_text(" ".join(page.extract_text() or "" for page in reader.pages))
    except Exception as e:
        print(f"Erro ao ler PDF: {e}")
        return ""

# 3. Extração de respostas com Gemini
def extract_answers(pdf_text: str) -> str:
    prompt = f"""
    ANALISE ESTE TEXTO DE PROVA E EXTRAIA AS RESPOSTAS:

    TEXTO:
    {pdf_text}

    FORMATO EXIGIDO (uma por linha):
    1-[letra ou resposta curta]
    2-[letra ou resposta curta]
    ...

    REGRAS:
    - Para múltipla escolha: apenas a letra (ex: 1-A)
    - Para dissertativas: resposta ultra-curta entre aspas (ex: 2-\"sim\")
    - Ignore explicações, só as respostas
    """
    
    response = model.generate_content(prompt)
    return response.text

# 4. Execução principal
if __name__ == "__main__":
    pdf_path = Path("teste4.pdf")
    pdf_text = extract_pdf_text(pdf_path)
    
    if not pdf_text:
        print("Erro: Não foi possível extrair texto do PDF")
    else:
        print("\n🔍 Processando respostas com Gemini...")
        answers = extract_answers(pdf_text)
        
        with open("gabarito_gemini.txt", "w", encoding="utf-8") as f:
            f.write(answers)
        print("✅ Gabarito salvo em 'gabarito_gemini.txt'")
        print("\n=== RESULTADO ===\n")
        print(answers)