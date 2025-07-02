from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from database import get_connection
from models import EmployeeCreate, EmployeeDelete

app = FastAPI()

# Allow CORS for development – remove "*" in production
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1",
    "http://localhost",
    "*"  # ⚠️ remove this in production for security
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Serve index.html at root "/"
@app.get("/", response_class=HTMLResponse)
def serve_index():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="index.html not found")

# ✅ Add Employee
@app.post("/add-employee")
def add_employee(emp: EmployeeCreate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO employees (first_name, middle_name, last_name, position, company_id, site_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (emp.first_name, emp.middle_name, emp.last_name, emp.position, emp.company_id, emp.site_id))
        conn.commit()
        return {"message": "Employee added successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ✅ Remove Employee
@app.delete("/remove-employee")
def remove_employee(emp: EmployeeDelete):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM employees WHERE id = %s", (emp.id,))
        conn.commit()
        return {"message": "Employee removed successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ✅ Get Employees by Company
@app.get("/employees/by-company/{company_id}")
def get_employees_by_company(company_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT e.*, c.name as company_name, s.name as site_name
            FROM employees e
            JOIN companies c ON e.company_id = c.id
            JOIN sites s ON e.site_id = s.id
            WHERE e.company_id = %s
        """, (company_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

# ✅ Get Employees by Site
@app.get("/employees/by-site/{site_id}")
def get_employees_by_site(site_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT e.*, c.name as company_name, s.name as site_name
            FROM employees e
            JOIN companies c ON e.company_id = c.id
            JOIN sites s ON e.site_id = s.id
            WHERE e.site_id = %s
        """, (site_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
