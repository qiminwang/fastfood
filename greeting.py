time_now = time.localtime().tm_hour

if 7 <= time_now <= 11:
    print("Good Morning")

elif 12 <= time_now <= 19:
    print("Good Afternoon")

else:
    print("Good Night")
