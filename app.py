from flask import Flask, render_template, request
from model.ranker import rank_resumes, extract_text_from_pdf, get_matching_keywords, analyze_resume

app = Flask(__name__)


# ======================
# HOME PAGE
# ======================
@app.route('/')
def home():
    return render_template('home.html')


# ======================
# RANK PAGE
# ======================
@app.route('/rank-page')
def rank_page():
    return render_template('index.html')


# ======================
# MAIN LOGIC
# ======================
@app.route('/rank', methods=['POST'])
def rank():
    job_desc = request.form['job_description']
    files = request.files.getlist('resumes')

    resume_texts = []
    file_names = []

    # Extract text
    for file in files:
        if file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(file)
            resume_texts.append(text)
            file_names.append(file.filename)

    # Rank resumes
    ranked = rank_resumes(resume_texts, job_desc)

    results = []

    # 🔥 FIXED LOOP (no index error now)
    for rank, (resume_text, score) in enumerate(ranked, start=1):

        # Get correct file name
        index = resume_texts.index(resume_text)

        keywords = get_matching_keywords(resume_text, job_desc)

        category_scores, match_percent, verdict = analyze_resume(
            resume_text, job_desc
        )

        # Match level
        if score > 0.5:
            level = "Excellent Match"
        elif score > 0.3:
            level = "Good Match"
        elif score > 0.15:
            level = "Average Match"
        else:
            level = "Poor Match"

        results.append({
            'rank': rank,
            'name': file_names[index],
            'score': round(float(score), 4),
            'level': level,
            'keywords': keywords,
            'category_scores': category_scores,
            'match_percent': match_percent,
            'verdict': verdict
        })

    return render_template('index.html', results=results)


# ======================
# RUN APP
# ======================
if __name__ == '__main__':
    app.run(debug=True)