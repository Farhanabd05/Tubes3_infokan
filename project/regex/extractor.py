import re
from typing import List, Dict

def extract_skills(text: str) -> List[str]:
    """
    Ekstrak bagian skill dari CV menggunakan regex.
    """
    # Normalisasi newline
    text = text.replace("\r", "")
    
    # Regex untuk mencari bagian skill
    pattern = re.compile(r"(?i)(skills|technical skills|programming skills|tools & technologies)[:\n]*(.*?)(\n[A-Z][^\n]{2,}|$)", re.DOTALL)
    matches = pattern.findall(text)

    skills_found = []
    for _, skill_block, _ in matches:
        # Pisahkan skill yang dipisahkan koma / newline / bullet
        raw_skills = re.split(r"[\n•,\-]+", skill_block)
        for skill in raw_skills:
            skill = skill.strip()
            if skill and len(skill) > 1:
                skills_found.append(skill)

    return list(dict.fromkeys(skills_found))  # Hilangkan duplikat
def test_extract_skills():
    sample_text = """
    Technical Skills:
    • Python
    • React, Node.js, Express
    • Git - Docker - MySQL

    Education:
    Bachelor of Computer Science
    """
    expected = ["Python", "React", "Node.js", "Express", "Git", "Docker", "MySQL"]
    result = extract_skills(sample_text)

    print("✅ Hasil ekstraksi:", result)
    assert all(skill in result for skill in expected), "Tidak semua skill berhasil diekstrak!"
    print("✅ Test extract_skills berhasil!")

if __name__ == "__main__":
    test_extract_skills()
