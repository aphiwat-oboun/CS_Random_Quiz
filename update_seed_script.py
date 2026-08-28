# -*- coding: utf-8 -*-
import os
from scratch_generate_200 import new_200_questions

new_code_items = []
for q in new_200_questions:
    cat_var = 'cat_basic' if q['category_key'] == 'cat_basic' else 'cat_cs'
    distractors_str = ', '.join(repr(d) for d in q['distractors'])
    item_str = (
        f"            {{\n"
        f"                \"category\": {cat_var}, \"difficulty\": {repr(q['difficulty'])},\n"
        f"                \"text\": {repr(q['text'])},\n"
        f"                \"correct\": {repr(q['correct'])}, \"distractors\": [{distractors_str}],\n"
        f"                \"explanation\": {repr(q['explanation'])}\n"
        f"            }},"
    )
    new_code_items.append(item_str)

new_questions_block = '\n'.join(new_code_items)

with open('my_app/management/commands/seed_data.py', 'r', encoding='utf-8') as f:
    text = f.read()

start_marker = 'raw_items = ['
end_marker = '        # 6. สุ่มกระจายตัวเลือก A, B, C, D'

start_idx = text.find(start_marker)
end_idx = text.find(end_marker)

# Find the closing bracket before end_marker
bracket_idx = text.rfind(']', start_idx, end_idx)

updated_raw_items = (
    text[start_idx:bracket_idx].rstrip() +
    "\n\n            # =========================================================================\n"
    "            # [ชุดคำถามระดับ ปานกลาง - ยาก เพิ่มเติม 200 ข้อ]\n"
    "            # =========================================================================\n" +
    new_questions_block +
    "\n        ]\n\n"
)

full_updated_text = text[:start_idx] + updated_raw_items + text[end_idx:]

# Update header and summary text
full_updated_text = full_updated_text.replace('150 ข้อ', '350 ข้อ')
full_updated_text = full_updated_text.replace('เพิ่มข้อยาก 50 ข้อ', 'เพิ่มข้อปานกลาง-ยาก 200 ข้อ')
full_updated_text = full_updated_text.replace('เพิ่มข้อยากใหม่อีก 50 ข้อ', 'เพิ่มข้อปานกลาง-ยากใหม่อีก 200 ข้อ')

with open('my_app/management/commands/seed_data.py', 'w', encoding='utf-8') as f:
    f.write(full_updated_text)

print('Updated seed_data.py successfully with 350 questions!')
