# push_districts.py
from pressroom.models import District

districts = [
    "Hyderabad",
    "Ranga Reddy",
    "Medchal",
    "Adilabad",
    "Bhadradri Kothagudem",
    "Jagtial",
    "Jangaon",
    "Jogulamba Gadwal",
    "Kamareddy",
    "Karimnagar",
    "Khammam",
    "Mahabubabad",
    "Mahabubnagar",
    "Mancherial",
    "Medak",
    "Mulugu",
    "Nagarkurnool",
    "Nalgonda",
    "Narayanpet",
    "Nizamabad",
    "Peddapalli",
    "Rajanna Sircilla",
    "Sangareddy",
    "Siddipet",
    "Suryapet",
    "Vikarabad",
    "Wanaparthy",
    "Warangal Rural",
    "Warangal Urban",
    "Yadadri Bhuvanagiri"
]

for name in districts:
    District.objects.get_or_create(name=name)

print("✅ Districts inserted successfully!")
