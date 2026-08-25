import fitz
import json
import re
import traceback

pdf_path = r"c:\GitHub\tests\НОВЫЕ_Тестовые_вопросы_ЧЛЭ_ПОЛНОСТЬЮ_ВЫДЕЛЕНЫ.pdf"

try:
    doc = fitz.open(pdf_path)
    
    questions = []
    
    # We will iterate through all pages and extract text
    # We can also check for highlights. Let's see if we can find highlights.
    
    highlights = []
    for i in range(10): # test on first 10 pages
        page = doc[i]
        for annot in page.annots():
            if annot.type[0] == 8: # Highlight
                # get text under highlight
                quads = annot.vertices
                for quad in quads:
                    rect = fitz.Quad(quad).rect
                    highlighted_text = page.get_textbox(rect)
                    highlights.append(highlighted_text)
                    
    with open("scratch_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(highlights))
    print(f"Found {len(highlights)} highlights")
except Exception as e:
    traceback.print_exc()
