from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/generate-job', methods=['POST'])
def generate_job():
    data = request.json
    generator = JobDescriptionGenerator()
    description = generator.generate(
        data['title'], data['company'], 
        data['keywords'], data['experience']
    )
    return jsonify({"description": description})

@app.route('/evaluate-resume', methods=['POST'])
def evaluate_resume():
    # Handle file upload and job description
    # Return analysis
    
if __name__ == '__main__':
    app.run(debug=True)