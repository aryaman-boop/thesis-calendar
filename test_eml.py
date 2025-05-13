from datetime import datetime, timedelta

template = """From: school@uwindsor.ca
To: you@uwindsor.ca
Subject: MSc Thesis Proposal by: {name}
Date: {today}

{name} is presenting their MSc Thesis Proposal

{title}

MSc Thesis Proposal by: {name}

Date: {event_date}
Time: {event_time}
Location: {location}

Abstract:
{abstract}
"""

names = ["Alice Johnson", "Bob Singh", "Carlos Nguyen"]
titles = [
    "Improving LLMs with Edge-Aware Fine-Tuning",
    "Optimizing Neural Search with Compressed Memory Routing",
    "Sensor Fusion Techniques in Urban Drone Logistics"
]
locations = ["Essex Hall, Room 101", "Chrysler Hall, Room 305", "CEI, Room 210"]
abstract = "This research explores model optimization techniques for AI systems operating on non-IID data in distributed environments."

now = datetime.now()
for i in range(3):
    name = names[i]
    title = titles[i]
    loc = locations[i]
    dt = now + timedelta(days=i)
    date_str = dt.strftime("Thursday, %B %dth, %Y")
    time_str = dt.strftime("10:00 AM")
    eml_content = template.format(
        name=name,
        title=title,
        location=loc,
        event_date=date_str,
        event_time=time_str,
        abstract=abstract,
        today=dt.strftime("%a, %d %b %Y %H:%M:%S -0400")
    )
    with open(f"test_event_{i+1}.eml", "w") as f:
        f.write(eml_content)

print("✅ 3 test .eml files generated.")