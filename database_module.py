"""
Module 3: Use Case Database
Hackathon Framework - Lightweight SQLite Database System

NO INSTALLATION REQUIRED - SQLite is built into Python

FEATURES:
- Zero-setup database
- Dynamic schema loading
- Pre-built templates for common use cases
- Natural language to SQL conversion
- Easy data import/export

CUSTOMIZATION:
1. Choose a schema template below
2. Modify tables for your use case
3. Populate with sample data
4. Deploy instantly!
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
from datetime import datetime
import csv

# ============================================================================
# SCHEMA TEMPLATES
# ============================================================================

SCHEMA_TEMPLATES = {
    "ecommerce": """
    -- E-commerce Platform Schema
    
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        price REAL NOT NULL,
        stock INTEGER DEFAULT 0,
        description TEXT,
        image_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        address TEXT,
        city TEXT,
        country TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_amount REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        shipping_address TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    );
    
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
    
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        customer_id INTEGER NOT NULL,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        comment TEXT,
        review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id),
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    );
    """,
    
    "healthcare": """
    -- Healthcare System Schema
    
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        date_of_birth DATE NOT NULL,
        gender TEXT,
        blood_type TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        emergency_contact TEXT,
        emergency_phone TEXT,
        allergies TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialization TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        license_number TEXT UNIQUE,
        years_experience INTEGER,
        available_days TEXT
    );
    
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        appointment_date TIMESTAMP NOT NULL,
        reason TEXT,
        status TEXT DEFAULT 'scheduled',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(id)
    );
    
    CREATE TABLE IF NOT EXISTS medical_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        visit_date TIMESTAMP NOT NULL,
        diagnosis TEXT,
        treatment TEXT,
        prescriptions TEXT,
        notes TEXT,
        follow_up_date DATE,
        FOREIGN KEY (patient_id) REFERENCES patients(id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(id)
    );
    
    CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        medication_name TEXT NOT NULL,
        dosage TEXT NOT NULL,
        frequency TEXT NOT NULL,
        duration TEXT,
        issued_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(id)
    );
    """,
    
    "education": """
    -- Educational Platform Schema
    
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        student_id TEXT UNIQUE NOT NULL,
        enrollment_date DATE NOT NULL,
        grade_level INTEGER,
        phone TEXT,
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS instructors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        department TEXT,
        specialization TEXT,
        phone TEXT,
        office_location TEXT
    );
    
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        instructor_id INTEGER,
        credits INTEGER NOT NULL,
        description TEXT,
        max_students INTEGER,
        schedule TEXT,
        FOREIGN KEY (instructor_id) REFERENCES instructors(id)
    );
    
    CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        grade TEXT,
        status TEXT DEFAULT 'enrolled',
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (course_id) REFERENCES courses(id),
        UNIQUE(student_id, course_id)
    );
    
    CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        due_date DATE NOT NULL,
        max_points INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (course_id) REFERENCES courses(id)
    );
    
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        content TEXT,
        grade INTEGER,
        feedback TEXT,
        FOREIGN KEY (assignment_id) REFERENCES assignments(id),
        FOREIGN KEY (student_id) REFERENCES students(id),
        UNIQUE(assignment_id, student_id)
    );
    """,
    
    "crm": """
    -- Customer Relationship Management Schema
    
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        company TEXT,
        job_title TEXT,
        lead_source TEXT,
        status TEXT DEFAULT 'new',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        industry TEXT,
        size TEXT,
        website TEXT,
        phone TEXT,
        address TEXT,
        city TEXT,
        country TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS deals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact_id INTEGER NOT NULL,
        company_id INTEGER,
        title TEXT NOT NULL,
        value REAL NOT NULL,
        stage TEXT DEFAULT 'prospecting',
        probability INTEGER CHECK(probability >= 0 AND probability <= 100),
        expected_close_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        closed_at TIMESTAMP,
        FOREIGN KEY (contact_id) REFERENCES contacts(id),
        FOREIGN KEY (company_id) REFERENCES companies(id)
    );
    
    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact_id INTEGER NOT NULL,
        activity_type TEXT NOT NULL,
        subject TEXT NOT NULL,
        description TEXT,
        activity_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed INTEGER DEFAULT 0,
        FOREIGN KEY (contact_id) REFERENCES contacts(id)
    );
    
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact_id INTEGER,
        deal_id INTEGER,
        note_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (contact_id) REFERENCES contacts(id),
        FOREIGN KEY (deal_id) REFERENCES deals(id)
    );
    """,
    
    "helpdesk": """
    -- Help Desk / Support Ticket Schema
    
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS agents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        department TEXT,
        specialization TEXT,
        max_tickets INTEGER DEFAULT 10,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        agent_id INTEGER,
        subject TEXT NOT NULL,
        description TEXT NOT NULL,
        priority TEXT DEFAULT 'medium',
        status TEXT DEFAULT 'open',
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (agent_id) REFERENCES agents(id)
    );
    
    CREATE TABLE IF NOT EXISTS ticket_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        is_internal INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ticket_id) REFERENCES tickets(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    
    CREATE TABLE IF NOT EXISTS knowledge_base (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT,
        tags TEXT,
        views INTEGER DEFAULT 0,
        helpful_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
}

# ============================================================================
# SAMPLE DATA GENERATORS
# ============================================================================

SAMPLE_DATA = {
    "ecommerce": {
        "products": [
            (1, "Laptop Pro 15", "Electronics", 1299.99, 25, "High-performance laptop with 16GB RAM", "laptop.jpg"),
            (2, "Wireless Mouse", "Accessories", 29.99, 150, "Ergonomic wireless mouse", "mouse.jpg"),
            (3, "USB-C Hub", "Accessories", 49.99, 80, "7-in-1 USB-C hub", "hub.jpg"),
            (4, "Mechanical Keyboard", "Accessories", 129.99, 45, "RGB mechanical keyboard", "keyboard.jpg"),
            (5, "27-inch Monitor", "Electronics", 349.99, 30, "4K UHD monitor", "monitor.jpg"),
        ],
        "customers": [
            (1, "John Doe", "john@email.com", "+1-555-0101", "123 Main St", "New York", "USA"),
            (2, "Jane Smith", "jane@email.com", "+1-555-0102", "456 Oak Ave", "Los Angeles", "USA"),
            (3, "Bob Johnson", "bob@email.com", "+1-555-0103", "789 Pine Rd", "Chicago", "USA"),
        ],
        "orders": [
            (1, 1, "2024-11-15 10:30:00", 1329.98, "shipped", "123 Main St, New York, USA"),
            (2, 2, "2024-11-18 14:20:00", 79.98, "processing", "456 Oak Ave, Los Angeles, USA"),
            (3, 1, "2024-11-19 09:15:00", 49.99, "delivered", "123 Main St, New York, USA"),
        ]
    },
    
    "healthcare": {
        "patients": [
            (1, "Alice Brown", "1985-03-15", "Female", "A+", "+1-555-0201", "alice@email.com", "123 Health St", "Emergency Contact: Bob Brown", "+1-555-0202", "Penicillin"),
            (2, "Charlie Davis", "1992-07-22", "Male", "O-", "+1-555-0203", "charlie@email.com", "456 Care Ave", "Emergency Contact: Diana Davis", "+1-555-0204", "None"),
            (3, "Eva Martinez", "1978-11-08", "Female", "B+", "+1-555-0205", "eva@email.com", "789 Wellness Blvd", "Emergency Contact: Frank Martinez", "+1-555-0206", "Latex"),
        ],
        "doctors": [
            (1, "Dr. Sarah Johnson", "Cardiology", "+1-555-0301", "dr.sarah@hospital.com", "MD12345", 15, "Mon-Fri"),
            (2, "Dr. Michael Lee", "Pediatrics", "+1-555-0302", "dr.michael@hospital.com", "MD12346", 10, "Mon-Wed-Fri"),
            (3, "Dr. Emily Chen", "General Practice", "+1-555-0303", "dr.emily@hospital.com", "MD12347", 8, "Tue-Thu-Sat"),
        ],
        "appointments": [
            (1, 1, 1, "2024-11-25 10:00:00", "Annual checkup", "scheduled", "Patient needs blood work"),
            (2, 2, 2, "2024-11-26 14:30:00", "Flu symptoms", "scheduled", "Prescribe medication if needed"),
            (3, 3, 3, "2024-11-27 09:00:00", "Follow-up visit", "scheduled", "Review test results"),
        ]
    },
    
    "education": {
        "students": [
            (1, "Tom Wilson", "tom@university.edu", "STU001", "2023-09-01", 1, "+1-555-0401", "100 Campus Dr"),
            (2, "Lisa Anderson", "lisa@university.edu", "STU002", "2023-09-01", 1, "+1-555-0402", "101 Campus Dr"),
            (3, "Mark Thompson", "mark@university.edu", "STU003", "2022-09-01", 2, "+1-555-0403", "102 Campus Dr"),
        ],
        "instructors": [
            (1, "Prof. James White", "james@university.edu", "Computer Science", "Artificial Intelligence", "+1-555-0501", "Room 301"),
            (2, "Prof. Maria Garcia", "maria@university.edu", "Mathematics", "Statistics", "+1-555-0502", "Room 302"),
            (3, "Prof. David Kim", "david@university.edu", "Physics", "Quantum Mechanics", "+1-555-0503", "Room 303"),
        ],
        "courses": [
            (1, "CS101", "Introduction to Programming", 1, 3, "Learn Python programming basics", 30, "Mon-Wed 10:00-11:30"),
            (2, "MATH201", "Calculus II", 2, 4, "Advanced calculus concepts", 25, "Tue-Thu 14:00-16:00"),
            (3, "PHY301", "Quantum Physics", 3, 4, "Introduction to quantum mechanics", 20, "Mon-Wed-Fri 09:00-10:00"),
        ]
    }
}

# ============================================================================
# MAIN DATABASE CLASS
# ============================================================================

class UseCaseDatabase:
    """
    Lightweight SQLite database for hackathon demos
    
    Features:
    - Zero installation required
    - Multiple schema templates
    - Easy data import/export
    - Natural language query support (with AI agent)
    """
    
    def __init__(self, db_path: str = "use_case.db", schema_type: str = "ecommerce"):
        """
        Initialize database
        
        Args:
            db_path: Path to SQLite database file
            schema_type: Template to use (ecommerce, healthcare, education, crm, helpdesk)
        """
        self.db_path = Path(db_path)
        self.schema_type = schema_type
        self.conn = None
        self.cursor = None
        
        self._connect()
        print(f"✅ Database initialized: {self.db_path}")
    
    def _connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        self.cursor = self.conn.cursor()
        
        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")
        
        # Use WAL mode for better concurrency
        self.cursor.execute("PRAGMA journal_mode = WAL")
    
    def setup_schema(self, schema_type: Optional[str] = None):
        """
        Create tables from template
        
        Args:
            schema_type: Which template to use (overrides init)
        """
        schema_type = schema_type or self.schema_type
        
        if schema_type not in SCHEMA_TEMPLATES:
            raise ValueError(f"Unknown schema type: {schema_type}. Available: {list(SCHEMA_TEMPLATES.keys())}")
        
        schema_sql = SCHEMA_TEMPLATES[schema_type]
        self.cursor.executescript(schema_sql)
        self.conn.commit()
        
        print(f"✅ Schema '{schema_type}' created successfully")
        return True
    
    def load_sample_data(self, schema_type: Optional[str] = None):
        """Load sample data for demonstration"""
        schema_type = schema_type or self.schema_type
        
        if schema_type not in SAMPLE_DATA:
            print(f"⚠️ No sample data available for '{schema_type}'")
            return False
        
        data = SAMPLE_DATA[schema_type]
        
        for table_name, rows in data.items():
            placeholders = ','.join(['?' for _ in rows[0]])
            sql = f"INSERT OR IGNORE INTO {table_name} VALUES ({placeholders})"
            
            try:
                self.cursor.executemany(sql, rows)
                self.conn.commit()
                print(f"✅ Loaded {len(rows)} rows into {table_name}")
            except sqlite3.Error as e:
                print(f"⚠️ Error loading data into {table_name}: {e}")
        
        return True
    
    def execute(self, sql: str, params: Tuple = ()) -> int:
        """
        Execute INSERT/UPDATE/DELETE query
        
        Returns:
            Last inserted row ID
        """
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"⚠️ SQL Error: {e}")
            raise
    
    def query(self, sql: str, params: Tuple = ()) -> List[Dict]:
        """
        Execute SELECT query
        
        Returns:
            List of dictionaries (rows)
        """
        try:
            self.cursor.execute(sql, params)
            columns = [description[0] for description in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"⚠️ SQL Error: {e}")
            return []
    
    def query_one(self, sql: str, params: Tuple = ()) -> Optional[Dict]:
        """Execute SELECT query and return first result"""
        results = self.query(sql, params)
        return results[0] if results else None
    
    def get_tables(self) -> List[str]:
        """Get list of all tables"""
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        results = self.query(sql)
        return [row['name'] for row in results]
    
    def get_table_schema(self, table_name: str) -> List[Dict]:
        """Get schema information for a table"""
        sql = f"PRAGMA table_info({table_name})"
        return self.query(sql)
    
    def get_row_count(self, table_name: str) -> int:
        """Get number of rows in a table"""
        result = self.query_one(f"SELECT COUNT(*) as count FROM {table_name}")
        return result['count'] if result else 0
    
    def export_to_json(self, output_file: str):
        """Export entire database to JSON"""
        data = {}
        
        for table in self.get_tables():
            data[table] = self.query(f"SELECT * FROM {table}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"✅ Exported database to {output_file}")
    
    def import_from_json(self, input_file: str):
        """Import data from JSON file"""
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for table_name, rows in data.items():
            if not rows:
                continue
            
            # Get column names from first row
            columns = list(rows[0].keys())
            placeholders = ','.join(['?' for _ in columns])
            sql = f"INSERT OR REPLACE INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
            
            # Convert dict rows to tuples
            values = [tuple(row[col] for col in columns) for row in rows]
            
            try:
                self.cursor.executemany(sql, values)
                self.conn.commit()
                print(f"✅ Imported {len(rows)} rows into {table_name}")
            except sqlite3.Error as e:
                print(f"⚠️ Error importing into {table_name}: {e}")
    
    def export_table_to_csv(self, table_name: str, output_file: str):
        """Export a table to CSV"""
        rows = self.query(f"SELECT * FROM {table_name}")
        
        if not rows:
            print(f"⚠️ No data in {table_name}")
            return
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✅ Exported {table_name} to {output_file}")
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        stats = {
            'tables': {},
            'total_rows': 0
        }
        
        for table in self.get_tables():
            count = self.get_row_count(table)
            stats['tables'][table] = count
            stats['total_rows'] += count
        
        return stats
    
    def clear_table(self, table_name: str):
        """Clear all data from a table"""
        self.execute(f"DELETE FROM {table_name}")
        print(f"✅ Cleared table: {table_name}")
    
    def clear_all_tables(self):
        """Clear all data from all tables"""
        for table in self.get_tables():
            self.clear_table(table)
        print("✅ All tables cleared")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✅ Database connection closed")

# ============================================================================
# NATURAL LANGUAGE SQL CONVERTER (for use with AI agent)
# ============================================================================

class NaturalLanguageSQL:
    """
    Convert natural language queries to SQL
    Requires AI agent with OpenAI API
    """
    
    def __init__(self, db: UseCaseDatabase, ai_client):
        self.db = db
        self.ai_client = ai_client
    
    def convert_to_sql(self, natural_query: str) -> str:
        """Convert natural language to SQL query"""
        # Get database schema
        schema_info = self._get_schema_description()
        
        # Generate SQL using AI
        prompt = f"""Convert this natural language query to SQL.

Database Schema:
{schema_info}

Natural Language Query: {natural_query}

Generate ONLY the SQL query, no explanations. Make it safe (read-only if possible)."""

        response = self.ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a SQL expert. Generate safe, efficient SQL queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=200
        )
        
        sql = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        sql = sql.replace("```sql", "").replace("```", "").strip()
        
        return sql
    
    def _get_schema_description(self) -> str:
        """Get human-readable schema description"""
        schema_parts = []
        
        for table in self.db.get_tables():
            columns = self.db.get_table_schema(table)
            col_desc = ", ".join([f"{col['name']} ({col['type']})" for col in columns])
            schema_parts.append(f"Table {table}: {col_desc}")
        
        return "\n".join(schema_parts)
    
    def query_natural_language(self, natural_query: str) -> List[Dict]:
        """Execute a natural language query"""
        sql = self.convert_to_sql(natural_query)
        print(f"Generated SQL: {sql}")
        
        # Validate it's a SELECT query (safety check)
        if not sql.strip().upper().startswith("SELECT"):
            print("⚠️ Only SELECT queries are allowed via natural language")
            return []
        
        return self.db.query(sql)

# ============================================================================
# DEMO & TESTING
# ============================================================================

def demo():
    """Demonstrate database functionality"""
    print("\n" + "="*50)
    print("DATABASE DEMO")
    print("="*50 + "\n")
    
    # Initialize database with e-commerce schema
    db = UseCaseDatabase("demo.db", "education")
    
    # Create schema
    db.setup_schema()
    
    # Load sample data
    db.load_sample_data()
    
    # Show statistics
    print("\n📊 Database Statistics:")
    stats = db.get_statistics()
    for table, count in stats['tables'].items():
        print(f"  - {table}: {count} rows")
    
    # Example queries
    print("\n🔍 Example Queries:\n")
    
    # 1. Get all products
    products = db.query("SELECT * FROM products LIMIT 3")
    print("Products:")
    for p in products:
        print(f"  - {p['name']}: ${p['price']}")
    
    # 2. Get orders with customer names
    orders = db.query("""
        SELECT o.id, c.name as customer, o.total_amount, o.status
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
    """)
    print("\nOrders:")
    for o in orders:
        print(f"  - Order #{o['id']} for {o['customer']}: ${o['total_amount']} ({o['status']})")
    
    # 3. Export to JSON
    print("\n💾 Exporting database...")
    db.export_to_json("demo_export.json")
    
    print("\n" + "="*50)
    print("Demo complete!")
    print("="*50)
    
    db.close()

if __name__ == "__main__":
    demo()
