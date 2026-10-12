# Get the current date and time
import datetime
now = datetime.datetime.now()
print("Current date and time:")
print(now)
# Extract useful parts
print("Year:", now.year)
print("Month:", now.month)
print("Day:", now.day)
print("Hour:", now.hour)
print("Minute:", now.minute)
# Example: Reminder if today is Friday
if now.weekday() == 4:   # 0 = Monday, 4 = Friday
   print("Reminder: Today is Friday! Check weekly report.")