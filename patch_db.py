import sqlite3
import os

db_path = 'db.sqlite3'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Adding columns manually to adminpanel_adminnotification...")
        # Check if columns exist
        cursor.execute("PRAGMA table_info(adminpanel_adminnotification)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'notification_type' not in columns:
            print("Adding notification_type column...")
            cursor.execute("ALTER TABLE adminpanel_adminnotification ADD COLUMN notification_type varchar(20) DEFAULT 'other' NOT NULL")
        
        if 'related_link' not in columns:
            print("Adding related_link column...")
            cursor.execute("ALTER TABLE adminpanel_adminnotification ADD COLUMN related_link varchar(255) NULL")
            
        conn.commit()
        print("Columns added successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
else:
    print(f"Database file {db_path} not found.")
