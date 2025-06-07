# AI Job Matcher

AI Job Matcher is a modern, AI-powered Streamlit web application that helps users analyze their CV, receive personalized career advice, and discover the most relevant job opportunities in Lebanon. The app leverages Google Custom Search to fetch jobs from LinkedIn and Bayt, and uses advanced AI (Gemini) to highlight the top 3 job matches for each user.

---

## Features

- **CV Upload & Parsing**: Upload your CV in PDF format. The app extracts and displays the text for review.
- **AI Career Advice**: Get actionable, personalized career advice and suggested job titles based on your CV using advanced AI analysis.
- **Job Search**: Instantly search for jobs from LinkedIn and Bayt, filtered for Lebanon and Beirut, using Google Custom Search.
- **AI-Powered Job Matching**: The AI reviews all found jobs and highlights the top 3 most relevant jobs for you, with clear explanations and visually distinct cards.
- **Modern UI/UX**: Beautiful, dark-themed interface with Lottie animations, custom CSS, and responsive design for a professional experience.
- **Advanced Filtering**: Filter jobs by location, type, and source directly from the sidebar.
- **Robust Error Handling**: User-friendly error messages and clear feedback throughout the workflow.

---

## How It Works

1. **Upload Your CV**: Drag and drop your PDF CV. The app parses and displays the extracted text.
2. **Get AI Career Advice**: Click the button to receive tailored advice and suggested job titles.
3. **Search for Jobs**: Select a job title and number of results, then search for jobs from LinkedIn and Bayt.
4. **Review AI Recommendations**: The AI highlights the top 3 jobs for you, with all other matches also displayed and filterable.

---

## Technologies Used

- **Streamlit**: For the interactive web UI.
- **Lottie Animations**: For engaging, modern visuals.
- **Google Custom Search API**: To fetch job listings from LinkedIn and Bayt.
- **Gemini AI (Google Generative AI)**: For CV analysis, career advice, and job matching.
- **PyMuPDF (fitz)**: For PDF parsing.
- **Python**: Core backend and logic.

---

## Project Structure

```
search_job/
├── main.py                # Main Streamlit app
├── requirements.txt       # Python dependencies
├── assets/
│   └── animation.json     # Lottie animation for hero section
├── utils/
│   ├── ai_advice.py       # AI analysis and job matching logic
│   ├── job_search.py      # Job search and filtering logic
│   └── __init__.py
├── .env                   # API keys and config (not committed)
└── pages/                 # (Optional) Additional Streamlit pages
```

---

## Setup & Installation

1. **Clone the repository**

```bash
# Clone the repo
$ git clone <your-repo-url>
$ cd search_job
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the root directory with the following keys:

```
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CX=your_google_cse_cx
GEMINI_API_KEY=your_gemini_api_key
```

4. **Run the app**

```bash
streamlit run main.py
```

---

## Usage

- Open the app in your browser (usually at http://localhost:8501).
- Upload your CV and follow the workflow to get advice and job matches.
- Use the sidebar to filter jobs by location, type, and source.

---

## Customization

- **Lottie Animations**: Replace `assets/animation.json` or update the Lottie URLs in `main.py` for different visuals.
- **Job Sources**: Extend `utils/job_search.py` to add more job boards or regions.
- **Styling**: Edit the custom CSS in `main.py` for further UI tweaks.

---

## Troubleshooting

- **No Jobs Found**: Google CSE may have daily limits or may not always return all jobs. Try again later or adjust your search terms.
- **API Errors**: Ensure your API keys are correct and have sufficient quota.
- **PDF Parsing Issues**: Only PDF files are supported. Ensure your CV is not password-protected or scanned as an image.

---

## License

This project is for educational and personal use. For commercial use, please check the terms of the APIs and data sources used.

---

## Credits

- Lottie animations from [lottiefiles.com](https://lottiefiles.com/)
- Job data from LinkedIn and Bayt via Google Custom Search
- AI powered by Google Gemini

---

Enjoy your AI-powered job search!
