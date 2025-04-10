# cover_letter_app.py
# Streamlit Interface for CrewAI Cover Letter Agent Crew

import streamlit as st
import fitz  # PyMuPDF for PDF reading
from docx import Document
from crewai import Agent, Task, Crew
from textwrap import dedent

def read_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def read_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in doc])

input_collector = Agent(
    role='Input Collector',
    goal='Gather resume, job description, and tone preference.',
    backstory='You ensure user input is correctly received and passed on.',
    verbose=True
)

job_analyzer = Agent(
    role='Job Description Analyst',
    goal='Extract key responsibilities, skills, and values from the job description.',
    backstory='You break down job descriptions into actionable items.',
    verbose=True
)

resume_matcher = Agent(
    role='Resume Matcher',
    goal='Identify and rank experiences relevant to the job description.',
    backstory='You extract matching content from resumes.',
    verbose=True
)

tone_stylist = Agent(
    role='Tone Stylist',
    goal='Create a tone and writing style guide.',
    backstory='You tailor the letter’s tone to user and company needs.',
    verbose=True
)

drafting_agent = Agent(
    role='Letter Drafter',
    goal='Write a compelling cover letter based on all inputs.',
    backstory='You are an expert professional writer.',
    verbose=True
)

editor_agent = Agent(
    role='Editor',
    goal='Polish the draft for professionalism and clarity.',
    backstory='You ensure the final draft is perfect.',
    verbose=True
)

st.title("📄 Cover Letter AI Agent Crew")
st.write("Upload your resume and job description to generate a personalized cover letter.")

resume_file = st.file_uploader("Upload your Resume (PDF or DOCX)", type=["pdf", "docx"])
job_file = st.file_uploader("Upload Job Description (PDF or DOCX)", type=["pdf", "docx"])
tone = st.selectbox("Select your preferred tone", ["formal", "enthusiastic", "conversational", "professional"])

generate = st.button("Generate Cover Letter")

if generate and resume_file and job_file:
    with st.spinner("Reading files and initializing agents..."):
        resume_text = read_pdf(resume_file) if resume_file.name.endswith("pdf") else read_docx(resume_file)
        job_text = read_pdf(job_file) if job_file.name.endswith("pdf") else read_docx(job_file)

        input_task = Task(
            description=f"Resume:\n{resume_text}\n\nJob Description:\n{job_text}\n\nTone Preference: {tone}",
            expected_output="A dictionary of inputs.",
            agent=input_collector
        )

        job_analysis_task = Task(
            description="Extract top 5 responsibilities and values from the job description.",
            expected_output="List of job priorities.",
            agent=job_analyzer
        )

        resume_matching_task = Task(
            description="Match relevant resume content to the job description.",
            expected_output="Ranked list of experiences.",
            agent=resume_matcher
        )

        tone_style_task = Task(
            description=f"Create a writing style guide based on tone: {tone}",
            expected_output="Tone guide.",
            agent=tone_stylist
        )

        draft_task = Task(
            description="Generate a draft cover letter.",
            expected_output="Initial draft.",
            agent=drafting_agent
        )

        edit_task = Task(
            description="Edit the draft for clarity and professionalism.",
            expected_output="Final letter.",
            agent=editor_agent
        )

        crew = Crew(
            agents=[input_collector, job_analyzer, resume_matcher, tone_stylist, drafting_agent, editor_agent],
            tasks=[input_task, job_analysis_task, resume_matching_task, tone_style_task, draft_task, edit_task],
            verbose=True
        )

        result = crew.run()
        st.success("✅ Cover letter generated!")
        st.text_area("Your Cover Letter", value=result, height=400)
        st.download_button("Download Cover Letter", data=result, file_name="cover_letter.txt")
