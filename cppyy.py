import streamlit as st
import spacy
from fuzzywuzzy import fuzz
import pandas as pd
import os
import plotly.express as px

# Load NLP model for grammar check
nlp = spacy.load('en_core_web_sm')

# --- Helper Functions ---
def ensure_data_directory(subject):
    # Create a directory for the subject if it doesn't exist
    subject_path = f'data/{subject}'
    if not os.path.exists(subject_path):
        os.makedirs(subject_path)
    return subject_path

def save_questions(subject, num_questions, questions, correct_answers, date, session):
    subject_path = ensure_data_directory(subject)
    
    # Save the questions, correct answers, date, and session to a CSV file
    question_data = {
        "Question": questions,
        "Correct Answer": correct_answers,
        "Date": [date] * num_questions,
        "Session": [session] * num_questions
    }
    
    df = pd.DataFrame(question_data)
    df.to_csv(f"{subject_path}/{subject}_questions.csv", index=False)

def save_answers(student_id, subject, answers):
    subject_path = ensure_data_directory(subject)

    # Save answers to a file specific to the subject
    with open(f"{subject_path}/{student_id}_answers.txt", "w") as f:
        for i, answer in enumerate(answers, 1):
            f.write(f"Q{i}: {answer}\n")

def plagiarism_check(answers, correct_answers):
    plagiarism_results = []
    for answer, correct_answer in zip(answers, correct_answers):
        similarity = fuzz.ratio(answer, correct_answer)
        plagiarism_results.append(similarity)
    return plagiarism_results

def grammar_check(doc):
    errors = [token.text for token in doc if token.pos_ == "X"]
    return len(errors)

def save_performance(student_id, subject, plagiarism_results, grammar_errors, num_questions):
    subject_path = ensure_data_directory(subject)

    # Create a dictionary to hold performance data
    result_data = {
        "subject": subject,
        "student": student_id,
    }

    for i in range(num_questions):
        result_data[f'q{i + 1}_plagiarism'] = plagiarism_results[i]
        result_data[f'q{i + 1}_grammar_errors'] = grammar_errors[i]

    # Save student performance data in a separate CSV file for each student
    file_path = f"{subject_path}/{student_id}_performance.csv"
    pd.DataFrame([result_data]).to_csv(file_path, index=False)

    # Update overall plagiarism data
    update_overall_plagiarism(subject, plagiarism_results)

def update_overall_plagiarism(subject, plagiarism_results):
    subject_path = ensure_data_directory(subject)
    overall_file_path = f"{subject_path}/overall_plagiarism.csv"
    
    if os.path.exists(overall_file_path):
        overall_data = pd.read_csv(overall_file_path)
    else:
        overall_data = pd.DataFrame(columns=["subject", "total_students", "total_plagiarism_score"])

    total_plagiarism_score = sum(plagiarism_results)
    total_students = overall_data['total_students'].sum() + 1  # Increment for new student
    
    # Check if the subject already exists in the overall_data DataFrame
    if overall_data.empty or overall_data['subject'].iloc[0] != subject:
        new_data = pd.DataFrame({
            "subject": [subject],
            "total_students": [total_students],
            "total_plagiarism_score": [total_plagiarism_score]
        })
        overall_data = pd.concat([overall_data, new_data], ignore_index=True)
    else:
        overall_data.at[0, "total_students"] = total_students
        overall_data.at[0, "total_plagiarism_score"] += total_plagiarism_score

    overall_data.to_csv(overall_file_path, index=False)

def display_dashboard(selected_subject):
    subject_path = f'data/{selected_subject}'

    # Performance Data
    performance_file_path = f"{subject_path}/{selected_subject}_performance.csv"
    if os.path.exists(performance_file_path):
        try:
            performance_data = pd.read_csv(performance_file_path, on_bad_lines='skip')
            st.subheader("Performance Data")
            st.write(performance_data)

            # Ensure the necessary columns are present
            if 'student' in performance_data.columns and 'q1_plagiarism' in performance_data.columns:
                # Bar Chart for average plagiarism scores
                avg_plagiarism = performance_data.filter(like='_plagiarism').mean(axis=1)
                performance_data['Average Plagiarism'] = avg_plagiarism

                bar_chart = px.bar(performance_data, 
                                    x='student', 
                                    y='Average Plagiarism',  
                                    title='Average Plagiarism Scores by Student',
                                    labels={'student': 'Students', 'Average Plagiarism': 'Average Plagiarism Score'})
                st.plotly_chart(bar_chart)

                # Pie Chart for total plagiarism distribution
                total_plagiarism = performance_data.filter(like='_plagiarism').sum(axis=1)
                performance_data['Total Plagiarism'] = total_plagiarism

                pie_chart = px.pie(performance_data, 
                                   names='student', 
                                   values='Total Plagiarism', 
                                   title='Total Plagiarism Distribution by Student')
                st.plotly_chart(pie_chart)

        except pd.errors.ParserError as e:
            st.error(f"Error reading performance data: {e}")
    else:
        st.write("No performance data available yet.")

    # Questions Data
    questions_file_path = f"{subject_path}/{selected_subject}_questions.csv"
    if os.path.exists(questions_file_path):
        try:
            questions_data = pd.read_csv(questions_file_path, on_bad_lines='skip')
            st.subheader("Questions Data")
            st.write(questions_data)

            # Ensure the necessary columns for questions data
            if 'Category' in questions_data.columns and 'Count' in questions_data.columns:
                questions_bar_chart = px.bar(questions_data, 
                                              x='Category',  
                                              y='Count',     
                                              title='Number of Questions by Category',
                                              labels={'Category': 'Categories', 'Count': 'Number of Questions'})
                st.plotly_chart(questions_bar_chart)

            if 'Question Type' in questions_data.columns:
                questions_pie_chart = px.pie(questions_data, 
                                               names='Question Type',  
                                               values='Count',        
                                               title='Distribution of Questions by Type')
                st.plotly_chart(questions_pie_chart)

        except pd.errors.ParserError as e:
            st.error(f"Error reading questions data: {e}")
    else:
        st.write("No questions data available for this subject.")

# --- Main App ---
st.title("Online Exam Portal")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Faculty Dashboard", "Student Page", "Analytics Dashboard"])

# --- Global Variables ---
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = []
if "subject" not in st.session_state:
    st.session_state.subject = ""
if "date" not in st.session_state:
    st.session_state.date = ""
if "session" not in st.session_state:
    st.session_state.session = ""

if page == "Faculty Dashboard":
    st.header("Faculty Dashboard")

    # Input for Subject, Number of Questions, Date, and Session
    subject = st.text_input("Enter Subject:")
    num_questions = st.number_input("Enter the number of questions:", min_value=1, step=1)
    exam_date = st.date_input("Select Exam Date:")
    session = st.selectbox("Choose Session:", ["Morning", "Afternoon"])

    if subject and num_questions and exam_date and session:
        st.session_state.subject = subject
        st.session_state.date = exam_date.strftime("%Y-%m-%d")
        st.session_state.session = session
        st.session_state.questions = []
        st.session_state.answers = []

        st.write(f"Subject: {subject}")
        st.write(f"Number of Questions: {num_questions}")
        st.write(f"Date: {st.session_state.date}")
        st.write(f"Session: {session}")

        # Input for Questions and Correct Answers
        for i in range(num_questions):
            question = st.text_area(f"Enter Question {i + 1}:")
            correct_answer = st.text_area(f"Enter Correct Answer for Question {i + 1}:")
            st.session_state.questions.append(question)
            st.session_state.answers.append(correct_answer)

        if st.button("Save Questions"):
            save_questions(subject, num_questions, st.session_state.questions, st.session_state.answers, st.session_state.date, st.session_state.session)
            st.success("Questions saved successfully! Students can now answer them.")

elif page == "Student Page":
    if not st.session_state.questions or not st.session_state.subject:
        st.warning("No questions available at the moment. Please check back later.")
    else:
        st.header(f"Submit Your Answers for {st.session_state.subject}")

        with st.form("answer_form"):
            student_id = st.text_input("Enter your Student ID:")
            answers = []
            for i, question in enumerate(st.session_state.questions, 1):
                st.write(f"Question {i}: {question}")
                answer = st.text_area(f"Your Answer for Question {i}:")
                answers.append(answer)

            submit_button = st.form_submit_button("Submit Answers")
            if submit_button:
                save_answers(student_id, st.session_state.subject, answers)
                plagiarism_results = plagiarism_check(answers, st.session_state.answers)
                grammar_errors = [grammar_check(nlp(answer)) for answer in answers]
                save_performance(student_id, st.session_state.subject, plagiarism_results, grammar_errors, len(answers))
                st.success("Answers submitted successfully! Thank you.")

elif page == "Analytics Dashboard":
    st.header("Analytics Dashboard")

    selected_subject = st.selectbox("Select Subject:", os.listdir('data/'))

    if selected_subject:
        display_dashboard(selected_subject)
