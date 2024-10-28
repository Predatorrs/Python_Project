import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import psycopg2
from datetime import datetime, timedelta
import random

# Funkcja do łączenia z bazą danych PostgreSQL
def connect_to_postgresql():
    try:
        connection = psycopg2.connect(
            dbname="Moja_Baza_Danych",    
            user="postgres",         
            password="niedowierzalny12!",  
            host="localhost",
            port="5432"
        )
        print("Połączono z PostgreSQL")
        return connection
    except Exception as error:
        print("Błąd połączenia:", error)
        return None

# Funkcja do odczytu danych z bazy
def read_data():
    connection = connect_to_postgresql()
    if connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM rezerwacje")
            records = cursor.fetchall()
            
            # Czyszczenie istniejących wierszy w tabeli
            for row in data_table.get_children():
                data_table.delete(row)
            
            # Dodawanie wierszy z bazy do tabeli
            for record in records:
                data_table.insert("", "end", values=record)
        
        connection.close()
        print("Odczytano dane z bazy danych!")
    else:
        messagebox.showerror("Błąd", "Nie udało się połączyć z bazą danych.")

# Funkcja do zapisu danych do bazy (dodanie nowej rezerwacji)
def save_data():
    date = date_var.get()
    timeslot = timeslot_var.get()

    if not date or not timeslot:
        messagebox.showerror("Błąd", "Wprowadź datę i przedział czasowy!")
        return

    connection = connect_to_postgresql()
    if connection:
        with connection.cursor() as cursor:
            # Losowanie unikalnego numeru spotkania
            unique_number = None
            while True:
                proposed_number = random.randint(1, 100)
                cursor.execute("SELECT COUNT(*) FROM rezerwacje WHERE opis = %s", (f"Spotkanie {proposed_number}",))
                if cursor.fetchone()[0] == 0:
                    unique_number = proposed_number
                    break

            # Sprawdzanie, czy wybrany przedział czasowy jest wolny
            cursor.execute(
                "SELECT COUNT(*) FROM rezerwacje WHERE date = %s AND przedzial_czasowy = %s",
                (date, timeslot)
            )
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Błąd", "Wybrany przedział czasowy jest już zajęty!")
                connection.close()
                return

            # Wstawianie danych do tabeli
            cursor.execute(
                "INSERT INTO rezerwacje (date, przedzial_czasowy, opis, status) VALUES (%s, %s, %s, %s)",
                (date, timeslot, f"Spotkanie {unique_number}", 'potwierdzony')
            )
        connection.commit()
        connection.close()
        messagebox.showinfo("Sukces", "Rezerwacja dodana pomyślnie!")
        read_data()
    else:
        messagebox.showerror("Błąd", "Nie udało się połączyć z bazą danych.")

# Funkcja do sprawdzania dostępności terminu
def check_availability():
    date = date_var.get()
    timeslot = timeslot_var.get()

    if not date or not timeslot:
        messagebox.showerror("Błąd", "Wybierz datę i przedział czasowy!")
        return

    connection = connect_to_postgresql()
    if connection:
        with connection.cursor() as cursor:
            # Sprawdzanie, czy wybrany przedział czasowy jest wolny
            cursor.execute(
                "SELECT * FROM rezerwacje WHERE date = %s AND przedzial_czasowy = %s",
                (date, timeslot)
            )
            records = cursor.fetchall()

            # Czyszczenie istniejących wierszy w tabeli
            for row in data_table.get_children():
                data_table.delete(row)

            if records:
                messagebox.showinfo("Wynik", "Wybrany termin jest zajęty!")
                for record in records:
                    data_table.insert("", "end", values=record)
            else:
                messagebox.showinfo("Wynik", "Wybrany termin jest wolny.")
        
        connection.close()
    else:
        messagebox.showerror("Błąd", "Nie udało się połączyć z bazą danych.")

# Tworzymy główne okno aplikacji
root = tk.Tk()
root.title("Rezerwacje")

# Rozmiaru okna
root.geometry("1000x500")  

# Ramka na przyciski i pola
button_frame = tk.Frame(root)
button_frame.pack(side="left", fill="y", padx=10, pady=10)

# Przycisk do odczytu danych z bazy
read_button = tk.Button(button_frame, text="Odczytaj dane z bazy", command=read_data)
read_button.pack(pady=10)

# Lista rozwijana do wyboru daty
date_label = tk.Label(button_frame, text="Data:")
date_label.pack(pady=5)

# Generowanie dat do wyboru (30 dni od dzisiaj)
dates = [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30)]
date_var = tk.StringVar(value=dates[0])
date_dropdown = tk.OptionMenu(button_frame, date_var, *dates)
date_dropdown.pack(pady=5)

# Lista rozwijana do wyboru przedziału czasowego
timeslot_label = tk.Label(button_frame, text="Przedział czasowy:")
timeslot_label.pack(pady=5)

# Generowanie przedziałów czasowych do wyboru
time_slots = ["09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00"]
timeslot_var = tk.StringVar(value=time_slots[0])
timeslot_dropdown = tk.OptionMenu(button_frame, timeslot_var, *time_slots)
timeslot_dropdown.pack(pady=5)

# Przycisk do zapisu danych do bazy
save_button = tk.Button(button_frame, text="Zapisz dane do bazy", command=save_data)
save_button.pack(pady=10)

# Przycisk do sprawdzania dostępności terminu
check_button = tk.Button(button_frame, text="Sprawdź dostępność", command=check_availability)
check_button.pack(pady=10)

# Tworzenie ramki na tabelkę
table_frame = tk.Frame(root)
table_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

# Tworzenie tabelki przy użyciu Treeview
data_table = ttk.Treeview(table_frame, columns=("ID", "Date", "Przedział czasowy", "Opis", "Status"), show="headings")
data_table.heading("ID", text="ID")
data_table.heading("Date", text="Data")
data_table.heading("Przedział czasowy", text="Przedział czasowy")
data_table.heading("Opis", text="Opis")
data_table.heading("Status", text="Status")

# Ustawienie szerokości kolumn
data_table.column("ID", width=50)
data_table.column("Date", width=100)
data_table.column("Przedział czasowy", width=120)
data_table.column("Opis", width=200)
data_table.column("Status", width=100)

# Dodanie tabelki do okna
data_table.pack(fill="both", expand=True)

# Uruchomienie głównej pętli aplikacji
root.mainloop()

