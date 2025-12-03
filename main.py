from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db, Base, engine
from models import User
from schemas import UserCreate, Token, BookingCreate, Car
from auth import create_access_token, authenticate_user
from crud import create_user, get_cars, get_car, create_booking
from config import STRIPE_PUBLIC_KEY, FRONTEND_URL
import stripe

# Инициализация Stripe (тестовый режим)
stripe.api_key = "sk_test_..."  # ЗАМЕНИ НА СВОЙ sk_test_... из .env позже

app = FastAPI()

# Подключаем статику и шаблоны
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Защита маршрутов — простая (для MVP)
def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401)
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401)
        return user
    except Exception:
        raise HTTPException(status_code=401)

# === Роуты ===

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"}, status_code=400)
    token = create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/profile", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=1800)
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    user_data = UserCreate(
        email=form["email"],
        password=form["password"],
        full_name=form["full_name"],
        phone=form.get("phone")
    )
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Email already registered"}, status_code=400)
    create_user(db, user_data)
    return RedirectResponse(url="/login", status_code=303)

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response

@app.get("/cars", response_class=HTMLResponse)
async def cars_page(request: Request, db: Session = Depends(get_db)):
    cars = get_cars(db)
    return templates.TemplateResponse("cars.html", {"request": request, "cars": cars})

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

# === Stripe: создание сессии оплаты ===
@app.post("/create-checkout-session")
async def create_checkout_session(
    request: Request,
    booking_data: BookingCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Создаём бронь в статусе "pending"
    booking = create_booking(db, booking_data, user.id)

    # Создаём Stripe-сессию
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "rub",
                "product_data": {"name": f"Аренда авто ID {booking.car_id}"},
                "unit_amount": int(booking.total_price * 100),  # в копейках
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=f"{FRONTEND_URL}/booking/success?id={booking.id}",
        cancel_url=f"{FRONTEND_URL}/cars",
        metadata={"booking_id": booking.id},
    )
    return {"url": session.url}

# Вебхук (опционально, но для MVP можно обойтись success_url)
# В реальном проекте — webhook для подтверждения оплаты
