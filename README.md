
---

# Online Exam Portal

## Overview

The **Online Exam Portal** is a web application built using Streamlit that facilitates online assessments. It provides functionalities for faculty to create and save questions, allows students to submit answers, and offers an analytics dashboard to review student performance and plagiarism statistics. The application integrates Natural Language Processing (NLP) for grammar checking and plagiarism detection using the `fuzzywuzzy` library.

## Features

- **Faculty Dashboard**:
  - Input for subject, number of questions, exam date, and session.
  - Ability to enter questions and correct answers.
  - Save questions and answers to CSV files for further analysis.

- **Student Page**:
  - Students can view questions and submit their answers.
  - Answers are saved for each student, allowing for future analysis.

- **Analytics Dashboard**:
  - Display performance data for students and question statistics.
  - Visualizations of average plagiarism scores, total plagiarism distribution, and question breakdowns.
  - Overall plagiarism statistics for all students.

## Technologies Used

- Python
- Streamlit
- Spacy (for NLP)
- Fuzzywuzzy (for plagiarism detection)
- Pandas (for data manipulation)
- Altair and Plotly (for data visualization)

## Installation

To run this application locally, follow these steps:

1. **Clone the Repository**:

   ```bash
   git clone <repository-url>
   cd online-exam-portal
   ```

2. **Set Up Virtual Environment (Optional but recommended)**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Required Libraries**:

   ```bash
   pip install -r requirements.txt
   ```

   Make sure to create a `requirements.txt` file with the following content:

   ```
   streamlit
   spacy
   fuzzywuzzy
   pandas
   plotly
   altair
   ```

4. **Download NLP Model**:

   Run the following command to download the English NLP model for Spacy:

   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Run the Application**:

   ```bash
   streamlit run app.py
   ```

   This will start a local server, and you can access the app in your web browser at `http://localhost:8501`.

## Directory Structure

```
/online-exam-portal
├── data/                # Contains saved question and performance data
│   └── [subject_name]/  # Subfolders for each subject containing CSV files
├── app.py               # Main application file
├── requirements.txt      # List of required packages
└── README.md            # Project documentation
```

## Usage

1. **Faculty Dashboard**:
   - Input the subject name, number of questions, date, and session.
   - Enter the questions and their corresponding correct answers.
   - Click the "Save Questions" button to save the data.

2. **Student Page**:
   - Students can submit their answers after reading the questions provided by the faculty.

3. **Analytics Dashboard**:
   - Faculty can view analytics, including overall plagiarism statistics and individual student performance metrics.

## How It Works

- **Saving Data**: The application creates directories for each subject under the `data/` folder. Questions and answers are stored in CSV format, which makes them easy to access and analyze later.
  
- **Plagiarism and Grammar Checking**: When students submit their answers, the application calculates plagiarism scores based on similarity to the correct answers. It also performs basic grammar checks using the Spacy library.

- **Visualizations**: The analytics dashboard uses Plotly for creating interactive visualizations to present data clearly and effectively.
