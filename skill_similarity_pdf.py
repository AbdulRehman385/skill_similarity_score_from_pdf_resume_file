# -*- coding: utf-8 -*-
"""Skill_similarity_pdf

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1_95-1JdKZLALZTaoy4D4R0yKjt2XrHZO
"""

#!pip install PyPDF2 streamlit

# import libraries
import PyPDF2
import streamlit as st
import spacy

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# def extract_text_from_pdf(pdf_path):
#     with open(pdf_path, 'rb') as file:
#         reader = PyPDF2.PdfReader(file)
#         text = ''
#         for page in reader.pages:
#             text += page.extract_text()
#     return text

def extract_text_from_pdf(pdf_file):
  reader = PyPDF2.PdfReader(pdf_file)
  text = ''
  for page in reader.pages:
    text += page.extract_text()
  return text

def skills_extract(text):

  try:
      nlp = spacy.load("en_core_web_sm")
  except OSError:
      subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
      nlp = spacy.load("en_core_web_sm")

  # Use pre-trained NER
  doc = nlp(text)
  skills = []
  for ent in doc.ents:
    skills.append(ent.text)
  return skills

def score_resume_cosine(job_desc_skills, resume_skills):

    all_skills = job_desc_skills + resume_skills

    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(all_skills)

    # Separate job description vector and resume vector
    job_desc_vector = tfidf_matrix[:len(job_desc_skills)]  # First part is job description skills
    resume_vector = tfidf_matrix[len(job_desc_skills):]     # Second part is resume skills

    # Compute cosine similarity between the job description and resume vectors
    similarity = cosine_similarity(resume_vector, job_desc_vector)

    # Average the similarity scores (To take combined mean of all the probabilities vectors)
    average_similarity = similarity.mean()

    # Return the score as a percentage
    return round(average_similarity * 100, 2)

def suggested_skills(job_skills, resume_skills):
  suggested_skills = []
  for skill in job_skills:
    if skill not in resume_skills:
      suggested_skills.append(skill)
  return suggested_skills

def process_skills_text(j_skills, r_skills):

  # split the job skills into list
  job_skills = j_skills.split(',')

  #clean both resume and job skills texts
  job_skills = [job_skill.strip() for job_skill in job_skills]
  job_skills = [job_skill.lower() for job_skill in job_skills]

  resume_skills = [resume_skill.strip() for resume_skill in resume_skills]
  resume_skills = [resume_skill.lower() for resume_skill in resume_skills]

  return job_skills, resume_skills

st.title('Resume Analyzer')

resume_file = st.file_uploader('Upload your Resume PDF file', type=['pdf'])

st.write("Input the Job Skills")
st.write("The job skills should be comma-separated as follows:")
st.write("EX: machine learning, deep learning, C++, ....")

job_skills = st.text_input("Write job skills")

if 'resume_score' not in st.session_state:
    st.session_state.resume_score = None
if 'resume_skills' not in st.session_state:
    st.session_state.resume_skills = None

if st.button('Analyze'):
    if resume_file is not None and job_skills:
        # Extract the pdf file
        text = extract_text_from_pdf(resume_file)
        resume_skills = skills_extract(text)

        # Process skills
        job_skills, resume_skills = process_skills_text(job_skills, resume_skills)

        # Get the resume score
        st.session_state.resume_score = score_resume_cosine(job_skills, resume_skills)
        st.session_state.resume_skills = resume_skills

        st.write(f"Resume Score: {st.session_state.resume_score}%")

# Get suggested skills only if resume_score is available
if st.session_state.resume_score is not None:
    if st.button("Suggest Skills"):
        missing_skills = suggested_skills(job_skills, st.session_state.resume_skills)

        if missing_skills:
            st.write("Suggested Skills to Add:")
            st.write(", ".join(missing_skills))
        else:
            st.write("Your resume already contains all the required job skills!")
