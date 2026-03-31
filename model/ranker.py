import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_text_from_pdf(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def rank_resumes(resumes, job_description):
    documents = [job_description] + resumes

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    ranked = sorted(
        list(zip(resumes, similarity)),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked


def get_matching_keywords(resume, job_description):
    resume_words = set(resume.lower().split())
    job_words = set(job_description.lower().split())

    return list(resume_words.intersection(job_words))


def analyze_resume(resume, job_description):
    resume = resume.lower()
    job = job_description.lower()

    categories = {
        "Programming": ["python", "java", "c++", "javascript", "sql"],
        "AI / Machine Learning": ["machine learning", "ml", "ai", "deep learning", "nlp"],
        "Data Analysis": ["pandas", "numpy", "data analysis", "statistics", "visualization"],
        "Web Development": ["flask", "django", "html", "css", "api"],
        "Tools & Platforms": ["git", "github", "linux", "docker", "cloud"]
    }

    category_scores = {}

    for category, keywords in categories.items():
        matched = []
        missing = []

        for word in keywords:
            if word in resume and word in job:
                matched.append(word)
            elif word in job and word not in resume:
                missing.append(word)

        score = int((len(matched) / len(keywords)) * 100)

        category_scores[category] = {
            "score": score,
            "matched": matched,
            "missing": missing
        }

    overall = int(
        sum(cat["score"] for cat in category_scores.values())
        / len(category_scores)
    )

    if overall >= 75:
        verdict = "Excellent match. Candidate strongly aligns with the job requirements."
    elif overall >= 55:
        verdict = "Good match. Candidate has relevant skills but could improve in some areas."
    elif overall >= 35:
        verdict = "Average match. Candidate lacks multiple required skills."
    else:
        verdict = "Weak match. Resume does not align well with the job description."

    return category_scores, overall, verdict