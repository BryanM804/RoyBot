roy_count = 0

try:
    with open("roy_count.txt", "r") as roy_file:
        contents = roy_file.read().split(":")
        if "count" in contents:
            roy_count = int(contents[1])
except FileNotFoundError:
    print("No count file found, starting count from 0.")

def save_count():
    with open("roy_count.txt", "w") as roy_file:
        roy_file.write(f"count:{roy_count}")
        print(f"Saved count at roy #{roy_count}")

def inc_count(count):
    global roy_count 
    roy_count += 1
    if roy_count % 5 == 0:
        save_count()