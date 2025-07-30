from flask import Flask, render_template_string, request, redirect, session
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

subjects = {
    "Analog Communication Lab": [],
    "Data Structures and Algorithms Lab": [],
    "Digital Logic Design Lab": [],
    "Linear Integrated Circuits Lab": [],
    "Operating System Concepts Lab": [],
    "Analog Communication": [],
    "Data Structures and Algorithms": [],
    "Digital Logic Design (M2)": [],
    "Electro-Magnetic Field Theory": [],
    "Linear Integrated Circuits": [],
    "Operating System Concepts": []
}

weekly_timetable = {
    "Monday": ["Operating System Concepts Lab", "Operating System Concepts", "Data Structures and Algorithms", "Electro-Magnetic Field Theory"],
    "Tuesday": ["Digital Logic Design (M2)", "Analog Communication Lab", "Linear Integrated Circuits", "Data Structures and Algorithms", "Analog Communication"],
    "Wednesday": ["Digital Logic Design (M2)", "Linear Integrated Circuits Lab", "Linear Integrated Circuits", "Analog Communication", "Electro-Magnetic Field Theory", "Data Structures and Algorithms Lab"],
    "Thursday": ["Analog Communication", "Digital Logic Design Lab", "Linear Integrated Circuits", "Operating System Concepts", "Digital Logic Design (M2)"],
    "Friday": ["Data Structures and Algorithms Lab", "Operating System Concepts", "Data Structures and Algorithms", "Electro-Magnetic Field Theory"]
}

users_file = "users.json"
attendance_file = "attendance.json"

def load_users():
    return json.load(open(users_file)) if os.path.exists(users_file) else {}

def save_users(data):
    json.dump(data, open(users_file, "w"))

def load_data():
    return json.load(open(attendance_file)) if os.path.exists(attendance_file) else subjects.copy()

def save_data(data):
    json.dump(data, open(attendance_file, "w"))

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()
        u, p = request.form["username"], request.form["password"]
        if u in users and users[u] == p:
            session["user"] = u
            return redirect("/dashboard")
        else:
            return "Invalid credentials"
    return render_template_string("""
    <html><head>
    <title>Login</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head><body class="bg-dark text-white d-flex justify-content-center align-items-center vh-100">
    <form method="post" class="p-5 rounded bg-secondary">
        <h2 class="mb-3">Login - Dark Knight Attendance Tracker</h2>
        <input name="username" placeholder="Username" class="form-control mb-2" required>
        <input name="password" type="password" placeholder="Password" class="form-control mb-3" required>
        <button class="btn btn-light w-100">Login</button>
        <p class="mt-3 text-center"><a href="/register" class="text-white">Create account</a></p>
    </form></body></html>
    """)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = load_users()
        u, p = request.form["username"], request.form["password"]
        users[u] = p
        save_users(users)
        return redirect("/")
    return render_template_string("""
    <html><head>
    <title>Register</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head><body class="bg-dark text-white d-flex justify-content-center align-items-center vh-100">
    <form method="post" class="p-5 rounded bg-secondary">
        <h2 class="mb-3">Register - Dark Knight Tracker</h2>
        <input name="username" placeholder="Choose Username" class="form-control mb-2" required>
        <input name="password" type="password" placeholder="Choose Password" class="form-control mb-3" required>
        <button class="btn btn-light w-100">Register</button>
        <p class="mt-3 text-center"><a href='/' class='text-white'>Back to Login</a></p>
    </form></body></html>
    """)

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")
    data = load_data()
    if request.method == "POST":
        subject = request.form["subject"]
        status = request.form["status"]
        if status in ["present", "absent", "off"]:
            data.setdefault(subject, []).append(status)
            save_data(data)
        return redirect("/dashboard")
    
    today = datetime.now().strftime("%A")
    current_day_subjects = weekly_timetable.get(today, [])

    html = """
    <html><head>
    <title>Dashboard - Dark Knight Attendance Tracker</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head><body class="bg-light">
    <div class="container py-4">
    <h1 class="text-center mb-4">🦇 Dark Knight Attendance Tracker</h1>
    
    <form method="post" class="row g-3">
        <div class="col-md-6">
            <label class="form-label">Subject</label>
            <select name="subject" class="form-select">
                {% for subj in subjects %}
                <option value="{{subj}}">{{subj}}</option>
                {% endfor %}
            </select>
        </div>
        <div class="col-md-4">
            <label class="form-label">Status</label>
            <select name="status" class="form-select">
                <option value="present">Present</option>
                <option value="absent">Absent</option>
                <option value="off">Off Class</option>
            </select>
        </div>
        <div class="col-md-2 d-flex align-items-end">
            <button class="btn btn-success w-100">Mark</button>
        </div>
    </form>

    <hr>
    <h3 class="mt-4 text-primary">📅 Weekly Timetable</h3>
    <div class="row">
        {% for day, subs in timetable.items() %}
        <div class="col-md-2">
            <div class="card {% if day == today %}bg-warning{% else %}bg-light{% endif %} mb-3">
                <div class="card-header">{{day}}</div>
                <ul class="list-group list-group-flush">
                    {% for s in subs %}
                    <li class="list-group-item">{{s}}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
        {% endfor %}
    </div>

    <h3 class="mt-4 text-primary">📊 Attendance Summary</h3>
    <table class="table table-bordered table-striped">
        <thead class="table-dark">
            <tr><th>Subject</th><th>Held</th><th>Present</th><th>Absent</th><th>Off</th><th>%</th></tr>
        </thead>
        <tbody>
        {% for subject, records in data.items() %}
            {% set present = records|select('equalto', 'present')|list|length %}
            {% set absent = records|select('equalto', 'absent')|list|length %}
            {% set off = records|select('equalto', 'off')|list|length %}
            {% set held = present + absent %}
            {% set percent = (present / held * 100) if held > 0 else 0 %}
            <tr class="{% if percent >= 75 %}table-success{% else %}table-danger{% endif %}">
                <td>{{subject}}</td>
                <td>{{held}}</td>
                <td>{{present}}</td>
                <td>{{absent}}</td>
                <td>{{off}}</td>
                <td>{{"%.2f"|format(percent)}}%</td>
            </tr>
        {% endfor %}
        </tbody>
    </table>

    <a href="/edit" class="btn btn-outline-secondary">Edit Attendance</a>
    <a href="/change-password" class="btn btn-outline-warning">Change Password</a>
    <a href="/logout" class="btn btn-outline-danger">Logout</a>
    </div></body></html>
    """
    return render_template_string(html, data=data, subjects=subjects.keys(), timetable=weekly_timetable, today=today)

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if "user" not in session:
        return redirect("/")
    data = load_data()
    if request.method == "POST":
        subject = request.form["subject"]
        new_count = int(request.form["count"])
        status = request.form["status"]
        if subject in data:
            data[subject] = [s for s in data[subject] if s != status]
            data[subject] += [status] * new_count
            save_data(data)
        return redirect("/edit")
    
    return render_template_string("""
    <html><head>
    <title>Edit Attendance</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head><body class="bg-light p-4">
    <div class="container">
    <h2>Edit Attendance Records</h2>
    <form method="post" class="row g-3">
        <div class="col-md-4">
            <label class="form-label">Subject</label>
            <select name="subject" class="form-select">
                {% for s in subjects %}
                <option>{{s}}</option>
                {% endfor %}
            </select>
        </div>
        <div class="col-md-4">
            <label class="form-label">Status</label>
            <select name="status" class="form-select">
                <option value="present">Present</option>
                <option value="absent">Absent</option>
                <option value="off">Off Class</option>
            </select>
        </div>
        <div class="col-md-2">
            <label class="form-label">Count</label>
            <input type="number" name="count" class="form-control" min="0">
        </div>
        <div class="col-md-2 d-flex align-items-end">
            <button class="btn btn-primary w-100">Update</button>
        </div>
    </form>
    <a href="/dashboard" class="btn btn-secondary mt-3">Back</a>
    </div></body></html>
    """, subjects=subjects.keys())

@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "user" not in session:
        return redirect("/")
    if request.method == "POST":
        users = load_users()
        user = session["user"]
        current = request.form["current"]
        new = request.form["new"]
        if users[user] == current:
            users[user] = new
            save_users(users)
            return redirect("/dashboard")
        else:
            return "Wrong current password"
    return render_template_string("""
    <html><head>
    <title>Change Password</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head><body class="bg-light p-4">
    <div class="container">
    <h2>Change Password</h2>
    <form method="post">
        <input name="current" type="password" placeholder="Current password" class="form-control mb-2" required>
        <input name="new" type="password" placeholder="New password" class="form-control mb-2" required>
        <button class="btn btn-warning">Change</button>
    </form>
    <a href="/dashboard" class="btn btn-secondary mt-3">Back</a>
    </div></body></html>
    """)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))  # Use Render's assigned port
    app.run(host="0.0.0.0", port=port)


