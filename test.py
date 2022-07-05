from datetime import datetime
import re
now = datetime.now()
current_time = now.strftime("%H:%M")

if current_time == "04:47":
    print(current_time)
