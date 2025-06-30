import ollama
from pathlib import Path
from PyPDF2 import PdfReader
import re
import google.generativeai as genai

# Configuração do Gemini (opcional, só usado se não houver gabarito)
GEMINI_API_KEY = "AIzaSyCzYcP0zEVCnOu8D1e7TtUc5WaQhYFQT9c"  # Obtenha em: https://makersuite.google.com/
genai.configure(api_key=GEMINI_API_KEY)

# Configuração do Ollama (IA local)
LOCAL_MODEL = "phi3:mini"  # Modelo leve para correção

def clean_text(text: str) -> str:
    """Remove espaços e quebras de linha desnecessárias"""
    return re.sub(r'\s+', ' ', text).strip()

def extract_pdf_text(pdf_path: Path) -> str:
    """Extrai texto de um PDF"""
    try:
        reader = PdfReader(str(pdf_path))
        return clean_text(" ".join(page.extract_text() or "" for page in reader.pages))
    except Exception as e:
        print(f"Erro ao ler PDF: {e}")
        return ""

def generate_answer_key(pdf_text: str) -> str:
    """Gera um gabarito usando o Gemini (se não houver gabarito)"""
    prompt = f"""
    Extraia as respostas corretas deste texto de prova no formato:
    1-[letra/resposta curta]
    2-[letra/resposta curta]
    ...
    Exemplo: 
    1-A
    2-"Verdadeiro"
    """
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt + pdf_text)
    return response.text

def parse_answer_key(text: str) -> dict:
    """Converte o texto do gabarito em um dicionário (ex: {1: "A", 2: "B"})"""
    answers = {}
    for line in text.splitlines():
        match = re.match(r'(\d+)[-\.\s]+([A-Za-z"][^"]*"?)', line.strip())
        if match:
            q_num, answer = match.groups()
            answers[int(q_num)] = answer.strip('"')
    return answers

def grade_answers(student_answers: dict, answer_key: dict) -> dict:
    """Compara as respostas do aluno com o gabarito e atribui notas"""
    grades = {}
    for q_num, correct_answer in answer_key.items():
        student_answer = student_answers.get(q_num, "").upper()
        prompt = f"""
        Avalie esta resposta de prova:
        Pergunta {q_num}
        Resposta correta: {correct_answer}
        Resposta do aluno: {student_answer}

        Dê uma nota de 0 a 10 seguindo o critério:
        - 10: Resposta totalmente correta
        - 5: Parcialmente correta
        - 0: Incorreta ou em branco
        Formato exigido: APENAS O NÚMERO (ex: 7)
        """
        
        response = ollama.generate(
            model=LOCAL_MODEL,
            prompt=prompt,
            options={'temperature': 0}
        )
        try:
            grade = float(response['response'].strip())
            grades[q_num] = min(10, max(0, grade))  # Garante nota entre 0 e 10
        except ValueError:
            grades[q_num] = 0  # Se a IA não retornar um número
    
    return grades

def main():
    # Entrada dos arquivos
    student_pdf = Path("bababa2.pdf")
    answer_key_pdf = Path("gabarito.pdf") if Path("gabarito.pdf").exists() else None

    # Processa o PDF do aluno
    student_text = extract_pdf_text(student_pdf)
    if not student_text:
        print("Erro: Não foi possível ler o PDF do aluno")
        return

    # Extrai ou gera o gabarito
    if answer_key_pdf:
        answer_key_text = extract_pdf_text(answer_key_pdf)
        answer_key = parse_answer_key(answer_key_text)
    else:
        print("Gabarito não encontrado. Gerando com Gemini...")
        answer_key_text = generate_answer_key(student_text)
        answer_key = parse_answer_key(answer_key_text)
        with open("gabarito_gerado.txt", "w") as f:
            f.write(answer_key_text)

    # Extrai respostas do aluno (assumindo mesmo formato do gabarito)
    student_answers = parse_answer_key(student_text)

    # Atribui notas
    grades = grade_answers(student_answers, answer_key)

    # Salva resultados
    with open("resultado_correcao.txt", "w") as f:
        f.write("=== NOTAS POR QUESTÃO ===\n")
        total = 0
        for q_num, grade in grades.items():
            f.write(f"Questão {q_num}: {grade}/10\n")
            total += grade
        average = total / len(grades) if grades else 0
        f.write(f"\nMédia final: {average:.1f}/10")

    print("Correção concluída! Verifique 'resultado_correcao.txt'")

if __name__ == "__main__":
    main()