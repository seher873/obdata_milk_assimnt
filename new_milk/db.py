import sqlite3
from dataclasses import dataclass
from typing import List, Tuple

# Data class to store a milk entry
@dataclass
class MilkEntry:
    customer_name: str
    start_date: str
    end_date: str
    morning_mound: float
    morning_sair: int
    morning_rate: float
    evening_mound: float
    evening_sair: int
    evening_rate: float
    rent: float
    commission: float
    bandi: float
    paid_amount: float

class MilkDatabase:
    def __init__(self, db_name="milk_dairy.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS milk_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            start_date TEXT,
            end_date TEXT,
            morning_mound REAL,
            morning_sair INTEGER,
            morning_rate REAL,
            evening_mound REAL,
            evening_sair INTEGER,
            evening_rate REAL,
            rent REAL,
            commission REAL,
            bandi REAL,
            paid_amount REAL
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def insert_entry(self, entry: MilkEntry):
        query = """
        INSERT INTO milk_entries (
            customer_name, start_date, end_date,
            morning_mound, morning_sair, morning_rate,
            evening_mound, evening_sair, evening_rate,
            rent, commission, bandi, paid_amount
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.conn.execute(query, (
            entry.customer_name,
            entry.start_date,
            entry.end_date,
            entry.morning_mound,
            entry.morning_sair,
            entry.morning_rate,
            entry.evening_mound,
            entry.evening_sair,
            entry.evening_rate,
            entry.rent,
            entry.commission,
            entry.bandi,
            entry.paid_amount
        ))
        self.conn.commit()

    def get_weekly_report(self, start_date: str, end_date: str) -> List[Tuple]:
        query = """
        SELECT * FROM milk_entries
        WHERE start_date BETWEEN ? AND ?
        ORDER BY start_date
        """
        cur = self.conn.cursor()
        cur.execute(query, (start_date, end_date))
        return cur.fetchall()

    def get_daily_report(self, selected_date: str) -> List[Tuple]:
        query = """
        SELECT * FROM milk_entries
        WHERE start_date = ?
        ORDER BY customer_name
        """
        cur = self.conn.cursor()
        cur.execute(query, (selected_date,))
        return cur.fetchall()

    def get_monthly_report(self, month: str) -> List[Tuple]:
        query = f"""
        SELECT * FROM milk_entries
        WHERE strftime('%m', start_date) = ?
        ORDER BY start_date
        """
        cur = self.conn.cursor()
        cur.execute(query, (month,))
        return cur.fetchall()

    def get_customer_entries(self, customer_name: str) -> List[Tuple]:
        query = """
        SELECT * FROM milk_entries
        WHERE customer_name = ?
        ORDER BY start_date
        """
        cur = self.conn.cursor()
        cur.execute(query, (customer_name,))
        return cur.fetchall()
