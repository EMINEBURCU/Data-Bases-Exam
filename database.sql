-- DDL Statements

DROP TABLE IF EXISTS preferences;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS students;

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    class TEXT NOT NULL
);

CREATE TABLE teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    class TEXT NOT NULL
);

CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE preferences (
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

-- DML Komutları (Verilerin eklenmesi)

INSERT INTO students (name, age, class) VALUES
('John Doe', 14, '1A'), ('Jane Smith', 14, '1A'),
('Michael Johnson', 15, '1A'), ('Emily Davis', 14, '1A'),
('Daniel Brown', 15, '1A'), ('Olivia Wilson', 14, '1B'),
('William Taylor', 14, '1B'), ('Sophia Moore', 15, '1B'),
('James Anderson', 14, '1B'), ('Isabella Thomas', 15, '1B'),
('Ethan Martin', 14, '1C'), ('Charlotte White', 14, '1C'),
('Logan Harris', 15, '1C'), ('Ava Clark', 14, '1C'),
('Jacob Lewis', 15, '1C');

INSERT INTO teachers (name, class) VALUES
('Alice Johnson', '1A'), ('Bob Smith', '1B'), ('Carol Taylor', '1C');

INSERT INTO courses (name) VALUES
('Mathematics'), ('Science'), ('Gym'), ('Language'), ('Art');
