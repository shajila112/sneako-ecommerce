import sqlite3
import os

db_path = r'C:\Users\THIN 15\Desktop\SNEAKO_PROJECT\sneako_project\db.sqlite3'

def force_fix():
    print(f"Checking database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop existing table if any
    print("Dropping table 'adminpanel_usernotification' if it exists...")
    cursor.execute("DROP TABLE IF EXISTS adminpanel_usernotification;")
    
    print("Creating table 'adminpanel_usernotification'...")
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
    
    # Reset migration record
    print("Resetting migration record for 0004...")
    cursor.execute("DELETE FROM django_migrations WHERE app='adminpanel' AND name='0004_usernotification';")
    
    from datetime import datetime
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    cursor.execute("INSERT INTO django_migrations (app, name, applied) VALUES ('adminpanel', '0004_usernotification', ?);", (now,))
    
    conn.commit()
    conn.close()
    print("Force fix complete.")

if __name__ == "__main__":
    force_fix()
