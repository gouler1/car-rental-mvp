from database import SessionLocal
from models import Car
import random

db = SessionLocal()

brands_models = [
    ("Toyota", "Camry"), ("Hyundai", "Solaris"), ("Kia", "Rio"),
    ("Renault", "Logan"), ("Volkswagen", "Polo"), ("Lada", "Granta")
]

for _ in range(10):
    brand, model = random.choice(brands_models)
    car = Car(
        brand=brand,
        model=model,
        year=random.randint(2018, 2024),
        price_per_day=round(random.uniform(1500, 4000), 0),
        transmission=random.choice(["manual", "automatic"]),
        fuel_type=random.choice(["petrol", "hybrid"]),
        seats=random.choice([4, 5]),
        latitude=55.751244 + random.uniform(-0.05, 0.05),
        longitude=37.618423 + random.uniform(-0.05, 0.05)
    )
    db.add(car)

db.commit()
print("✅ 10 авто добавлено")
