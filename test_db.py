from database import get_db_connection, init_db

def test_database():
    try:
        # Initialize database and create tables
        print("Initializing database...")
        init_db()
        print("Database initialized successfully!")

        # Get database connection
        print("\nTesting database connection...")
        conn = get_db_connection()
        cursor = conn.cursor()

        # Test 1: Check if tables exist
        print("\nChecking tables...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Found tables:", [table[0] for table in tables])

        # Test 2: Insert test data
        print("\nInserting test data...")
        # Insert test user
        cursor.execute("""
            INSERT INTO users (username, password, role, email, phone, address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, ('testuser', 'testpass', 'seller', 'test@example.com', '1234567890', 'Test Address'))
        user_id = cursor.lastrowid
        print(f"Inserted test user with ID: {user_id}")

        # Insert test metal waste
        cursor.execute("""
            INSERT INTO metal_waste (user_id, metal_type, quantity, unit, description, price)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, 'Copper', 100.00, 'kg', 'High quality copper scrap', 500.00))
        waste_id = cursor.lastrowid
        print(f"Inserted test metal waste with ID: {waste_id}")

        # Test 3: Query the data
        print("\nQuerying test data...")
        cursor.execute("SELECT * FROM users WHERE username = 'testuser'")
        user = cursor.fetchone()
        print("User data:", user)

        cursor.execute("SELECT * FROM metal_waste WHERE user_id = %s", (user_id,))
        waste = cursor.fetchone()
        print("Metal waste data:", waste)

        # Test 4: Clean up test data
        print("\nCleaning up test data...")
        cursor.execute("DELETE FROM metal_waste WHERE id = %s", (waste_id,))
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        print("Test data cleaned up successfully!")

        # Commit changes
        conn.commit()
        print("\nAll tests completed successfully!")

    except Exception as e:
        print(f"Error during testing: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print("\nDatabase connection closed.")

if __name__ == "__main__":
    test_database() 