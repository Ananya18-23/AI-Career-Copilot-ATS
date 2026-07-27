import streamlit as st
import pdfplumber
import re

# Page Configuration
st.set_page_config(page_title="AI Resume Quality & ATS Checker", page_icon="📄", layout="centered")

st.title("📄 AI Resume & ATS Checker")
st.write("Upload your resume to get an instant Quality Score, Section Analysis, and Improvement Tips!")

# --- Helper Functions ---

def get_pdf_text(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + " "
    return text

def analyze_resume(text):
    text_lower = text.lower()
    word_count = len(text.split())
    
    # 1. Essential Sections Check
    sections = {
        "Education": ["education", "university", "college", "b.tech", "degree"],
        "Skills": ["skills", "technical skills", "technologies", "programming"],
        "Projects": ["projects", "personal projects", "key projects"],
        "Experience / Internships": ["experience", "internship", "work history", "employment"],
        "Summary / Objective": ["summary", "objective", "profile", "about me"]
    }
    
    found_sections = []
    missing_sections = []
    for section, keywords in sections.items():
        if any(kw in text_lower for kw in keywords):
            found_sections.append(section)
        else:
            missing_sections.append(section)

    # 2. Contact Information Detection
    email_found = bool(re.search(r'[\w\.-]+@[\w\.-]+', text))
    phone_found = bool(re.search(r'\+?\d[\d\s-]{8,12}\d', text))
    linkedin_found = "linkedin.com" in text_lower
    github_found = "github.com" in text_lower

    # 3. Score Calculation Logic
    score = 0
    suggestions = []

    # Section Score (Max 40 Points)
    score += len(found_sections) * 8
    if missing_sections:
        suggestions.append(f"**Add Missing Sections:** Add {', '.join(missing_sections)} to your resume.")

    # Contact Info Score (Max 20 Points)
    contact_score = sum([email_found, phone_found, linkedin_found, github_found]) * 5
    score += contact_score
    if not linkedin_found:
        suggestions.append("**Add LinkedIn Link:** Include your professional LinkedIn profile link.")
    if not github_found:
        suggestions.append("**Add GitHub Link:** Add your GitHub link to showcase your project code.")

    # Word Count Score (Max 20 Points)
    if 300 <= word_count <= 900:
        score += 20
    elif word_count < 300:
        score += 10
        suggestions.append("**Short Length:** Your resume is too short. Add more details about your projects and responsibilities.")
    else:
        score += 10
        suggestions.append("**Too Long:** Try to keep your resume concise (under 800-900 words).")

    # Action Words / Impact Check (Max 20 Points)
    action_words = ["developed", "built", "implemented", "created", "analyzed", "designed", "achieved", "managed", "deployed"]
    action_count = sum(1 for word in action_words if word in text_lower)
    
    if action_count >= 5:
        score += 20
    else:
        score += (action_count * 4)
        suggestions.append("**Use Strong Action Verbs:** Use words like *Developed, Implemented, Analyzed, Deployed* to describe your project work.")

    return score, found_sections, missing_sections, {
        "Email": email_found,
        "Phone": phone_found,
        "LinkedIn": linkedin_found,
        "GitHub": github_found
    }, word_count, suggestions

# --- Streamlit UI Layout ---

st.divider()

uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    if st.button("🚀 Check Resume Quality", use_container_width=True):
        with st.spinner("Analyzing resume content and structure..."):
            resume_text = get_pdf_text(uploaded_file)
            
            score, found_sec, missing_sec, contacts, word_count, suggestions = analyze_resume(resume_text)

            st.divider()
            st.subheader("📊 Overall Resume Health Score")
            st.metric(label="ATS Readiness Score", value=f"{score} / 100")
            st.progress(score)

            if score >= 80:
                st.balloons()
                st.success("🔥 Excellent Resume! Your resume is well-formatted and ready for ATS.")
            elif score >= 60:
                st.info("⚠️ Good Resume! A few minor changes can push your score above 80%.")
            else:
                st.warning("❌ Needs Improvement. Follow the suggestions below to fix issues.")

            st.divider()

            # Breakdown Cards
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("✅ Detected Sections")
                for sec in found_sec:
                    st.write(f"✔️ {sec}")
                
                if missing_sec:
                    st.subheader("⚠️ Missing Sections")
                    for sec in missing_sec:
                        st.write(f"❌ {sec}")

            with col2:
                st.subheader("📇 Contact Info Check")
                for item, status in contacts.items():
                    if status:
                        st.write(f"✔️ {item}")
                    else:
                        st.write(f"❌ {item} Missing")

                st.write(f"**Total Word Count:** {word_count} words")

            # Suggestions Section
            st.divider()
            st.subheader("💡 Suggestions to Improve Your Score")
            if suggestions:
                for tip in suggestions:
                    st.write(f"• {tip}")
            else:
                st.write("Great job! No major improvements needed.")