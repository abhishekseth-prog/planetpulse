from database import get_connection

connection = get_connection()

print("MySQL connection successful!")

connection.close()