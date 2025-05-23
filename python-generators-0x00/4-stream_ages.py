from seed import connect_to_prodev

def stream_user_ages():
    connection = connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT age FROM user_data")

    for (age) in cursor:
        yield age

    connection.close()

def compute_average_age():
    total = 0
    count = 0

    for age in stream_user_ages():
        total += age
        count += 1
    
    if count == 0:
        print("Average age of users: 0")
    else:
        average = total / count
        print(f"Average age of users: {average:.2f}")

if __name__ == "__main__":
    compute_average_age()
    