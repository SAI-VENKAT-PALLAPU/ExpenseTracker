import sqlite3
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt


# ---------------- Database Setup ---------------- #
def init_db():
    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            amount REAL,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()


# ---------------- Expense Functions ---------------- #
def add_expense():
    category = category_var.get()
    amount = amount_var.get()

    if not category or not amount:
        messagebox.showwarning("Input Error", "Please enter all fields!")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number!")
        return

    date = datetime.date.today().strftime("%Y-%m-%d")

    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)",
                (category, amount, date))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Expense added successfully!")
    category_var.set("")
    amount_var.set("")
    load_expenses()


def load_expenses():
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM expenses")
    rows = cur.fetchall()
    conn.close()

    for row in rows:
        tree.insert("", tk.END, values=row)


def show_summary():
    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()
    cur.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        messagebox.showwarning("No Data", "No expenses to summarize!")
        return

    summary_win = tk.Toplevel(root)
    summary_win.title("Category Summary")

    tk.Label(summary_win, text="Category-wise Summary", font=("Arial", 14, "bold")).pack(pady=10)

    for row in rows:
        tk.Label(summary_win, text=f"{row[0]}: ₹{row[1]:.2f}", font=("Arial", 12)).pack(anchor="w")

    # Plot pie chart
    categories = [row[0] for row in rows]
    amounts = [row[1] for row in rows]
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title("Expense Distribution")
    plt.show()


# ---------------- GUI Setup ---------------- #
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("600x500")

init_db()

# Input Frame
frame = tk.Frame(root, pady=10)
frame.pack()

tk.Label(frame, text="Category:").grid(row=0, column=0, padx=5)
category_var = tk.StringVar()
tk.Entry(frame, textvariable=category_var).grid(row=0, column=1, padx=5)

tk.Label(frame, text="Amount (₹):").grid(row=0, column=2, padx=5)
amount_var = tk.StringVar()
tk.Entry(frame, textvariable=amount_var).grid(row=0, column=3, padx=5)

tk.Button(frame, text="Add Expense", command=add_expense, bg="green", fg="white").grid(row=0, column=4, padx=10)

# Table Frame
table_frame = tk.Frame(root)
table_frame.pack(fill="both", expand=True)

columns = ("ID", "Category", "Amount", "Date")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120, anchor="center")
tree.pack(fill="both", expand=True)

# Summary Button
tk.Button(root, text="Show Summary", command=show_summary, bg="blue", fg="white", font=("Arial", 12)).pack(pady=10)

# Load data initially
load_expenses()

root.mainloop()
