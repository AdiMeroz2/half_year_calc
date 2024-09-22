import pandas as pd
import math
MIN_ELEMENTS = 10

class SixMonthStock:
    # Function to find trades closed within 6 months
    def find_trades_within_6_months(self, file_path):
        start_index = self.get_start_index(file_path)
        closed_trades = []

        # Read the CSV starting from the identified header line
        df = pd.read_csv(file_path, skiprows=start_index)
        # Iterate over the rows of the DataFrame
        for index, row in df.iterrows():
            if row['DataDiscriminator'] == "ClosedLot":
                stock_name = row["Symbol"]
                currency = row["Currency"]
                open_date = row['Date/Time']
                quantity = row["Quantity"]
                buy_price = row["T. Price"]

                # Convert the "Date/Time" column to datetime format
                open_date = pd.to_datetime(open_date)
                # Find the closest upper row with '-' in the "Exchange" column
                for i in range(index - 1, -1, -1):
                    if df.at[i, 'Exchange'] == '-':
                        close_date = df.at[i, 'Date/Time']
                        close_date = pd.to_datetime(close_date)
                        sold_price = df.at[i, "T. Price"]
                        asset = df.at[i, "Asset Category"]
                        mult_num = 1
                        if asset == "Equity and Index Options":
                            mult_num = 100
                        break

                # Check if the trade was closed within 6 months
                if (close_date - open_date).days <= 183:
                    if float(quantity) < 0:
                        earn = (float(buy_price) - float(sold_price)) * float(quantity) * -1 * mult_num
                    else:
                        earn = (float(sold_price) - float(buy_price)) * float(quantity) * mult_num

                    closed_trades.append({
                        "Stock Name": stock_name,
                        "Currency": currency,
                        "Open Date": open_date,
                        "Close Date": close_date,
                        "Days Held": (close_date - open_date).days,
                        "Earn": earn
                    })

        if not closed_trades:
            return None, None, None, None

        # Aggregate trades by stock name, currency, open date, and close date
        aggregated_trades = {}
        for trade in closed_trades:
            stock_name = trade["Stock Name"]
            curr = trade["Currency"]
            key = (stock_name, curr, trade["Open Date"], trade["Close Date"])

            if key not in aggregated_trades:
                aggregated_trades[key] = {
                    "Stock Name": trade["Stock Name"],
                    "Currency": trade["Currency"],
                    "Open Date": trade["Open Date"],
                    "Close Date": trade["Close Date"],
                    "Days Held": trade["Days Held"],
                    "Earn": 0
                }
            aggregated_trades[key]["Earn"] += float(trade["Earn"])


        per_stock = {}
        total_earn_loss = {}
        total_earn = {}

        for trades_key in aggregated_trades.keys():
            stock_name = aggregated_trades[trades_key]["Stock Name"]
            curr = aggregated_trades[trades_key]["Currency"]
            earn = aggregated_trades[trades_key]["Earn"]
            # calculate the final status per stock
            if f"{stock_name}({curr})" not in per_stock:
                per_stock[f"{stock_name}({curr})"] = 0
            per_stock[f"{stock_name}({curr})"] += earn

        for stock_name, sold_res in per_stock.items():
            curr = stock_name.split('(')[1]
            curr = curr.split(')')[0]
            # summarise all the earning stocks and losing stocks
            if curr not in total_earn_loss:
                total_earn_loss[curr] = {"earn": 0, "loss": 0}
                total_earn[curr] = 0

            if sold_res <= 0:
                total_earn_loss[curr]["loss"] += sold_res
            else:
                total_earn_loss[curr]["earn"] += sold_res
            total_earn[curr] += sold_res

        return_stocks = []
        for stock in aggregated_trades:
            return_stocks.append(aggregated_trades[stock])

        return return_stocks, per_stock, total_earn_loss, total_earn


    def get_start_index(self, file_path):
        # Read the file and find the start index for the desired header
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if len(line.split(',')) > MIN_ELEMENTS:
                    return i

    def get_all_closed_trades(self):
        pass
