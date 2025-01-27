import sys
import os
from sqlalchemy import inspect, text

# Add the project directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from website import create_app, db

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)

    # Ensure 'student_planner' table exists
    if not inspector.has_table('student_planner'):
        with db.engine.connect() as connection:
            connection.execute(
                text("""
                    CREATE TABLE student_planner (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title VARCHAR(255) NOT NULL,
                        start_date DATE NOT NULL,
                        end_date DATE NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        user_id INTEGER NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES user(id)
                    )
                """)
            )
            print("Created 'student_planner' table.")
    else:
        print("'student_planner' table already exists.")

    # Ensure 'planner_task' table exists
    if not inspector.has_table('planner_task'):
        with db.engine.connect() as connection:
            connection.execute(
                text("""
                    CREATE TABLE planner_task (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        day VARCHAR(50) NOT NULL,
                        description VARCHAR(500) NOT NULL,
                        start_time TIME NOT NULL,
                        end_time TIME NOT NULL,
                        student_planner_id INTEGER NOT NULL,
                        FOREIGN KEY(student_planner_id) REFERENCES student_planner(id) ON DELETE CASCADE
                    )
                """)
            )
            print("Created 'planner_task' table.")
    else:
        print("'planner_task' table already exists.")

    # Ensure 'planner_feedback' table exists
    if not inspector.has_table('planner_feedback'):
        with db.engine.connect() as connection:
            connection.execute(
                text("""
                    CREATE TABLE planner_feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        comment TEXT NOT NULL,
                        date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
                        user_id INTEGER NOT NULL,
                        student_planner_id INTEGER NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES user(id),
                        FOREIGN KEY(student_planner_id) REFERENCES student_planner(id) ON DELETE CASCADE
                    )
                """)
            )
            print("Created 'planner_feedback' table.")
    else:
        print("'planner_feedback' table already exists.")

    # Ensure 'task' table exists
    if not inspector.has_table('task'):
        with db.engine.connect() as connection:
            connection.execute(
                text("""
                    CREATE TABLE task (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        day VARCHAR(50) NOT NULL,
                        description VARCHAR(500) NOT NULL,
                        start_time TIME NOT NULL,
                        end_time TIME NOT NULL,
                        planner_id INTEGER NOT NULL,
                        FOREIGN KEY(planner_id) REFERENCES planner(id)
                    )
                """)
            )
            print("Created 'task' table.")
    else:
        print("'task' table already exists.")

    # Ensure 'planner' table exists
    if not inspector.has_table('planner'):
        with db.engine.connect() as connection:
            connection.execute(
                text("""
                    CREATE TABLE planner (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title VARCHAR(255) NOT NULL,
                        start_date DATE NOT NULL,
                        end_date DATE NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        user_id INTEGER NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES user(id)
                    )
                """)
            )
            print("Created 'planner' table.")
    else:
        print("'planner' table already exists.")

    print("Migration completed successfully.")
