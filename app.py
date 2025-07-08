from flask import Flask, render_template, request
import openai
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# In-memory patient database (for demo purposes)
patients_db = {}

@app.route("/", methods=["GET", "POST"])
def index():
    diagnosis = None
    patient_name = None
    submitted_by = None
    hospital_name = None
    symptoms = None
    test_results = None
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if request.method == "POST":
        if "search_patient" in request.form:
            # Search patient record
            patient_name = request.form["search_patient"].strip()
            if patient_name and patient_name in patients_db:
                patient_record = patients_db[patient_name]
                submitted_by = patient_record.get("submitted_by")
                hospital_name = patient_record.get("hospital_name")
                symptoms = patient_record.get("symptoms")
                test_results = patient_record.get("test_results")
                diagnosis = patient_record.get("diagnosis")
            else:
                diagnosis = f"No records found for patient: {patient_name}"
        else:
            # Handle diagnosis submission
            patient_name = request.form["patient_name"].strip()
            submitted_by = request.form["submitted_by"].strip()
            hospital_name = request.form["hospital_name"].strip()
            symptoms = request.form["symptoms"].strip()
            test_results = request.form["test_results"].strip()

            prompt = f"""
            You are a helpful AI medical assistant. Based on the patient's name, symptoms, and test results, provide a diagnosis and medical recommendation.

            Patient Name: {patient_name}
            Symptoms: {symptoms}
            Test Results: {test_results}

            Respond clearly and professionally, as if you are assisting a medical team.
            """

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                diagnosis = response["choices"][0]["message"]["content"]

                # Save record
                patients_db[patient_name] = {
                    "submitted_by": submitted_by,
                    "hospital_name": hospital_name,
                    "symptoms": symptoms,
                    "test_results": test_results,
                    "diagnosis": diagnosis
                }

            except Exception as e:
                diagnosis = f"Error: {str(e)}"

    return render_template(
        "index.html",
        diagnosis=diagnosis,
        patient_name=patient_name,
        submitted_by=submitted_by,
        hospital_name=hospital_name,
        symptoms=symptoms,
        test_results=test_results,
        current_time=current_time
    )

# ✅ This line makes it work on Render or other cloud platforms
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)