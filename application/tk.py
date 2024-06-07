import tkinter as tk
from tkinter import ttk
import requests


class RestaurantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Management System")

        # Create notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True, fill=tk.BOTH)

        # Customer tab
        self.customer_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.customer_frame, text="Customers")
        self.create_customer_widgets()

        # # Meal tab
        # self.meal_frame = ttk.Frame(self.notebook)
        # self.notebook.add(self.meal_frame, text="Meals")
        # self.create_meal_widgets()

        # # Order tab
        # self.order_frame = ttk.Frame(self.notebook)
        # self.notebook.add(self.order_frame, text="Orders")
        # self.create_order_widgets()

    def create_customer_widgets(self):
        # Customer Entry Widgets
        self.customer_name_entry = ttk.Entry(self.customer_frame)
        self.customer_name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.customer_phone_entry = ttk.Entry(self.customer_frame)
        self.customer_phone_entry.grid(row=1, column=1, padx=5, pady=5)

        # Customer Labels
        ttk.Label(self.customer_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Label(self.customer_frame, text="Phone Number:").grid(row=1, column=0, padx=5, pady=5, sticky="e")

        # Customer Buttons
        ttk.Button(self.customer_frame, text="Add Customer", command=self.add_customer).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Customer Treeview
        self.customer_tree = ttk.Treeview(self.customer_frame, columns=("ID", "Name", "Phone Number"))
        self.customer_tree.heading("#0", text="ID")
        self.customer_tree.heading("ID", text="ID")
        self.customer_tree.heading("Name", text="Name")
        self.customer_tree.heading("Phone Number", text="Phone Number")
        self.customer_tree.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    # def create_meal_widgets(self):
    #     # Meal Entry Widgets
    #     self.meal_name_entry = ttk.Entry(self.meal_frame)
    #     self.meal_name_entry.grid(row=0, column=1, padx=5, pady=5)
    #     self.meal_price_entry = ttk.Entry(self.meal_frame)
    #     self.meal_price_entry.grid(row=1, column=1, padx=5, pady=5)

    #     # Meal Labels
    #     ttk.Label(self.meal_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    #     ttk.Label(self.meal_frame, text="Price:").grid(row=1, column=0, padx=5, pady=5, sticky="e")

    #     # Meal Buttons
    #     ttk.Button(self.meal_frame, text="Add Meal", command=self.add_meal).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    #     # Meal Treeview
    #     self.meal_tree = ttk.Treeview(self.meal_frame, columns=("ID", "Name", "Price"))
    #     self.meal_tree.heading("#0", text="ID")
    #     self.meal_tree.heading("ID", text="ID")
    #     self.meal_tree.heading("Name", text="Name")
    #     self.meal_tree.heading("Price", text="Price")
    #     self.meal_tree.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    # def create_order_widgets(self):
    #     # Order Entry Widgets
    #     self.order_phone_entry = ttk.Entry(self.order_frame)
    #     self.order_phone_entry.grid(row=0, column=1, padx=5, pady=5)
    #     self.order_total_price_entry = ttk.Entry(self.order_frame)
    #     self.order_total_price_entry.grid(row=1, column=1, padx=5, pady=5)

        # # Order Labels
        # ttk.Label(self.order_frame, text="Phone Number:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        # ttk.Label(self.order_frame, text="Total Price:").grid(row=1, column=0, padx=5, pady=5, sticky="e")

        # # Order Buttons
        # ttk.Button(self.order_frame, text="Add Order", command=self.add_order).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # # Order Treeview
        # self.order_tree = ttk.Treeview(self.order_frame, columns=("ID", "Phone Number", "Total Price"))
        # self.order_tree.heading("#0", text="ID")
        # self.order_tree.heading("ID", text="ID")
        # self.order_tree.heading("Phone Number", text="Phone Number")
        # self.order_tree.heading("Total Price", text="Total Price")
        # self.order_tree.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def add_customer(self):
        name = self.customer_name_entry.get()
        phone_number = self.customer_phone_entry.get()
        data = {"name": name, "phone_number": phone_number}
        response = requests.post("http://127.0.0.1:8001/customers", json=data)
        if response.status_code == 201:
            self.load_customers()

    def load_customers(self):
        self.customer_tree.delete(*self.customer_tree.get_children())
        response = requests.get("http://127.0.0.1:8001/customers")
        customers = response.json()
        for customer in customers:
            self.customer_tree.insert("", "end", text=customer["id"], values=(customer["id"], customer["name"], customer["phone_number"]))

#     def add_meal(self):
#         name = self.meal_name_entry.get()
#         price = float(self.meal_price_entry.get())
#         data = {"name": name, "price": price}
#         response = requests.post("http://127.0.0.1:8001/meals", json=data)
#         if response.status_code == 201:
#             self.load_meals()

#     def load_meals(self):
#         self.meal_tree.delete(*self.meal_tree.get_children())
#         response = requests.get("http://127.0.0.1:8001/meals")
#         meals = response.json()
#         for meal in meals:
#             self.meal_tree.insert("", "end", text=meal["id"], values=(meal["id"], meal["name"], meal["price"]))

#     def add_order(self):
#         phone_number = self.order_phone_entry.get()
#         total_price = float(self.order_total_price_entry.get())
#         data = {"phone_number": phone_number, "total_price": total_price}
#         response = requests.post("http://127.0.0.1:8001/orders", json=data)
#         if response.status_code == 201:
#             self.load_orders()

#     def load_orders(self):
#         self.order_tree.delete(*self.order_tree.get_children())
#         response = requests.get("http://127.0.0.1:8001/orders")
#         orders = response.json()
#         for order in orders:
#             self.order_tree.insert("", "end", text=order["id"], values=(order["id"], order["phone_number"], order["total_price"]))

if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantApp(root)
    app.load_customers()
#     app.load_meals()
#     app.load_orders()
    root.mainloop()
