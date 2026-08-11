import sqlite3
from datetime import datetime
from config import DATABASE_PATH

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation_type TEXT NOT NULL,
            input_filename TEXT NOT NULL,
            output_filename TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def log_operation(operation_type, input_filename, output_filename, status="Success", details=""):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO operations (operation_type, input_filename, output_filename, status, details, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (operation_type, input_filename, output_filename, status, details, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database logging error: {e}")

def get_history(limit=50):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, operation_type, input_filename, output_filename, status, details, created_at
            FROM operations
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []

def clear_history():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM operations')
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error clearing history: {e}")
        return False

def get_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as total FROM operations')
        total = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as success FROM operations WHERE status = 'Success'")
        success = cursor.fetchone()['success']

        cursor.execute('''
            SELECT operation_type, COUNT(*) as count 
            FROM operations 
            GROUP BY operation_type 
            ORDER BY count DESC
        ''')
        breakdown = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return {
            'total_operations': total,
            'successful_operations': success,
            'breakdown': breakdown
        }
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {'total_operations': 0, 'successful_operations': 0, 'breakdown': []}

# Initialize database on module load
init_db()
