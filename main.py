from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from database import get_connection, initialize_database
from models import EmployeeCreate, EmployeeDelete
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:5500",
    "http://127.0.0.1",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    try:
        initialize_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

# Serve frontend
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Frontend not found")

# API Endpoints
@app.post("/add-employee")
async def add_employee(emp: EmployeeCreate):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            INSERT INTO employees (first_name, middle_name, last_name, position, company_id, site_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (emp.first_name, emp.middle_name, emp.last_name, emp.position, emp.company_id, emp.site_id))
        conn.commit()
        return {"message": "Employee added successfully"}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error adding employee: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.delete("/remove-employee")
async def remove_employee(emp: EmployeeDelete):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM employees WHERE id = %s", (emp.id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Employee not found")
        conn.commit()
        return {"message": "Employee removed successfully"}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error removing employee: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/employees/by-company/{company_id}")
async def get_employees_by_company(company_id: int):
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
        results = cursor.fetchall()
        if not results:
            raise HTTPException(status_code=404, detail="No employees found for this company")
        return results
    except Exception as e:
        logger.error(f"Error fetching employees: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/employees/by-site/{site_id}")
async def get_employees_by_site(site_id: int):
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
        results = cursor.fetchall()
        if not results:
            raise HTTPException(status_code=404, detail="No employees found for this site")
        return results
    except Exception as e:
        logger.error(f"Error fetching employees: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
