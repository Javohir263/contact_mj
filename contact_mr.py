import psycopg2
from datetime import date

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    database="yoqlama",
    user="postgres",
    password="Java_0420",
    port="5432"
)
cur = conn.cursor()

# --- Choose role ---
role = input("Login as Teacher (T) or Student (S)? ").upper()

if role == 'T':
    # --- Teacher login ---
    username = input("Enter your first name (teacher): ")
    cur.execute("SELECT teacher_id, first_name FROM teacher WHERE first_name=%s", (username,))
    teacher = cur.fetchone()

    if teacher is None:
        print("Teacher not found!")
        cur.close()
        conn.close()
        exit()

    teacher_id = teacher[0]
    print(f"Welcome {teacher[1]}! You can now mark attendance.\n")

    # --- Get students ---
    cur.execute("SELECT student_id, first_name FROM student WHERE teacher_id=%s ORDER BY student_id", (teacher_id,))
    students = cur.fetchall()
    print("Students in your class:")
    for s in students:
        print(s[1], end="  ")
    print("\n")

    # --- Input attendance ---
    attendance_input = input(f"Enter attendance for {len(students)} students (1=Present, 0=Absent): ")

    for i, (student_id, first_name) in enumerate(students):
        if i < len(attendance_input):
            status = 'Present' if attendance_input[i] == '1' else 'Absent'
            cur.execute("""
                INSERT INTO attendance (student_id, teacher_id, class_date, status)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (student_id, teacher_id, class_date)
                DO UPDATE SET status = EXCLUDED.status
            """, (student_id, teacher_id, date.today(), status))

    conn.commit()
    print("\nAttendance updated!\n")

    # --- Show today's attendance ---
    cur.execute("""
        SELECT s.first_name, a.status
        FROM attendance a
        JOIN student s ON a.student_id = s.student_id
        WHERE a.teacher_id=%s AND a.class_date=%s
    """, (teacher_id, date.today()))
    for row in cur.fetchall():
        print(f"{row[0]} -> {row[1]}")

elif role == 'S':
    # --- Student login ---
    student_name = input("Enter your first name (student): ")
    cur.execute("SELECT student_id, first_name FROM student WHERE first_name=%s", (student_name,))
    student = cur.fetchone()

    if student is None:
        print("Student not found!")
        cur.close()
        conn.close()
        exit()

    student_id = student[0]
    print(f"Hello {student[1]}! Here is your attendance:\n")

    # --- Show attendance ---
    cur.execute("""
        SELECT class_date, status, t.first_name AS teacher_name
        FROM attendance a
        JOIN teacher t ON a.teacher_id = t.teacher_id
        WHERE a.student_id=%s
        ORDER BY class_date
    """, (student_id,))

    rows = cur.fetchall()
    if rows:
        for row in rows:
            print(f"{row[0]} | {row[2]} -> {row[1]}")
    else:
        print("No attendance records found.")

else:
    print("Invalid role! Please choose T or S.")

cur.close()
conn.close()
