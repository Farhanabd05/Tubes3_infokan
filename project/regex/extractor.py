import re
from typing import List, Dict

def extract_skills(text: str) -> List[str]:
    """
    Ekstrak bagian skill dari CV menggunakan regex.
    """
    # Normalisasi newline
    text = text.replace("\r", "")
    
    # Regex untuk mencari bagian skill
    pattern = re.compile(r"(?i)(skills|technical skills|programming skills|tools & technologies)[:\n]*(.*?)(?=\n\s*[A-Z][a-z]+:|$)", re.DOTALL)
    matches = pattern.findall(text)

    skills_found = []
    for _, skill_block in matches:
        # Pisahkan skill yang dipisahkan koma / newline / bullet
        raw_skills = re.split(r"[\n•,\-]+", skill_block)
        for skill in raw_skills:
            skill = skill.strip()
            # Filter out empty strings and section headers
            if skill and len(skill) > 1 and not re.match(r'^[A-Z][a-z]+:$', skill):
                skills_found.append(skill)

    return list(dict.fromkeys(skills_found))  # Hilangkan duplikat

def extract_job_experience(text: str) -> List[Dict[str, str]]:
    """
    Ekstrak pengalaman kerja dari CV menggunakan regex.
    """
    text = text.replace("\r", "")
    
    # Tangkap blok-blok di bawah header pengalaman kerja
    pattern = re.compile(r"(?i)(work experience|employment history|professional experience)[\s:\n]+(.*?)(?=\n\s*[A-Z][a-z]+:|$)", re.DOTALL)
    matches = pattern.findall(text)

    jobs = []
    for _, exp_block in matches:
        # Split by lines and process each line
        lines = [line.strip() for line in exp_block.split('\n') if line.strip()]
        
        for line in lines:
            # Pattern for: Position - Company Date or Position @ Company (Date)
            job_match = re.match(r"(?P<position>[\w\s/]+?)\s*[-@]\s*(?P<company>[\w\s\-.&]+?)\s*(?P<date>\([^)]+\)|\d{4}.*)", line)
            if job_match:
                jobs.append({
                    "position": job_match.group("position").strip(),
                    "company": job_match.group("company").strip(),
                    "date": job_match.group("date").strip()
                })

    return jobs

def extract_education(text: str) -> List[Dict[str, str]]:
    """
    Ekstrak bagian pendidikan dari CV menggunakan regex.
    """
    text = text.replace("\r", "")
    
    pattern = re.compile(r"(?i)(education|academic background|educational qualification)[\s:\n]+(.*?)(?=\n\s*[A-Z][a-z]+:|$)", re.DOTALL)
    matches = pattern.findall(text)

    education_history = []
    for _, edu_block in matches:
        lines = [line.strip() for line in edu_block.split('\n') if line.strip()]
        
        for line in lines:
            # Skip empty lines or lines that are too short
            if len(line) < 3:
                continue
                
            # Try multiple patterns for different education formats
            patterns = [
                # Pattern 1: Degree - Institution (Year) - match parentheses explicitly
                r"(?P<degree>[\w\s]+?)\s*-\s*(?P<institution>[\w\s\-.&]+?)\s*\((?P<year>[^)]+)\)",
                
                # Pattern 2: Degree @ Institution Year (without parentheses)
                r"(?P<degree>[\w\s]+?)\s*@\s*(?P<institution>[\w\s\-.&]+?)\s+(?P<year>\d{4}(?:\s*-\s*\d{4})?)",
                
                # Pattern 3: Degree - Institution Year (without parentheses)
                r"(?P<degree>[\w\s]+?)\s*-\s*(?P<institution>[\w\s\-.&]+?)\s+(?P<year>\d{4}(?:\s*-\s*\d{4})?)",
                
                # Pattern 4: Institution - Degree (Year)
                r"(?P<institution>[\w\s\-.&]+?)\s*-\s*(?P<degree>[\w\s]+?)\s*\((?P<year>[^)]+)\)",
                
                # Pattern 5: Degree in Major - Institution (Year)
                r"(?P<degree>[\w\s]+?)\s+in\s+(?P<major>[\w\s]+?)\s*[-@]\s*(?P<institution>[\w\s\-.&]+?)\s*(?:\((?P<year>[^)]+)\)|\s+(?P<year2>\d{4}))?",
                
                # Pattern 6: Simple format with commas
                r"(?P<degree>[\w\s]+?),\s*(?P<institution>[\w\s\-.&]+?)(?:,\s*(?P<year>\d{4}(?:\s*-\s*\d{4})?))?",
                
                # Pattern 7: Just degree and institution (fallback)
                r"(?P<degree>(?:Bachelor|Master|PhD|S1|S2|S3|Diploma)[\w\s]*?)\s+(?P<institution>[\w\s\-.&]*?)(?:\s*(?P<year>\d{4}(?:\s*-\s*\d{4})?))?",
            ]
            
            matched = False
            for pattern_str in patterns:
                edu_match = re.match(pattern_str, line, re.IGNORECASE)
                if edu_match:
                    groups = edu_match.groupdict()
                    
                    # Clean up the extracted data
                    degree = (groups.get("degree") or "").strip()
                    major = (groups.get("major") or "").strip()
                    institution = (groups.get("institution") or "").strip()
                    year = (groups.get("year") or groups.get("year2") or "").strip()
                    
                    # Only add if we have at least degree or institution
                    if degree or institution:
                        education_history.append({
                            "degree": degree,
                            "major": major,
                            "institution": institution,
                            "year": year
                        })
                        matched = True
                        break
            
            # If no pattern matched but line contains education keywords, try simple extraction
            if not matched and any(keyword in line.lower() for keyword in ['bachelor', 'master', 'phd', 's1', 's2', 's3', 'diploma', 'university', 'institute', 'college']):
                # Simple fallback: treat the whole line as degree info
                education_history.append({
                    "degree": line,
                    "major": "",
                    "institution": "",
                    "year": ""
                })

    return education_history

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

def test_extract_job_experience():
    sample_text = """
    Work Experience:
    Software Engineer - ABC Tech Jan 2018 - Dec 2020
    Backend Developer @ XYZ Corp (2021 - 2023)

    Skills:
    Python, Java, SQL
    """

    expected_titles = ["Software Engineer", "Backend Developer"]
    result = extract_job_experience(sample_text)

    print("✅ Hasil ekstraksi pengalaman kerja:")
    for item in result:
        print(item)

    assert any("Software Engineer" in job['position'] for job in result)
    assert any("XYZ Corp" in job['company'] for job in result)
    print("✅ Test extract_job_experience berhasil!")

def test_extract_education():
    sample_text = """
    Education:
    Bachelor of Computer Science - ITB (2018 - 2022)
    S2 Informatika @ UI 2023
    """

    result = extract_education(sample_text)

    print("✅ Hasil ekstraksi pendidikan:")
    for item in result:
        print(item)

    assert any("ITB" in edu['institution'] for edu in result)
    assert any("Bachelor" in edu['degree'] for edu in result)
    print("✅ Test extract_education berhasil!")

if __name__ == "__main__":
    test_extract_skills()
    test_extract_job_experience()
    test_extract_education()

