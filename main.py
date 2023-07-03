import tkinter as tk
from tkinter import ttk, font
from ttkthemes import ThemedTk
import os
import pandas as pd
from tkinter import messagebox
from custom_dialogs import AllInOneInputDialog
import logging
import sys
import numpy as np



class InventoryManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Manager")
        self.root.geometry("800x500")

        self.setup_fonts_and_styles()

        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(fill="both", expand=True)

        # Determine if running as script or compiled exe
        if getattr(sys, 'frozen', False):
            # If it's an exe, find the directory the exe is in
            application_path = os.path.dirname(sys.executable)
        else:
            # If it's a script, find the directory the script is in
            application_path = os.path.dirname(os.path.abspath(__file__))

        # Construct the full file paths
        self.inventory_file = os.path.join(application_path, 'inventory.xlsx')
        self.history_file = os.path.join(application_path, 'inventory_history.xlsx')

        logging.basicConfig(filename="inventory.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

        self.create_initial_files()

        self.setup_treeview()
        self.setup_buttons()
        self.setup_search_bar()

        self.update_treeview()

    def setup_fonts_and_styles(self):
        customFont = font.Font(family="Lora", size=20)
        style = ttk.Style(self.root)
        style.configure('.', font=customFont, paddings=10)

    def create_initial_files(self):
        try:
            if not os.path.exists(self.inventory_file):
                with pd.ExcelWriter(self.inventory_file, engine='openpyxl') as writer:
                    df = pd.DataFrame(columns=["Item Name", "Quantity", "Cost Price", "Sales Price", "Reorder Point"])
                    df.to_excel(writer, index=False)

            if not os.path.exists(self.history_file):
                with pd.ExcelWriter(self.history_file, engine='openpyxl') as writer:
                    df = pd.DataFrame(
                        columns=["Item Name", "Quantity Changed", "Cost Price", "Sales Price", "Change Type", "Timestamp"])
                    df.to_excel(writer, index=False)

        except Exception as e:
            error_message = f"Failed to create initial files. Error: {str(e)}"
            # Show the error message in a message box
            messagebox.showerror("Error", error_message)
            # Log the error
            logging.error(error_message)

    def setup_treeview(self):
        frame1 = ttk.Frame(self.top_frame)
        frame1.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.treeview = ttk.Treeview(frame1, columns=("Item Name", "Quantity", "Total Cost Price", "Total Sales Price"),
                                     show="headings")
        self.treeview.heading("Item Name", text="Item Name")
        self.treeview.heading("Quantity", text="Quantity @ CP")
        self.treeview.heading("Total Cost Price", text="Total Cost Price")
        self.treeview.heading("Total Sales Price", text="Total Sales Price")
        self.treeview.pack(fill="both", expand=True)

    def setup_buttons(self):
        frame2 = ttk.Frame(self.root)
        frame2.pack()
        # Buttons
        add_stock_button = ttk.Button(frame2, text="Add New Stock Item", command=self.show_add_stock_fields)
        add_stock_button.grid(row=0, column=1, padx=10, pady=10)

        increase_stock_button = ttk.Button(frame2, text="Increase Stock", command=self.increase_stock)
        increase_stock_button.grid(row=0, column=0, padx=10, pady=10)

        decrease_stock_button = ttk.Button(frame2, text="Make Sale", command=self.decrease_stock)
        decrease_stock_button.grid(row=0, column=2, padx=10, pady=10)

    def setup_search_bar(self):
        # Search bar with placeholder text
        self.search_entry = ttk.Entry(self.top_frame)
        self.search_entry.insert(0, "Search...")
        self.search_entry.grid(row=0, column=1, sticky="e")
        self.search_entry.bind("<FocusOut>", self.on_search_entry_focus_out)

        # Bind the KeyRelease event to the search_entry widget for real-time searching
        self.search_entry.bind("<KeyRelease>", self.search_stock)

        # Bind the FocusIn event to clear the placeholder text
        self.search_entry.bind("<FocusIn>", self.clear_placeholder_text)

        # Configure grid
        self.top_frame.grid_columnconfigure(0, weight=1)  # Allow column 0 to expand
        self.top_frame.grid_rowconfigure(1, weight=1)
        self.update_treeview()

    def check_reorder(self, row, reorder_point):
        try:
            quantity = int(row['values'][1].split('@')[0].strip())
            return quantity < reorder_point
        except Exception as e:
            print(f"Error in check_reorder: {e}")
            return False

    def get_existing_sales_locations(self):
        try:
            # Read the historical data
            df = pd.read_excel(self.history_file)
            # Get unique locations from the Location column
            locations = df["Location"].dropna().unique().tolist()
            return locations
        except:
            # Return an empty list if there is an error
            return []

    def show_custom_input_dialog(self):
        dialog = AllInOneInputDialog(root, "Custom Input Dialog", "Enter some text:")
        print("Result:", dialog.result)

    def show_custom_number_input_dialog(self):
        dialog = AllInOneInputDialog(root, "Custom Number Input Dialog", "Enter a number:")
        print("Result:", dialog.result)

    # Functions to be implemented
    def show_add_stock_fields(self):
        try:
            # Open the single dialog to get all necessary information
            labels = ["Enter Item Name:", "Enter Quantity:", "Enter Cost Price:", "Enter Sales Price:",
                      "Enter Reorder Point:"]
            stock_dialog = AllInOneInputDialog(parent=self.root, title="Enter Stock Details", labels=labels, width=500,
                                               height=275)
            stock_details = stock_dialog.result

            # Check if the dialog was cancelled
            if stock_details is None:
                return

            # Extract and validate the values
            item_name = stock_details[0].strip()
            if not item_name:
                raise ValueError("Item name cannot be empty.")

            try:
                quantity = int(stock_details[1])
                if quantity <= 0:
                    raise ValueError("Quantity should be a positive integer.")
            except ValueError:
                raise ValueError("Quantity should be a positive integer.")

            try:
                cost_price = float(stock_details[2])
                if cost_price < 0:
                    raise ValueError("Cost price should be a non-negative number.")
            except ValueError:
                raise ValueError("Cost price should be a non-negative number.")

            try:
                sales_price = float(stock_details[3])
                if sales_price < 0:
                    raise ValueError("Sales price should be a non-negative number.")
            except ValueError:
                raise ValueError("Sales price should be a non-negative number.")

            try:
                reorder_point = int(stock_details[4])
                if reorder_point < 0:
                    raise ValueError("Reorder point should be a non-negative number.")
            except ValueError:
                raise ValueError("Reorder point should be a non-negative number.")

            # Record the change
            self.record_change(item_name, quantity, cost_price, sales_price, "Added")

            # Check if item name is unique
            if self.is_item_name_unique(item_name):
                df = pd.read_excel(self.inventory_file)

                # Append the new stock data
                new_stock = pd.DataFrame([[item_name, quantity, cost_price, sales_price, reorder_point]],
                                         columns=["Item Name", "Quantity", "Cost Price", "Sales Price",
                                                  "Reorder Point"])
                df = df._append(new_stock, ignore_index=True)

                # Save the updated stock data back to the Excel file
                df.to_excel(self.inventory_file, index=False)

                # Update the Treeview to reflect the changes
                self.update_treeview()
            else:
                tk.messagebox.showerror("Error", "Item name must be unique")
        except ValueError as ve:
            # Handle value errors (e.g., invalid inputs)
            messagebox.showwarning("Invalid Input", str(ve))
            logging.warning(str(ve))
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")
            logging.error(str(e))

    def is_item_name_unique(self, item_name):
        try:
            df = pd.read_excel(self.inventory_file)
            return not df['Item Name'].str.lower().isin([item_name.lower()]).any()
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred while checking for item uniqueness: {str(e)}")
            return False

    def get_item_index(self, item_name):
        df = pd.read_excel(self.inventory_file)
        for index, row in df.iterrows():
            if row["Item Name"] == item_name:
                return index, row
        return None, None

    def modify_stock(self, item_name, change_amount, operation,entered_location = None):
        index, row = self.get_item_index(item_name)
        if index is None:
            tk.messagebox.showerror("Error", f"Item {item_name} not found.")
            return

        # Get the relevant values of the selected stock item
        quantity = row["Quantity"]
        cost_price = row["Cost Price"]
        sales_price = row["Sales Price"]

        # Record the change
        if entered_location is not None:
            self.record_change(item_name, abs(change_amount), cost_price, sales_price, operation,entered_location)
        else:
            self.record_change(item_name,abs(change_amount),cost_price,sales_price,operation)

        # Update the stock in the inventory file

        try:
            df = pd.read_excel(self.inventory_file)
            new_quantity = int(quantity) + change_amount
            if new_quantity < 0:
                tk.messagebox.showwarning("Invalid Operation",
                                          f"Cannot decrease stock below 0. Current stock: {quantity}")
                return
            df.at[index, "Quantity"] = new_quantity
            df.to_excel(self.inventory_file, index=False)

            # Update the treeview
            self.update_treeview()
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred while updating the stock: {str(e)}")

    @staticmethod
    def is_number(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def increase_stock(self):
        try:
            # Check if a row is selected
            selected_items = self.treeview.selection()
            if not selected_items:
                tk.messagebox.showwarning("No Selection", "Please select an item to increase stock.")
                return

            # Get the item name from the selected row
            item_name = self.treeview.item(selected_items[0], "values")[0]

            # Prompt the user for the amount by which to increase the stock
            labels = ["Enter amount to increase:"]
            dialog = AllInOneInputDialog(parent=self.root, title="Increase Stock", labels=labels, width=400, height=120)

            # Check if the dialog was cancelled
            if dialog.result is None:
                return

            # Extract and validate the value
            try:
                increase_amount = int(dialog.result[0])
                if increase_amount <= 0:
                    raise ValueError("Amount to increase should be a positive integer.")
            except ValueError:
                raise ValueError("Amount to increase should be a positive integer.")

            # Modify the stock
            self.modify_stock(item_name, increase_amount, "Increased")

        except ValueError as ve:
            # Handle value errors (e.g., invalid inputs)
            tk.messagebox.showwarning("Invalid Input", str(ve))
            logging.warning(str(ve))
        except Exception as e:
            # Handle general exceptions
            tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")
            logging.error(str(e))



    def decrease_stock(self):
        try:
            # Check if a row is selected
            selected_items = self.treeview.selection()
            if not selected_items:
                tk.messagebox.showwarning("No Selection", "Please select an item to decrease stock.")
                return

            # Get the item name from the selected row
            item_name = self.treeview.item(selected_items[0], "values")[0]

            # Read the sales locations from the Excel file
            excel_file = self.history_file  # Assuming the sales locations are stored in the history file
            df = pd.read_excel(excel_file)

            # Filter out NaN values and get unique sales locations
            sales_locations = [loc for loc in df['Location'].unique().tolist() if
                               loc is not np.nan and 'Location' in df.columns]

            # Prompt the user for the amount by which to decrease the stock
            labels = ["Stock amount of sale:", "Enter Sales Location:"]
            autocomplete_fields = {1: sales_locations}  # Sales Location field is the second field (index 1)

            dialog = AllInOneInputDialog(parent=self.root, title="Decrease Stock", labels=labels,
                                         autocomplete_fields=autocomplete_fields, width=400, height=165)

            # Check if the dialog was cancelled
            if dialog.result is None:
                return

            # Extract and validate the values
            try:
                decrease_amount = int(dialog.result[0])
                if decrease_amount <= 0:
                    raise ValueError("Amount to decrease should be a positive integer.")
            except ValueError:
                raise ValueError("Amount to decrease should be a positive integer.")

            sales_location = dialog.result[1]
            if not sales_location or sales_location.strip() == "":
                raise ValueError("Sales location cannot be empty.")

            # Modify the stock
            self.modify_stock(item_name, -decrease_amount, "Decreased", sales_location)

        except ValueError as ve:
            # Handle value errors (e.g., invalid inputs)
            tk.messagebox.showwarning("Invalid Input", str(ve))
            logging.warning(str(ve))
        except Exception as e:
            # Handle general exceptions
            tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")
            logging.error(str(e))

    def on_search_entry_focus_out(self, event=None):
        # Set the placeholder text if the search entry is empty
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search...")

    def search_stock(self, event=None):
        try:
            # Get the search term from the search entry field
            search_term = self.search_entry.get().lower()

            # Clear existing rows in the Treeview
            for row in self.treeview.get_children():
                self.treeview.delete(row)

            # Load data from Excel file
            df = pd.read_excel(self.inventory_file)

            # Filter and display only the items that match the search term
            for index, row in df.iterrows():
                item_name = row["Item Name"]
                quantity = row["Quantity"]
                cost_price = row["Cost Price"]
                sales_price = row["Sales Price"]
                total_cost_price = float(cost_price) * int(quantity)
                total_sales_price = float(sales_price) * int(quantity)
                total_cost_string = f'{total_cost_price} --R{cost_price}'
                total_sales_string = f'{total_sales_price} --R{sales_price}'

                # Get the reorder point for this item, if not available fall back to a default value
                reorder_point = row.get("Reorder Point")
                if not reorder_point or not isinstance(reorder_point, (int, float)):
                    reorder_point = 5

                if search_term in item_name.lower():
                    # Populate the treeview with data
                    item_id = self.treeview.insert("", "end",
                                                   values=(item_name, quantity, total_cost_string, total_sales_string))

                    # Change the row color if below reorder point
                    if quantity < reorder_point:
                        self.treeview.item(item_id, tags='below_reorder')

            # Configure the tag to change the background color of the rows tagged as 'below_reorder'
            self.treeview.tag_configure('below_reorder', foreground='red')
        except FileNotFoundError:
            tk.messagebox.showerror("Error","Inventory file not found.")
        except Exception as e:
            tk.messagebox.showerror("Error",f"An error occured: {str(e)}")




    def clear_placeholder_text(self, event=None):
        try:
            # Clear the text in the search entry if it is the placeholder text
            if self.search_entry.get() == "Search...":
                self.search_entry.delete(0, tk.END)
        except Exception as e:
            tk.messagebox.showerror("Error",f"An unexpected error occurred: {str(e)}    ")

    def update_treeview(self):
        try:
            # Clear existing rows
            for row in self.treeview.get_children():
                self.treeview.delete(row)

            # Define a reorder point (you can adjust this value as needed)


            # Load data from Excel file
            df = pd.read_excel(self.inventory_file)

            for index, row in df.iterrows():
                item_name = row["Item Name"]
                quantity = row["Quantity"]
                cost_price = row["Cost Price"]
                sales_price = row["Sales Price"]
                total_cost_price = float(cost_price) * int(quantity)
                total_sales_price = float(sales_price) * int(quantity)
                total_cost_string = f'{total_cost_price}  -- R{cost_price}'
                total_sales_string = f'{total_sales_price} --R{sales_price}'

                #get the reorder point for this item, if not available fall back to a defualt value
                reorder_point = row.get("Reorder Point")
                if not reorder_point or not isinstance(reorder_point,(int,float)):
                    reorder_point = 5


                # Populate the treeview with data
                item_id = self.treeview.insert('', 'end', values=(
                item_name, quantity, total_cost_string, total_sales_string))

                # Change the row color if below reorder point
                if quantity < reorder_point:
                    self.treeview.item(item_id, tags='below_reorder')

            # Configure the tag to change the background color of the rows tagged as 'below_reorder'
            self.treeview.tag_configure('below_reorder', foreground='red')
        except FileNotFoundError:
            tk.messagebox.showerror("Error","Inventory file not found.")
        except Exception as e:
            tk.messagebox.showerror("Error",f"An unexpected error occured: {str(e)}")

    def record_change(self, item_name, quantity_changed, cost_price, sales_price, change_type,sales_location=None):
        """
        Records changes in inventory to the history Excel file.
        """
        try:
            # Read the historical data
            df = pd.read_excel(self.history_file)
            timestamp = pd.Timestamp.now()
            # Append the new change to the historical data
            new_row = {"Item Name": item_name, "Quantity Changed": quantity_changed,
                       "Cost Price": cost_price, "Sales Price": sales_price,
                       "Change Type": change_type, "Timestamp": timestamp}
            if sales_location is not None:
                new_row["Location"]=sales_location
            df = df._append(new_row, ignore_index=True)
            # Save the updated historical data
            df.to_excel(self.history_file, index=False)
        except FileNotFoundError:
            tk.messagebox.showerror("Error","Inventory History file not found.")
        except ValueError as ve:
            tk.messagebox.showerror("Invalid Input",str(ve))
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred while recording historical data: {str(e)}")




if __name__ == "__main__":
    root = ThemedTk(theme='breeze')
    root.minsize(600, 450)
    inventory_manager = InventoryManager(root)
    root.mainloop()


