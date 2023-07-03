import pandas as pd

class InventoryAnalytics:

    def __init__(self):
        # File paths
        sales_data_path = '/Users/john/PycharmProjects/revised_inventory_manager/inventory_history.xlsx'
        inventory_data_path = '/Users/john/PycharmProjects/revised_inventory_manager/inventory.xlsx'

        # Read data from Excel files
        self.sales_data = pd.read_excel(sales_data_path)
        self.inventory_data = pd.read_excel(inventory_data_path)

    def get_top_selling_items(self):
        # Filter sales data
        sales_only = self.sales_data[self.sales_data['Change Type'] == 'Decreased']

        # Group by Item Name and sum the Quantity Changed
        top_selling = sales_only.groupby('Item Name')['Quantity Changed'].sum()

        # Sort by total quantity sold in descending order
        top_selling = top_selling.sort_values(ascending=False)

        return top_selling

    def calculate_inventory_value(self):
        # Multiply Quantity by Cost Price for each item
        self.inventory_data['Value'] = self.inventory_data['Quantity'] * self.inventory_data['Cost Price']

        # Sum these values to get the total inventory value
        total_value = self.inventory_data['Value'].sum()

        return total_value

    def calculate_inventory_turnover(self, inventory_value):
        # Filter sales data
        sales_only = self.sales_data[self.sales_data['Change Type'] == 'Decreased']

        # Calculate Cost of Goods Sold (COGS)
        cogs = (sales_only['Quantity Changed'] * sales_only['Cost Price']).sum()

        # Divide COGS by average inventory value
        inventory_turnover = cogs / inventory_value

        return inventory_turnover

    def calculate_profit_margin(self):
        # Filter sales data
        sales_only = self.sales_data[self.sales_data['Change Type'] == 'Decreased'].copy()

        # Calculate profit for each sale
        sales_only['Profit'] = sales_only['Quantity Changed'] * (sales_only['Sales Price'] - sales_only['Cost Price'])

        # Group by Item Name and sum the profits
        profit_margin = sales_only.groupby('Item Name')['Profit'].sum()

        # Sort by total profits in descending order
        profit_margin = profit_margin.sort_values(ascending=False)

        return profit_margin

    def calculate_seasonal_trends(self):
        # Filter sales data
        sales_only = self.sales_data[self.sales_data['Change Type'] == 'Decreased'].copy()

        # Convert Timestamp to datetime
        sales_only['Timestamp'] = pd.to_datetime(sales_only['Timestamp'])

        # Extract month from Timestamp
        sales_only['Month'] = sales_only['Timestamp'].dt.month

        # Group by Item Name and month
        trends = sales_only.groupby(['Item Name', 'Month'])['Quantity Changed'].sum().reset_index()

        return trends







