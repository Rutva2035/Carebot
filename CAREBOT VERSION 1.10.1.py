import os
import sys
import random
import string
import pymysql
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog


mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="rutva@2035",
    database="carebot"
)

mycursor = mydb.cursor()


REPORT_DIR = "user_reports"
os.makedirs(REPORT_DIR, exist_ok=True)

def get_age_group(age):
    query = """
    SELECT age_group_id FROM age_groups 
    WHERE %s BETWEEN min_age AND max_age
    """
    mycursor.execute(query, (age,))
    result = mycursor.fetchone()
    return result[0] if result else None

def get_conditions_by_symptoms(symptom_names, age, gender):
    condition_scores = {}
    age_group_id = get_age_group(age)

    for symptom in symptom_names:
        mycursor.execute("""
            SELECT s.symptom_id FROM symptoms s
            WHERE LOWER(s.symptom_name) = LOWER(%s)
        """, (symptom,))
        symptom_data = mycursor.fetchone()

        if not symptom_data:
            continue

        symptom_id = symptom_data[0]

        mycursor.execute("""
            SELECT cs.condition_id, cs.severity_of_symptom 
            FROM condition_symptoms cs
            WHERE cs.symptom_id = %s
        """, (symptom_id,))

        for condition_id, severity in mycursor.fetchall():
            if condition_id not in condition_scores:
                condition_scores[condition_id] = 0
            if severity == 'Mild':
                condition_scores[condition_id] += 1
            elif severity == 'Moderate':
                condition_scores[condition_id] += 2
            elif severity == 'Severe':
                condition_scores[condition_id] += 3

    sorted_conditions = sorted(condition_scores.items(), key=lambda x: x[1], reverse=True)
    final_conditions = []

    for condition_id, score in sorted_conditions[:3]:
        mycursor.execute("""
            SELECT condition_name, condition_description, condition_severity, advice 
            FROM conditions 
            WHERE condition_id = %s
        """, (condition_id,))
        result = mycursor.fetchone()
        if result:
            condition = {
                'id': condition_id,
                'name': result[0],
                'description': result[1],
                'severity': result[2],
                'advice': result[3],
                'score': score
            }
            final_conditions.append(condition)

    return final_conditions

def recommend_doctors(condition_id):
    mycursor.execute("""
        SELECT d.doctor_name, d.specialization, d.contact_info
        FROM doctors d
        WHERE d.specialization = (
            SELECT c.condition_name FROM conditions c WHERE c.condition_id = %s
        )
    """, (condition_id,))
    return mycursor.fetchall()

def save_diagnosis(user_id, condition_id, symptoms):
    mycursor.execute("""
        INSERT INTO diagnosis_history (user_id, condition_id, symptoms, diagnosis_date)
        VALUES (%s, %s, %s, %s)
    """, (user_id, condition_id, ", ".join(symptoms), datetime.now()))
    mydb.commit()

def create_user(name, age, gender, pre_existing_conditions):
    mycursor.execute("""
        INSERT INTO users (name, age, gender, pre_existing_conditions)
        VALUES (%s, %s, %s, %s)
    """, (name, age, gender, pre_existing_conditions))
    mydb.commit()
    return mycursor.lastrowid

def delete_user_by_name(name):
    mycursor.execute("DELETE FROM users WHERE name = %s", (name,))
    mydb.commit()

def generate_report(user_id, name, conditions):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(REPORT_DIR, f"{name}_{user_id}_{timestamp}.txt")
    with open(filename, 'w') as f:
        f.write(f"Diagnosis Report for {name} (User ID: {user_id})\n\n")
        for cond in conditions:
            f.write(f"Condition: {cond['name']} ({cond['severity']})\n")
            f.write(f"Description: {cond['description']}\n")
            f.write(f"Advice: {cond['advice']}\n")
            f.write(f"Match Score: {cond['score']}\n\n")

    
    try:
        if sys.platform == "win32":
            os.startfile(REPORT_DIR)
        elif sys.platform == "darwin":
            os.system(f"open {REPORT_DIR}")
        else:
            os.system(f"xdg-open {REPORT_DIR}")
    except Exception as e:
        print("Could not open folder:", e)

    return filename

def user_mode():
    name = simpledialog.askstring("Input", "Enter your name:")
    age = int(simpledialog.askstring("Input", "Enter your age:"))
    gender = simpledialog.askstring("Input", "Enter your gender:")
    pre_existing = simpledialog.askstring("Input", "Any pre-existing conditions (comma-separated):")

    user_id = create_user(name, age, gender, pre_existing)

    symptoms_input = simpledialog.askstring("Input", "Enter your symptoms (comma-separated):")
    symptoms = [s.strip() for s in symptoms_input.split(",") if s.strip()]

    conditions = get_conditions_by_symptoms(symptoms, age, gender)

    if not conditions:
        messagebox.showinfo("Result", "No matching conditions found.")
        return

    report = ""
    for cond in conditions:
        report += f"\n- {cond['name']} ({cond['severity']})\n  Description: {cond['description']}\n  Advice: {cond['advice']}\n  Score: {cond['score']}\n"
        save_diagnosis(user_id, cond['id'], symptoms)

    messagebox.showinfo("Diagnosis", report)

    if messagebox.askyesno("Doctor Recommendation", "Would you like doctor recommendations?"):
        all_docs = []
        for cond in conditions:
            docs = recommend_doctors(cond['id'])
            all_docs.extend(docs)
        if all_docs:
            doc_list = "\n".join([f"Dr. {d[0]} ({d[1]}) — {d[2]}" for d in all_docs])
            messagebox.showinfo("Recommended Doctors", doc_list)
        else:
            messagebox.showinfo("Recommended Doctors", "No doctors found for your conditions.")

    report_file = generate_report(user_id, name, conditions)
    messagebox.showinfo("Report Saved", f"Report saved to: {report_file}")

def admin_mode():
    password = simpledialog.askstring("Admin Login", "Enter admin password:", show='*')
    if password != "asga06":
        messagebox.showerror("Error", "Incorrect admin password!")
        return

    choice = simpledialog.askstring("Admin", "Choose action: (view / delete_user)")
    if choice == "delete_user":
        username = simpledialog.askstring("Delete User", "Enter username to delete:")
        delete_user_by_name(username)
        messagebox.showinfo("Success", f"User '{username}' deleted.")
    elif choice == "view":
        mycursor.execute("SELECT * FROM users")
        data = mycursor.fetchall()
        info = "\n".join([str(row) for row in data])
        messagebox.showinfo("Users", info or "No users found.")
    else:
        messagebox.showerror("Error", "Invalid admin action.")

def main_gui():
    root = tk.Tk()
    root.withdraw()  
    choice = simpledialog.askstring("CareBot", "Mode: (user / admin)")
    if choice == "user":
        user_mode()
    elif choice == "admin":
        admin_mode()
    else:
        messagebox.showerror("Error", "Invalid mode selected.")

if __name__ == "__main__":
    main_gui()
