# 1. Official Python Base Image
FROM python:3.10-slim

# 2. Working directory set karein
WORKDIR /app

# 3. Requirements copy and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Project files copy karein
COPY . .

# 5. Port expose karein
EXPOSE 8501

# 6. Streamlit app run karein
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]