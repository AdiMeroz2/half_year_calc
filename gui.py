import csv
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox
from six_month_stock import SixMonthStock

BACKGROUND_COLOR = "lightgrey"

class StockGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Trade Analyzer")

        self.input_file_path = None
        self.output_file_path = self.generate_output_filename()

        self.frame = tk.Frame(root, bg=BACKGROUND_COLOR, width=800, height=100)
        self.frame.pack_propagate(False)  # Prevent frame from resizing based on its content
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.input_file_label = tk.Label(self.frame, text="Input File Path:", bg=BACKGROUND_COLOR)
        self.input_file_label.grid(row=0, column=0, padx=10, pady=10)

        self.input_file_entry = tk.Entry(self.frame, bg="white")
        self.input_file_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.input_open_button = tk.Button(self.frame, text="...", padx=10, pady=5, fg="white", bg="#263D42",
                                           command=self.open_input_file)
        self.input_open_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")

        # Set the default output path to the current directory with a date-time based filename
        self.output_file_label = tk.Label(self.frame, text="Output File Path:", bg=BACKGROUND_COLOR)
        self.output_file_label.grid(row=1, column=0, padx=10, pady=10)

        self.output_file_entry = tk.Entry(self.frame, bg="white")
        self.output_file_entry.insert(0, self.output_file_path)
        self.output_file_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.output_open_button = tk.Button(self.frame, text="...", padx=10, pady=5, fg="white", bg="#263D42",
                                            command=self.open_input_file)
        self.output_open_button.grid(row=1, column=2, padx=10, pady=10, sticky="e")

        self.calculate_button = tk.Button(self.frame, text="Calculate", padx=10, pady=5, fg="white", bg="#263D42",
                                          command=self.calculate_trades)
        self.calculate_button.grid(row=2, column=0, columnspan=3, pady=10)

        # Make the columns expand to fill the frame width
        self.frame.columnconfigure(1, weight=1)

    def generate_output_filename(self):
        # Generate a filename based on the current date and time
        now = datetime.now()
        formatted_time = now.strftime("%Y%m%d_%H%M%S")
        return f"calculate_{formatted_time}.csv"

    def open_input_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            if not file_path.lower().endswith('.csv'):
                messagebox.showwarning("Invalid File", "Please select a valid CSV file.")
            else:
                self.input_file_path = file_path
                self.input_file_entry.insert(0, self.input_file_path)

    def open_output_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            if not file_path.lower().endswith('.csv'):
                messagebox.showwarning("Invalid File", "Please select a valid CSV file.")
            else:
                self.output_file_path = file_path
                self.output_file_entry.insert(0, self.input_file_path)

    def calculate_trades(self):
        if not self.input_file_path:
            messagebox.showwarning("Invalid File", "No file selected. Please open a CSV file first.")
            return

        try:
            stock_processor = SixMonthStock()
            trades_within_6_months, per_stock, total_e_l, total_earn = stock_processor.find_trades_within_6_months(self.input_file_path)
        except Exception as e:
            messagebox.showwarning("Calculation Failed", f"Got error while reading from file:\n{e}.")
            return

        if not trades_within_6_months:
            messagebox.showinfo("success", f"No stocks were found")
            return

        try:
            # Writing to a CSV file
            with open(self.output_file_path, 'a', newline='') as file:
                file.write("All the stocks that were sold in six moths\n")
                writer = csv.DictWriter(file, fieldnames=trades_within_6_months[0].keys())
                writer.writeheader()  # Writing the header
                for data in trades_within_6_months:
                    writer.writerow(data)

            with open(self.output_file_path, 'a', newline='') as file:
                file.write("\nProfit per stock\n")
                writer = csv.DictWriter(file, fieldnames=["Stock Name", "Total Profit"])
                writer.writeheader()  # Writing the header
                for name, profit in per_stock.items():
                    row = {
                        "Stock Name": name,
                        "Total Profit": profit
                    }
                    writer.writerow(row)

            with open(self.output_file_path, 'a', newline='') as file:
                file.write("\nReturns & Losses Conclusion\n")
                writer = csv.DictWriter(file, fieldnames=["Currency", "Returns", "Losses"])
                writer.writeheader()  # Writing the header
                for currency, values in total_e_l.items():
                    row = {
                        "Currency": currency,
                        "Returns": values['earn'],
                        "Losses": values['loss']
                    }
                    writer.writerow(row)

            with open(self.output_file_path, 'a', newline='') as file:
                file.write("\nFinal Profit Conclusion\n")
                writer = csv.DictWriter(file, fieldnames=["Currency", "Profit"])
                writer.writeheader()  # Writing the header
                for currency, profit in total_earn.items():
                    row = {
                        "Currency": currency,
                        "Profit": profit
                    }
                    writer.writerow(row)
        except Exception as e:
            messagebox.showwarning("Error", f"Failed during writing to file, got exception:\n{e}")
            return

        messagebox.showinfo("success", f"calculation save to {self.output_file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = StockGui(root)
    root.mainloop()
