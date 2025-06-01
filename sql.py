import mysql.connector

# Connect to the database
db = mysql.connector.connect(
    host="localhost",        # Change if needed
    user="root",    # Your DB username
    password="kucingku",# Your DB password
    database="mtu_smart_classroom"
)

# Create a cursor
cursor = db.cursor()

# Execute the query
query = "SELECT * FROM room_reservations"
cursor.execute(query)

# Fetch all results
results = cursor.fetchall()

# Column names (optional but nice)
column_names = [i[0] for i in cursor.description]

# Print header
print(" | ".join(column_names))
print("-" * 60)

# Print each row
for row in results:
    print(" | ".join(str(cell) for cell in row))

# Close connection
cursor.close()
db.close()
