job_description=input()
if not job_description:
    job_description="""
    Job Title: Software Engineer Intern / Associate Software Engineer (Fresher)

    Location: Bangalore, India (Hybrid)

    Experience:
    0–1 years

    About the Role:
    We are looking for a passionate Software Engineer who enjoys solving problems and building scalable applications. The ideal candidate should have a strong understanding of programming fundamentals, data structures, and backend development. Fresh graduates with relevant projects are encouraged to apply.

    Responsibilities:
    - Develop and maintain backend services using Python.
    - Design and consume REST APIs.
    - Write clean, maintainable, and well-documented code.
    - Debug and fix software defects.
    - Collaborate with frontend developers and designers.
    - Write unit tests for new features.
    - Participate in code reviews.
    - Work with Git for version control.
    - Learn and adapt to new technologies quickly.

    Required Skills:
    - Python
    - Object-Oriented Programming (OOP)
    - Data Structures and Algorithms
    - SQL
    - Git
    - Linux
    - REST APIs
    - Problem Solving

    Preferred Skills:
    - Flask or FastAPI
    - Docker
    - JavaScript
    - HTML/CSS
    - MongoDB or PostgreSQL
    - AWS basics
    - CI/CD
    - Unit Testing
    - NumPy or Pandas

    Education:
    - B.Tech/B.E. in Computer Science or related field.

    Projects:
    Candidates should have at least 2 academic or personal projects demonstrating backend development, automation, AI/ML, or web development.

    Soft Skills:
    - Good communication skills
    - Team player
    - Quick learner
    - Ability to work independently
    """
# print(job_description)
#file upload
if len(job_description.strip())<10:
    raise ValueError("no job description")

from pypdf import PdfReader
reader=PdfReader("resume.pdf")
# print(len(reader.pages))
text=""
# page=reader.pages[0]
for page in reader.pages:
    page_text=page.extract_text()
    if page_text:
        text+=page_text
if len(text.strip())<20:
    raise ValueError("no resume")
# print(page.extract_text())
# print(text)




# 1=resume 2=jd
from groq import Groq
from dotenv import load_dotenv
import os
from pathlib import Path
from pydantic import BaseModel

load_dotenv()
api_key=os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("pls add api key")

client=Groq(api_key=api_key)
model="llama-3.3-70b-versatile"

class resume(BaseModel):
    name:str|None=None
    email:str|None=None
    phone:str|None=None
    projects:list[str]|None=None
    skills_technical: list[str] | None = None
    skills_tools: list[str] | None = None
    skills_soft: list[str] | None = None
    experience:list[str]|None=None
    education:list[str]|None=None
    certification:list[str]|None=None
schema=resume.model_json_schema()

class jd(BaseModel):
    required_skills: list[str] | None = None
    preferred_skills: list[str] | None = None
    education:list[str]|None=None
    job_title: str | None = None
    location: str | None = None
    work_mode: str | None = None  # remote/hybrid/onsite
    experience_required: str | None = None  # e.g. "0-1 years" — keep as string, ranges don't fit a number well
jdschema=jd.model_json_schema()

response_format={
    "type":"json_object"
}
class score(BaseModel):
    score:float
    candidate_name: str | None = None
    matching_skills: list[str] | None = None
    missing_skills: list[str] | None = None
    experience_met: bool | None = None
    verdict: str | None = None
schem=score.model_json_schema()

prompt_resume=f''' provided a resume can u give me output in json format according to the schema 
{schema}'''
prompt_jd=f''' provided a job description can u give me output in json format according to the schema 
{jdschema}
'''

message1={
    "role":"system",
    "content":prompt_resume
}
message2={
    "role":"user",
    "content":text
}
message3={
    "role":"system",
    "content":prompt_jd
}
message4={
    "role":"user",
    "content":job_description
}

mess1=[message1,message2]
mess2=[message3,message4]
response1=client.chat.completions.create(model=model,messages=mess1,response_format=response_format)
response2=client.chat.completions.create(model=model,messages=mess2,response_format=response_format)

# print(response)
ans1=response1.choices[0].message.content
ans2=response2.choices[0].message.content
# print(ans)

import json
raw_json1=ans1
data_file1=json.loads(raw_json1)
print(f'''resume:{data_file1}''')
raw_json2=ans2

data_file2=json.loads(raw_json2)
print(f'''jd:{data_file2}''')
resume1=resume(**data_file1)
jd1=jd(**data_file2)
# print(req.projects)
# print(req.skills)




prompt=f'''{resume1.model_dump_json()} and {jd1.model_dump_json()} giving u resume and job description     Give me:

    1. Candidate name
    2. Matching skills
    3. Missing important skills
    4. Whether experience requirement is met
    5. Overall match percentage from 0 to 100
    6. A short final verdict
{schem} '''
message={
    "role":"user",
    "content":prompt
}
mes=[message]
repsonse3=client.chat.completions.create(model=model,messages=mes,response_format=response_format)
finalans=repsonse3.choices[0].message.content
rj=finalans
data_file=json.loads(rj)
print(data_file)
score1=score(**data_file)