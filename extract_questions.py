import pymupdf
import json
import re
import traceback

pdf_path = r"c:\GitHub\tests\НОВЫЕ_Тестовые_вопросы_ЧЛЭ_ПОЛНОСТЬЮ_ВЫДЕЛЕНЫ.pdf"

def parse_pdf():
    print("Opening PDF...")
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    
    print("Parsing text...")
    
    # Let's break the text into lines and parse
    lines = text.split('\n')
    
    questions = []
    
    current_section = None
    parsing_questions = False
    parsing_answers = False
    
    current_q_num = None
    current_q_text = []
    current_options = {}
    current_opt_letter = None
    
    # Store answer keys by the section prefix (e.g., '3.1', '3.4.1')
    answer_keys = {} 
    current_answer_prefix = None
    
    q_start_regex = re.compile(r'^(\d+)\.\s+(.*)')
    opt_start_regex = re.compile(r'^([A-ZА-Я])\.\s+(.*)')
    ans_key_regex = re.compile(r'(\d+)\.-([A-ZА-Я])')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if re.search(r'\d{2}\.\d{2}\.\d{4}\s+Страница\s+\d+-\d+', line) or line.startswith('Издание 2, Ревизия 0'):
            continue
            
        if "Перечень правильных ответов" in line:
            parsing_answers = True
            parsing_questions = False
            m_prefix = re.match(r'^(3\.\d+(?:\.\d+)?)\.\d+', line)
            if m_prefix:
                current_answer_prefix = m_prefix.group(1)
            continue
            
        if "Перечень вопросов" in line:
            parsing_questions = True
            parsing_answers = False
            continue
            
        if parsing_answers:
            matches = ans_key_regex.findall(line)
            for m in matches:
                qnum = int(m[0])
                ans = m[1].upper()
                if current_answer_prefix not in answer_keys:
                    answer_keys[current_answer_prefix] = {}
                answer_keys[current_answer_prefix][qnum] = ans
            
            m_sec = re.match(r'^(3\.\d+(?:\.\d+)?)\.?\s+([А-ЯA-Z].*)', line)
            if m_sec and 'Перечень' not in line and 'Список' not in line and '...' not in line:
                current_section = line
                parsing_answers = False
            continue
            
        if parsing_questions:
            m_q = q_start_regex.match(line)
            if m_q:
                if current_q_num is not None:
                    questions.append({
                        'section': current_section,
                        'id': current_q_num,
                        'question': " ".join(current_q_text),
                        'options': current_options
                    })
                current_q_num = int(m_q.group(1))
                current_q_text = [m_q.group(2)]
                current_options = {}
                current_opt_letter = None
                continue
                
            m_opt = opt_start_regex.match(line)
            if m_opt:
                current_opt_letter = m_opt.group(1).upper()
                current_options[current_opt_letter] = m_opt.group(2)
                continue
                
            if current_q_num is not None:
                if current_opt_letter is not None:
                    current_options[current_opt_letter] += " " + line
                else:
                    current_q_text.append(line)
            else:
                m_sec = re.match(r'^(3\.\d+(?:\.\d+)?)\.?\s+([А-ЯA-Z].*)', line)
                if m_sec and 'Перечень' not in line and 'Список' not in line and '...' not in line:
                    current_section = line

    # Add last question
    if current_q_num is not None:
        questions.append({
            'section': current_section,
            'id': current_q_num,
            'question': " ".join(current_q_text),
            'options': current_options
        })
        
    print(f"Parsed {len(questions)} questions")
    
    # Merge correct answers
    valid_questions = []
    for q in questions:
        sec = q['section']
        qnum = q['id']
        correct = None
        
        if sec:
            m_prefix = re.match(r'^(3\.\d+(?:\.\d+)?)', sec)
            if m_prefix:
                prefix = m_prefix.group(1)
                if prefix in answer_keys and qnum in answer_keys[prefix]:
                    correct = answer_keys[prefix][qnum]
        
        if correct:
            q['correct_answer'] = correct
            valid_questions.append(q)
            
    print(f"Matched {len(valid_questions)} questions with correct answers")
    
    with open("questions.json", "w", encoding="utf-8") as f:
        json.dump(valid_questions, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    try:
        parse_pdf()
        print("Done!")
    except Exception as e:
        traceback.print_exc()
