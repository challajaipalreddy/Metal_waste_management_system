import mysql.connector
from mysql.connector import Error
from config import Config

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            port=Config.MYSQL_PORT
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    role ENUM('user', 'scrap_processor', 'buyer') NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    phone VARCHAR(20),
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create metal_waste table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metal_waste (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    metal_type VARCHAR(50) NOT NULL,
                    quantity DECIMAL(10,2) NOT NULL,
                    unit ENUM('kg', 'ton') NOT NULL,
                    description TEXT,
                    price DECIMAL(10,2),
                    status ENUM('available', 'processing', 'sold') DEFAULT 'available',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Create transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    waste_id INT NOT NULL,
                    buyer_id INT NOT NULL,
                    processor_id INT,
                    amount DECIMAL(10,2) NOT NULL,
                    status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (waste_id) REFERENCES metal_waste(id),
                    FOREIGN KEY (buyer_id) REFERENCES users(id),
                    FOREIGN KEY (processor_id) REFERENCES users(id)
                )
            """)
            
            # Create pickup_requests table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pickup_requests (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    waste_id INT NOT NULL,
                    user_id INT NOT NULL,
                    pickup_date DATE NOT NULL,
                    pickup_time TIME NOT NULL,
                    status ENUM('pending', 'scheduled', 'completed', 'cancelled') DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (waste_id) REFERENCES metal_waste(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Create messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sender_id INT NOT NULL,
                    receiver_id INT NOT NULL,
                    message TEXT NOT NULL,
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sender_id) REFERENCES users(id),
                    FOREIGN KEY (receiver_id) REFERENCES users(id)
                )
            """)
            
            connection.commit()
            print("Database tables created successfully!")
            
        except Error as e:
            print(f"Error creating tables: {e}")
        finally:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    init_db() 