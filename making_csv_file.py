import csv

with open('Entry_time.csv', 'x', newline='') as file:
    writer = csv.writer(file)
    columns = ['ID', "Name", "Entry time"]
    writer.writerow(columns)

    # print(f"CSV file '{filename}' created with columns: {', '.join(columns)}")

with open('Exit_time.csv', 'x', newline='') as file:
    writer = csv.writer(file)
    columns = ['ID', "Name", "Exit time"]
    writer.writerow(columns)

# Example usage

