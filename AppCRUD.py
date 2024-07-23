import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import sqlite3

class EmpleadosDB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS empleados (
                id INTEGER PRIMARY KEY,
                nombre TEXT,
                cargo TEXT,
                salario REAL
            )
        """)
        self.conn.commit()

    def execute_query(self, query, *args):
        try:
            self.cursor.execute(query, args)
            self.conn.commit()
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Error de base de datos", str(e))

    def fetch_all_employees(self):
        return self.execute_query("SELECT * FROM empleados")

class EmpleadosCRUD:
    def __init__(self, root):
        self.root = root
        self.root.title('Gestión de Empleados')
        
        self.db = EmpleadosDB("empleados.db")
        self.create_widgets()
        self.load_employees()
        
    def create_widgets(self):
        self.create_treeview()
        self.create_input_fields()
        self.create_buttons()
        
    def create_treeview(self):
        self.tree = ttk.Treeview(self.root, columns=("ID", "Nombre", "Cargo", "Salario"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Cargo", text="Cargo")
        self.tree.heading("Salario", text="Salario")
        self.tree.pack(padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def create_input_fields(self):
        fields = [("Nombre:", 30), ("Cargo:", 30), ("Salario:", 15)]
        self.entries = {}
        for label_text, width in fields:
            label = ttk.Label(self.root, text=label_text)
            label.pack(pady=(0, 5), padx=10, anchor="w")

            entry = ttk.Entry(self.root, width=width)
            entry.pack(pady=(0, 10), padx=10, fill="x")
            self.entries[label_text] = entry

    def create_buttons(self):
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        buttons = [("Agregar", self.add_employee), 
                ("Eliminar", self.remove_employee),
                ("Actualizar", self.update_employee), 
                ("Buscar", self.search_employee),
                ("Mostrar Todo", self.show_all_employees)]

        for text, command in buttons:
            button = ttk.Button(btn_frame, text=text, command=command)
            button.grid(row=0, column=buttons.index((text, command)), padx=5)

    def load_employees(self):
        self.clear_table()
        for row in self.db.fetch_all_employees():
            self.tree.insert("", "end", values=row)

    def add_employee(self):
        values = [entry.get() for entry in self.entries.values()]
        if all(values):
            self.db.execute_query("INSERT INTO empleados (nombre, cargo, salario) VALUES (?, ?, ?)", *values)
            messagebox.showinfo("Éxito", "Empleado agregado con éxito")
            self.load_employees()
            self.clear_input_fields()
        else:
            messagebox.showerror("Error", "Por favor, complete todos los campos")

    def remove_employee(self):
        selected_item = self.tree.selection()
        if selected_item:
            employee_id = self.tree.item(selected_item, "values")[0]
            self.db.execute_query("DELETE FROM empleados WHERE id=?", employee_id)
            messagebox.showinfo("Éxito", "Empleado eliminado con éxito")
            self.load_employees()
        else:
            messagebox.showerror("Error", "Por favor, seleccione un registro para eliminar")

    def update_employee(self):
        selected_item = self.tree.selection()
        if selected_item:
            employee_id = self.tree.item(selected_item, "values")[0]
            values = [entry.get() for entry in self.entries.values()]
            self.db.execute_query("UPDATE empleados SET nombre=?, cargo=?, salario=? WHERE id=?", *(values + [employee_id]))
            messagebox.showinfo("Éxito", "Empleado actualizado con éxito")
            self.load_employees()
            self.clear_input_fields()
        else:
            messagebox.showerror("Error", "Por favor, seleccione un registro para actualizar")

    def search_employee(self):
        search_term = self.entries["Nombre:"].get()
        if search_term:
            self.clear_table()
            for row in self.db.execute_query("SELECT * FROM empleados WHERE nombre LIKE ?", '%' + search_term + '%'):
                self.tree.insert("", "end", values=row)
        else:
            messagebox.showerror("Error", "Por favor, ingrese un término de búsqueda")

    def show_all_employees(self):
        self.load_employees()

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            if values:
                for entry, value in zip(self.entries.values(), values[1:]):
                    entry.delete(0, tk.END)
                    entry.insert(0, value)

    def clear_input_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

if __name__ == '__main__':
    root = tk.Tk()
    app = EmpleadosCRUD(root)
    root.mainloop()