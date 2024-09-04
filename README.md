Welcome! This is a proof of concept of a resume scanning tool. 
It uses a combination of ChatGPT-4 and the Gmail API to automate assessing a candidate for a job, and then emailing that candidate if they are a good fit.
Multiple interviews with recruiters were conducted to identify the use case, and built this prototype using Claude and ChatGPT.
I plan on expanding on this proof of concept to include assessments of multiple resumes at once.

## Overview

This Python script automates the process of analyzing a candidate's fit for a job based on their resume and a job description, using OpenAI's GPT-4 API. If the candidate is deemed a good fit, the script generates a personalized interview invitation email and sends it to the candidate.

## Features

- **PDF Text Extraction**: Extracts text from PDF files containing the candidate's resume and job description.
- **Email Extraction**: Identifies and extracts the candidate's email address from the resume.
- **Fit Analysis**: Uses GPT-4 to analyze the candidate's resume against the job description to determine if they are a good fit.
- **Email Generation**: Generates a personalized email to the candidate if they are a good fit.
- **Email Sending**: Sends the generated email to the candidate using Gmail's SMTP server.

## Prerequisites

- Python 3.x
- Google API client libraries for Gmail
- OpenAI account and API key
- Gmail account with "App Passwords" enabled if using 2FA

## Environment Setup

Ensure the following environment variables are set before running the script:

- `SENDER_EMAIL`: The sender's Gmail address.
- `SENDER_PASSWORD`: The sender's Gmail password or app-specific password.
- `OPENAI_API_KEY`: Your OpenAI API key.
- `RECEIVER_EMAIL`: The receiver's email address (usually extracted from the resume).

You can set these variables in your environment or include them in a `.env` file and load them using a package like `python-dotenv`.

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
