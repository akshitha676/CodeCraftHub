from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "courses.json"

VALID_STATUS = ["Not Started", "In Progress", "Completed"]

# ---------------------------
# Helper Functions
# ---------------------------

def load_courses():
    """Load courses from JSON file"""
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except:
        return []


def save_courses(courses):
    """Save courses to JSON file"""
    with open(DATA_FILE, "w") as file:
        json.dump(courses, file, indent=4)


def get_next_id(courses):
    """Generate next course ID"""
    if not courses:
        return 1
    return max(course["id"] for course in courses) + 1


# ---------------------------
# HOME ROUTE (Fixes 404)
# ---------------------------

@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to CodeCraftHub API 🚀",
        "available_endpoints": {
            "GET all courses": "/api/courses",
            "GET course by id": "/api/courses/<id>",
            "POST create course": "/api/courses",
            "PUT update course": "/api/courses/<id>",
            "DELETE course": "/api/courses/<id>"
        }
    })


# ---------------------------
# API ROUTES
# ---------------------------

@app.route("/api/courses", methods=["POST"])
def add_course():
    data = request.get_json()

    required_fields = ["name", "description", "target_date", "status"]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    if data["status"] not in VALID_STATUS:
        return jsonify({"error": "Invalid status value"}), 400

    courses = load_courses()

    new_course = {
        "id": get_next_id(courses),
        "name": data["name"],
        "description": data["description"],
        "target_date": data["target_date"],
        "status": data["status"],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    courses.append(new_course)
    save_courses(courses)

    return jsonify(new_course), 201


@app.route("/api/courses", methods=["GET"])
def get_all_courses():
    courses = load_courses()
    return jsonify(courses)


@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    courses = load_courses()

    for course in courses:
        if course["id"] == course_id:
            return jsonify(course)

    return jsonify({"error": "Course not found"}), 404


@app.route("/api/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    courses = load_courses()
    data = request.get_json()

    for course in courses:
        if course["id"] == course_id:

            if "status" in data and data["status"] not in VALID_STATUS:
                return jsonify({"error": "Invalid status value"}), 400

            course.update(data)
            save_courses(courses)

            return jsonify(course)

    return jsonify({"error": "Course not found"}), 404


@app.route("/api/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    courses = load_courses()

    for course in courses:
        if course["id"] == course_id:
            courses.remove(course)
            save_courses(courses)

            return jsonify({"message": "Course deleted successfully"})

    return jsonify({"error": "Course not found"}), 404


# ---------------------------
# RUN SERVER
# ---------------------------

if __name__ == "__main__":
    print("CodeCraftHub API is starting...")
    print("Open in browser: http://localhost:5000")
    print("Courses endpoint: http://localhost:5000/api/courses")

    app.run(debug=True)