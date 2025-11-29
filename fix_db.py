import sqlite3

db_path = '/home/uvaibhav/vgdev/taskman/task_manager.db'
print(f"Connecting to {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

columns_to_add = [
    ("created_at", "DATETIME"),
    ("updated_at", "DATETIME"),
    ("parent_id", "INTEGER")
]

for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f"ALTER TABLE task ADD COLUMN {col_name} {col_type}")
        print(f"Successfully added column: {col_name}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"Column {col_name} already exists.")
        else:
            print(f"Error adding {col_name}: {e}")

conn.commit()
conn.close()
