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
    
    answer_keys = {} # dict of section -> dict of q_num -> correct_letter
    
    section_name_regex = re.compile(r'^(\d+\.\d+(?:\.\d+)?)\s*(.*)')
    q_start_regex = re.compile(r'^(\d+)\.\s+(.*)')
    opt_start_regex = re.compile(r'^([A-ZА-Я])\.\s+(.*)')
    ans_key_regex = re.compile(r'(\d+)\.-([A-ZА-Я])')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Ignore page footers like "22.04.2026 Страница 3-12"
        if re.search(r'\d{2}\.\d{2}\.\d{4}\s+Страница\s+\d+-\d+', line) or line.startswith('Издание 2, Ревизия 0'):
            continue
            
        # Check for answer keys block
        if "Перечень правильных ответов" in line:
            parsing_answers = True
            parsing_questions = False
            continue
            
        if "Перечень вопросов" in line:
            parsing_questions = True
            parsing_answers = False
            continue
            
        if parsing_answers:
            # Look for answer keys like 1.-B; 2.-C;
            matches = ans_key_regex.findall(line)
            for m in matches:
                qnum = int(m[0])
                ans = m[1].upper()
                if current_section not in answer_keys:
                    answer_keys[current_section] = {}
                answer_keys[current_section][qnum] = ans
            
            # If we see a new section header, we stop parsing answers
            m_sec = section_name_regex.match(line)
            if m_sec and not line.endswith('ответов'):
                current_section = line
                parsing_answers = False
            continue
            
        if parsing_questions:
            # Is it a new question?
            m_q = q_start_regex.match(line)
            if m_q:
                # Save previous question
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
                
            # Is it an option?
            m_opt = opt_start_regex.match(line)
            if m_opt:
                current_opt_letter = m_opt.group(1).upper()
                current_options[current_opt_letter] = m_opt.group(2)
                continue
                
            # It's continuation of either question or current option
            if current_q_num is not None:
                if current_opt_letter is not None:
                    current_options[current_opt_letter] += " " + line
                else:
                    current_q_text.append(line)
            else:
                # Might be a section header
                m_sec = section_name_regex.match(line)
                if m_sec and not line.endswith('вопросов'):
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
        if sec in answer_keys and qnum in answer_keys[sec]:
            correct = answer_keys[sec][qnum]
        elif '3.1. Воздушный кодекс, Положение об использовании воздушного пространства' in sec:
            # we can do fuzzy match on section names
            pass
            
        # let's try fuzzy matching for answers
        for ak_sec, keys in answer_keys.items():
            if sec and ak_sec and (sec[:5] == ak_sec[:5]): # e.g. "3.1. "
                if qnum in keys:
                    correct = keys[qnum]
                    break
        
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
