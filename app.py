import google.generativeai as genai
import json
import re  # Added for regex-based JSON extraction

# Set up Gemini API key
GEMINI_API_KEY = "Your_api_key"
genai.configure(api_key=GEMINI_API_KEY)

def extract_json(text):
    """Extract JSON content from Gemini response."""
    json_match = re.search(r"\{.*\}|\[.*\]", text, re.DOTALL)  # Match JSON objects/arrays
    if json_match:
        return json_match.group(0)  # Return only the JSON part
    return None

def generate_questions(role, topic):
    """Generate 3 interview questions based on role & topic using Gemini."""
    prompt = f"Generate 3 interview questions for a {role} role on {topic}. Return only JSON with keys: 'question' and 'topic'."

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    print(response)

    # Extract and parse JSON from response
    json_str = extract_json(response.text)
    if not json_str:
        print("❌ Error: Could not extract JSON from response.")
        return ["Could not generate questions. Please try again."]

    try:
        questions_data = json.loads(json_str)  # Parse JSON
        questions = [q["question"] for q in questions_data]  # Extract questions
    except Exception as e:
        print(f"❌ JSON Parsing Error: {e}")
        questions = ["Could not generate questions. Please try again."]

    return questions

def conduct_interview(questions):
    """Ask questions one by one and store answers in a dictionary."""
    qa_pairs = {}

    print("\n🔹 AI Interview Started 🔹\n")
    for i, question in enumerate(questions, 1):
        print(f"Q{i}: {question}")
        answer = input("Your Answer: ").strip()
        qa_pairs[question] = answer if answer else "No Answer Given"  # Avoid empty answers

    return qa_pairs

def evaluate_responses(qa_pairs):
    """Send question-answer pairs to Gemini for evaluation."""
    prompt = f"""
    Evaluate the following interview answers and provide structured JSON feedback. 
    Include:
    - overall_assessment (summary)
    - sections (detailed feedback for each question)
    - recommendations for improvement.

    {json.dumps(qa_pairs, indent=2)}
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    json_str = extract_json(response.text)
    if not json_str:
        print("❌ Error: Could not extract evaluation JSON.")
        return {"error": "Evaluation failed."}

    try:
        evaluation = json.loads(json_str)  # Parse JSON
    except Exception as e:
        print(f"❌ JSON Parsing Error: {e}")
        evaluation = {"error": "Could not generate evaluation."}

    return evaluation

def main():
    """Main function to run the interview process."""
    role = input("Enter the job role: ").strip()
    topic = input("Enter the topic: ").strip()

    # Step 1: Get questions
    questions = generate_questions(role, topic)
    if "Could not generate questions" in questions[0]:
        return  # Stop execution if questions fail to generate

    # Step 2: Conduct interview
    qa_pairs = conduct_interview(questions)

    # Step 3: Evaluate responses
    evaluation = evaluate_responses(qa_pairs)

    print("\n🔹 AI Evaluation Result 🔹\n")
    print(json.dumps(evaluation, indent=2))  # Display JSON response nicely

if __name__ == "__main__":
    main()
