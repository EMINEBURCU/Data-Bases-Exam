from flask import Flask, request, redirect, url_for, render_template
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as db:

        db.execute('DROP TABLE IF EXISTS preferences')
        db.execute('DROP TABLE IF EXISTS courses')
        db.execute('DROP TABLE IF EXISTS teachers')
        db.execute('DROP TABLE IF EXISTS students')
        # Create students table
        db.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                class TEXT NOT NULL
            );
        ''')
        students_data = [
            ('John Doe', 14, '1A'),
            ('Jane Smith', 14, '1A'),
            ('Michael Johnson', 15, '1A'),
            ('Emily Davis', 14, '1A'),
            ('Daniel Brown', 15, '1A'),
            ('Olivia Wilson', 14, '1B'),
            ('William Taylor', 14, '1B'),
            ('Sophia Moore', 15, '1B'),
            ('James Anderson', 14, '1B'),
            ('Isabella Thomas', 15, '1B'),
            ('Ethan Martin', 14, '1C'),
            ('Charlotte White', 14, '1C'),
            ('Logan Harris', 15, '1C'),
            ('Ava Clark', 14, '1C'),
            ('Jacob Lewis', 15, '1C')
        ]
        db.executemany('INSERT INTO students (name, age, class) VALUES (?, ?, ?)', students_data)

        # Create teachers table 
        db.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                class TEXT NOT NULL
            );
        ''')
        teachers_data = [
            ('Alice Johnson', '1A'),
            ('Bob Smith', '1B'),
            ('Carol Taylor', '1C'),
        ]
        db.executemany('INSERT INTO teachers (name, class) VALUES (?, ?)', teachers_data)

        # Create courses table 
        db.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );
        ''')
        courses_data = [
            ('Mathematics',),
            ('Science',),
            ('Gym',),
            ('Language',),
            ('Art',)
        ]
        db.executemany('INSERT INTO courses (name) VALUES (?)', courses_data)

        # Create preferences table
        db.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                teacher_id INTEGER,
                course_id INTEGER,
                first_choice_id INTEGER,
                second_choice_id INTEGER,
                third_choice_id INTEGER,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (teacher_id) REFERENCES teachers(id),
                FOREIGN KEY (course_id) REFERENCES courses(id),
                FOREIGN KEY (first_choice_id) REFERENCES students(id),
                FOREIGN KEY (second_choice_id) REFERENCES students(id),
                FOREIGN KEY (third_choice_id) REFERENCES students(id)
            );
        ''')
        db.commit()

@app.route('/')
def index():
    return render_template('index.html')

def fetch_mutually_preferred_pairs():
    with get_db_connection() as conn:
       
        result = conn.execute('''
        SELECT
            student1.name AS student1,
            student2.name AS student2,
            student3.name AS student3,
            courses.name AS course
        FROM preferences
        JOIN students AS student1 ON preferences.first_choice_id = student1.id
        JOIN students AS student2 ON preferences.second_choice_id = student2.id
        JOIN students AS student3 ON preferences.third_choice_id = student3.id
        JOIN courses ON preferences.course_id = courses.id
        WHERE preferences.first_choice_id IS NOT NULL
        ''').fetchall()
        return result


def fetch_top_students_by_class():
    with get_db_connection() as conn:
        result = {}
        classes = conn.execute('SELECT DISTINCT class FROM students').fetchall()
        for class_name in classes:
            students = conn.execute('''
            SELECT name
            FROM students
            WHERE class = ?
            ORDER BY popularity DESC
            LIMIT 3
            ''', (class_name['class'],)).fetchall()
            result[class_name['class']] = students
        return result

def fetch_courses_by_popularity():
    with get_db_connection() as conn:
        result = conn.execute('''
        SELECT name, popularity
        FROM courses
        ORDER BY popularity DESC
        ''').fetchall()
        return result


@app.route('/summary')
def summary():
    student_id = request.args.get('student_id')
    teacher_id = request.args.get('teacher_id')
    course_id = request.args.get('course_id')

    pairs = fetch_mutually_preferred_pairs(student_id, teacher_id, course_id)
    popular_students = fetch_top_students_by_class(student_id, teacher_id, course_id)
    popular_courses = fetch_courses_by_popularity()

    return render_template('summary.html', pairs=pairs, popular_students=popular_students, popular_courses=popular_courses)

def fetch_top_students_by_class(student_id=None, teacher_id=None, course_id=None):
    with get_db_connection() as conn:
        result = {}
        classes = conn.execute('SELECT DISTINCT class FROM students').fetchall()
        for class_name in classes:
            students = conn.execute('''
            SELECT name, IFNULL(popularity, 0) AS popularity
            FROM students
            WHERE class =?
            ORDER BY popularity DESC
            LIMIT 3
            ''', (class_name['class'],)).fetchall()
            result[class_name['class']] = students
        return result


def fetch_mutually_preferred_pairs(student_id=None, teacher_id=None, course_id=None):
    with get_db_connection() as conn:
        query = '''
        SELECT student1.name AS student1, student2.name AS student2, student3.name AS student3, courses.name AS course
        FROM preferences
        JOIN students AS student1 ON preferences.first_choice_id = student1.id
        JOIN students AS student2 ON preferences.second_choice_id = student2.id
        JOIN students AS student3 ON preferences.third_choice_id = student3.id
        JOIN courses ON preferences.course_id = courses.id
        WHERE 1 = 1
        '''
        params = []

        # Optional filtering by student, teacher, or course
        if student_id:
            query += ' AND preferences.student_id = ?'
            params.append(student_id)

        if teacher_id:
            query += ' AND preferences.teacher_id = ?'
            params.append(teacher_id)

        if course_id:
            query += ' AND preferences.course_id = ?'
            params.append(course_id)

        result = conn.execute(query, params).fetchall()
        return result


@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    error_message = None
    success_message = None

    if request.method == 'POST':
        # Extract form data
        student_id = request.form.get('student_id')
        teacher_id = request.form.get('teacher_id')
        course_id = request.form.get('favorite_course')
        preferences = {
            'first_preference': request.form.get('first_preference'),
            'second_preference': request.form.get('second_preference'),
            'third_preference': request.form.get('third_preference')
        }

        # Process and update popularity
        update_popularity(student_id, teacher_id, course_id, preferences)

        # Insert into preferences table using values from the preferences dictionary
        with get_db_connection() as db:
            db.execute('''
                INSERT INTO preferences (
                    student_id, teacher_id, course_id, first_choice_id, second_choice_id, third_choice_id
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, teacher_id, course_id, preferences['first_preference'], preferences['second_preference'], preferences['third_preference']))
            db.commit()

        # Redirect to another page or indicate success
        return redirect(url_for('summary'))
    else:
        with get_db_connection() as db:
            students = db.execute('SELECT * FROM students').fetchall()
            teachers = db.execute('SELECT * FROM teachers').fetchall()
            courses = db.execute('SELECT * FROM courses').fetchall()
        return render_template('questionnaire.html', students=students, teachers=teachers, courses=courses)

    if request.method == 'POST':
        # Extract form data
        student_id = request.form.get('student_id')
        teacher_id = request.form.get('teacher_id')
        course_id = request.form.get('favorite_course')
        preferences = {
            'first_preference': request.form.get('first_preference'),
            'second_preference': request.form.get('second_preference'),
            'third_preference': request.form.get('third_preference')
        }
        # Process and update popularity
        update_popularity(student_id, teacher_id, course_id, preferences)

        # Process the data (e.g., save to database)
        with get_db_connection() as db:
            db.execute('''
                INSERT INTO preferences (
                    student_id, teacher_id, course_id, first_choice_id, second_choice_id, third_choice_id
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, teacher_id, course_id, first_preference, second_preference, third_preference))
            db.commit()

        # Redirect to another page or indicate success
        return redirect(url_for('summary'))
    else:
        with get_db_connection() as db:
            students = db.execute('SELECT * FROM students').fetchall()
            teachers = db.execute('SELECT * FROM teachers').fetchall()
            courses = db.execute('SELECT * FROM courses').fetchall()
        return render_template('questionnaire.html', students=students, teachers=teachers, courses=courses)

    return render_template('questionnaire.html', students=students, teachers=teachers, courses=courses, error_message=error_message, success_message=success_message)

def update_db_schema():
    with get_db_connection() as db:
        try:
           
            db.execute('''
                ALTER TABLE students
                ADD COLUMN popularity INTEGER DEFAULT 0
            ''')

          
            db.execute('''
                ALTER TABLE courses
                ADD COLUMN popularity INTEGER DEFAULT 0
            ''')
            db.commit()
        except sqlite3.OperationalError as e:
            print(f"Error updating schema: {e}")


# Update popularity
def update_popularity(student_id, teacher_id, course_id, preferences):
    with get_db_connection() as db:
        preference_ids = (preferences['first_preference'], preferences['second_preference'], preferences['third_preference'])
        for pid in preference_ids:
            db.execute('''
                UPDATE students
                SET popularity = popularity + 1
                WHERE id = ?
            ''', (pid,))
        
      
        db.execute('''
            UPDATE courses
            SET popularity = popularity + 1
            WHERE id = ?
        ''', (course_id,))
        db.commit()



popular_students = fetch_top_students_by_class()
print("\nTop Students by Class:")
for class_name, students in popular_students.items():
    print(f"Class {class_name}:")
    for student in students:
        print(f"{student['name']}: {student['popularity']}")
        print(student['name'])

popular_courses = fetch_courses_by_popularity()
print("\nPopular Courses:")
for course in popular_courses:
    print(f"{course['name']}: {course['popularity']}")

@app.route('/get_classmates', methods=['GET'])
def get_classmates():
    student_id = request.args.get('student_id')
    if student_id is None:
        return {'error': 'Missing student_id'}, 400

    with get_db_connection() as conn:
        
        student_class = conn.execute('''
        SELECT class FROM students WHERE id = ?
        ''', (student_id,)).fetchone()

        if not student_class:
            return {'error': 'Student not found'}, 404

    
        classmates = conn.execute('''
        SELECT id, name FROM students
        WHERE class = ? AND id != ?
        ''', (student_class['class'], student_id)).fetchall()

    return {
        'classmates': [{'id': classmate['id'], 'name': classmate['name']} for classmate in classmates]
    }


if __name__ == '__main__':
    init_db()  
    update_db_schema() 
    app.run(debug=True)

