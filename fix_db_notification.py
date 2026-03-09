import sqlite3
import os

db_path = r'C:\Users\THIN 15\Desktop\SNEAKO_PROJECT\sneako_project\db.sqlite3'

def fix_db():
    print(f"Checking database at: {db_path}")
    if not os.path.exists(db_path):
        print("Database file NOT FOUND!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check for table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='adminpanel_usernotification';")
    table_exists = cursor.fetchone()

    if not table_exists:
        print("Table 'adminpanel_usernotification' is MISSING. Creating it now...")
        cursor.execute('''
            CREATE TABLE "adminpanel_usernotification" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "message" text NOT NULL,
                "is_read" bool NOT NULL,
                "created_at" datetime NOT NULL,
                "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
            );
        ''')
        cursor.execute('CREATE INDEX "adminpanel_usernotification_user_id_3306236b" ON "adminpanel_usernotification" ("user_id");')
        print("Table created successfully.")
    else:
        print("Table 'adminpanel_usernotification' already exists.")

    # Ensure migration is marked as applied
    cursor.execute("SELECT id FROM django_migrations WHERE app='adminpanel' AND name='0004_usernotification';")
    migration_applied = cursor.fetchone()

    if not migration_applied:
        print("Marking migration 0004 as applied...")
        from datetime import datetime
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        cursor.execute("INSERT INTO django_migrations (app, name, applied) VALUES ('adminpanel', '0004_usernotification', ?);", (now,))
        print("Migration record added.")
    else:
        print("Migration 0004 is already recorded as applied.")

    conn.commit()
    conn.close()
    print("Database sync complete.")

if __name__ == "__main__":
    fix_db()
