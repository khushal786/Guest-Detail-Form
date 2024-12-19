import psycopg2
import pandas as pd

# PostgreSQL connection setup
def get_db_connection():
    connection = psycopg2.connect(
        host="localhost",
        database="kd",
        user="khushal",
        password="khushal@108"
    )
    return connection

# Fetch data from PostgreSQL
def fetch_data_from_db():
    conn = get_db_connection()
    query = "SELECT * FROM guest_data"  # Replace with your table name
    data = pd.read_sql(query, conn)
    conn.close()
    return data

# Save data to CSV
def save_to_csv(data, file_name="guest_data.csv"):
    data.to_csv(file_name, index=False)
    print(f"Data has been saved to {file_name}")

# Main workflow
if __name__ == "__main__":
    # Fetch data from the database
    data = fetch_data_from_db()

    # Save to CSV
    save_to_csv(data)
