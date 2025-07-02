import mysql.connector
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT"))
    )

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Create tables if they don't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INT PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sites (
            id INT PRIMARY KEY,
            company_id INT NOT NULL,
            name VARCHAR(255) NOT NULL,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(255) NOT NULL,
            middle_name VARCHAR(255),
            last_name VARCHAR(255) NOT NULL,
            position VARCHAR(255) NOT NULL,
            company_id INT NOT NULL,
            site_id INT NOT NULL,
            FOREIGN KEY (company_id) REFERENCES companies(id),
            FOREIGN KEY (site_id) REFERENCES sites(id)
        )
        """)
        
        # Insert default companies and sites
        companies = [
            (1, 'INNO'),
            (2, 'SRLH'),
            (3, 'CORELINK'),
            (4, 'HBLX')
        ]
        
        sites = [
            (1, 1, 'Head'), (2, 1, 'Koye'), (3, 1, 'Kilinto'),
            (4, 1, 'Bole Lemi'), (5, 1, 'Gelan'), (6, 1, 'Sebeta'),
            (7, 2, 'Head'), (8, 2, 'Debrebrihan'),
            (9, 3, 'Head'), (10, 3, 'Kilinto'),
            (11, 4, 'Head')
        ]
        
        cursor.executemany("""
        INSERT IGNORE INTO companies (id, name)
        VALUES (%s, %s)
        """, companies)
        
        cursor.executemany("""
        INSERT IGNORE INTO sites (id, company_id, name)
        VALUES (%s, %s, %s)
        """, sites)
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
