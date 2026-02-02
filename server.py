from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pyodbc

app = FastAPI(title="Вендинг API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Подключение к MSSQL LocalDB
def get_db_connection():
    conn = pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=(localdb)\\MSSQLLocalDB;"
        "Database=vending_db;"
        "Trusted_Connection=yes;"
    )
    return conn

# Модель для валидации
class Machine(BaseModel):
    serial_number: str
    inventory_number: str
    name: str
    model: str
    location: str
    address: str
    status: str = "Работает"

# Главная страница
@app.get("/")
def home():
    return {"message": "Сервер работает", "документация": "/docs"}

# Получить все ТА
@app.get("/machines")
def get_machines():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM machines")
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "serial_number": r[1],
            "inventory_number": r[2],
            "name": r[3],
            "model": r[4],
            "location": r[5],
            "address": r[6],
            "status": r[7]
        }
        for r in rows
    ]

# Добавить новый ТА
@app.post("/machines")
def add_machine(machine: Machine):
    conn = get_db_connection()
    cur = conn.cursor()

    # Проверка дубликатов
    cur.execute("SELECT id FROM machines WHERE serial_number = ?", (machine.serial_number,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(400, "ТА с таким серийным номером уже существует")

    cur.execute("SELECT id FROM machines WHERE inventory_number = ?", (machine.inventory_number,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(400, "ТА с таким инвентарным номером уже существует")

    # Вставка
    cur.execute('''
        INSERT INTO machines (serial_number, inventory_number, name, model, location, address, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        machine.serial_number,
        machine.inventory_number,
        machine.name,
        machine.model,
        machine.location,
        machine.address,
        machine.status
    ))

    conn.commit()
    conn.close()
    return {"message": "ТА добавлен"}

# Изменить статус
@app.put("/machines/{machine_id}/status")
def update_status(machine_id: int, new_status: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE machines SET status = ? WHERE id = ?", (new_status, machine_id))

    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(404, "ТА не найден")

    conn.commit()
    conn.close()
    return {"message": f"Статус обновлён на '{new_status}'"}

if __name__ == "__main__":
    print("\n🚀 Сервер запущен: http://localhost:8000")
    print("📖 Документация: http://localhost:8000/docs\n")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)