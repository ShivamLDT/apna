
import sqlite3

# Array of strings to match against the family_name column
familyNames = ["pdf", "xlsx", "Williams", "Jones", "Brown"]

# Connect to the SQLite database
# (Replace 'your_database.db' with the actual database file name)
conn = sqlite3.connect("D:\\PyRepos\\FlaskWebProject3\\FlaskWebProject3\\26d1bc626d2bdccc8874b7da3e914d9a4053f7975d83845aa70e74395ba3719c.db")
cursor = conn.cursor()

# Construct the SQL query directly with the LIKE clauses
query = "SELECT * FROM backups WHERE name = 1717235820.3287108 and (" + " OR ".join([f"full_file_name LIKE '%{name}'" for name in familyNames]) +")"

# Print the constructed query for verification
print("Constructed Query:", query)

# Execute the query
cursor.execute(query)

# Fetch all matching records
results = cursor.fetchall()

# Print the results
for row in results:
    print(row[8])

# Close the connection
conn.close()
