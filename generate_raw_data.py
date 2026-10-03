import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_datasets(data_dir="data/raw"):
    os.makedirs(data_dir, exist_ok=True)
    np.random.seed(42)

    # 1. SKU Master
    num_skus = 200
    categories = ['Furnishings', 'Décor', 'Small Appliances']
    subcategories = {
        'Furnishings': ['Bedding', 'Seating', 'Rugs', 'Storage'],
        'Décor': ['Lighting', 'Wall Art', 'Vases', 'Mirrors'],
        'Small Appliances': ['Coffee Makers', 'Air Purifiers', 'Blenders', 'Toasters']
    }

    raw_categories_pool = [
        'Furnishings', 'furnishing', 'Furnishings', 
        'Décor', 'Decor', 'DECOR', 
        'Small Appliances', 'small appliances', 'Small Appliances'
    ]

    sku_ids = [f"SKU_{i:03d}" for i in range(1, num_skus + 1)]
    sku_master_list = []

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 3, 1)

    for i, sku in enumerate(sku_ids):
        cat = categories[i % len(categories)]
        subcat = np.random.choice(subcategories[cat])
        # Insert inconsistent category string for cleaning test
        raw_cat = np.random.choice([c for c in raw_categories_pool if cat.lower() in c.lower()])
        
        launch = start_date + timedelta(days=int(np.random.randint(0, 180)))
        unit_cost = round(float(np.random.uniform(300, 8000)), 2)
        margin_multiplier = np.random.uniform(1.4, 2.3)
        list_price = round(unit_cost * margin_multiplier, 2)
        
        sku_master_list.append({
            'sku_id': sku,
            'category': raw_cat,
            'subcategory': subcat,
            'launch_date': launch.strftime('%Y-%m-%d'),
            'unit_cost': unit_cost,
            'list_price': list_price
        })

    df_sku_master = pd.DataFrame(sku_master_list)

    # Introduce a missing category value for 1 SKU to test cleaning pipeline
    df_sku_master.loc[5, 'category'] = None

    df_sku_master.to_csv(os.path.join(data_dir, 'sku_master.csv'), index=False)

    # 2. Calendar
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    calendar_list = []
    
    for d in date_range:
        season = 'Winter'
        if d.month in [3, 4, 5]:
            season = 'Spring'
        elif d.month in [6, 7, 8]:
            season = 'Summer'
        elif d.month in [9, 10, 11]:
            season = 'Fall'

        is_holiday = 1 if (d.month == 10 and d.day in [24, 25, 26, 27]) or (d.month == 11 and d.day == 1) or (d.month == 12 and d.day == 25) else 0
        
        promo_event = 'None'
        if d.month == 10 and 20 <= d.day <= 30:
            promo_event = 'Diwali Sale'
        elif d.month == 11 and 20 <= d.day <= 27:
            promo_event = 'Black Friday'
        elif d.month == 1 and 1 <= d.day <= 7:
            promo_event = 'New Year Bash'
        elif d.month == 7 and 10 <= d.day <= 15:
            promo_event = 'Summer Splash'

        calendar_list.append({
            'date': d.strftime('%Y-%m-%d'),
            'week': int(d.isocalendar()[1]),
            'month': d.month,
            'season': season,
            'is_holiday': is_holiday,
            'promo_event': promo_event
        })

    df_calendar = pd.DataFrame(calendar_list)
    df_calendar.to_csv(os.path.join(data_dir, 'calendar.csv'), index=False)

    # 3. Sales Daily
    sales_list = []
    
    # Base daily demand per SKU
    sku_base_demand = {sku: np.random.uniform(0.5, 12.0) for sku in sku_ids}
    
    # Introduce 5 dead stock SKUs (near zero demand)
    for dead_sku in sku_ids[-5:]:
        sku_base_demand[dead_sku] = 0.02

    # Introduce 5 fast moving SKUs
    for top_sku in sku_ids[:5]:
        sku_base_demand[top_sku] = 25.0

    calendar_dict = df_calendar.set_index('date').to_dict(orient='index')
    sku_dict = df_sku_master.set_index('sku_id').to_dict(orient='index')

    for d in date_range:
        d_str = d.strftime('%Y-%m-%d')
        cal_row = calendar_dict[d_str]
        
        # Day of week seasonality
        dow_mult = 1.3 if d.weekday() in [5, 6] else 0.9
        promo_mult = 1.8 if cal_row['promo_event'] != 'None' else 1.0
        holiday_mult = 1.4 if cal_row['is_holiday'] == 1 else 1.0
        
        for sku in sku_ids:
            # Check launch date
            launch_str = sku_dict[sku]['launch_date']
            if d_str < launch_str:
                continue

            base = sku_base_demand[sku]
            noise = np.random.poisson(lam=max(0.1, base * dow_mult * promo_mult * holiday_mult))
            units = max(0, int(noise))
            
            # Promo flag
            is_promo = 1 if cal_row['promo_event'] != 'None' or np.random.rand() < 0.1 else 0
            list_p = sku_dict[sku]['list_price']
            price = round(list_p * 0.85, 2) if is_promo else list_p
            revenue = round(units * price, 2)

            sales_list.append({
                'date': d_str,
                'sku_id': sku,
                'units_sold': units,
                'revenue': revenue,
                'unit_price': price,
                'promo_flag': is_promo
            })

    df_sales = pd.DataFrame(sales_list)

    # Inject real-world deliberate flaws:
    # 1. Missing values (~0.8% missing promo_flag)
    missing_indices = np.random.choice(df_sales.index, size=int(len(df_sales) * 0.008), replace=False)
    df_sales.loc[missing_indices, 'promo_flag'] = np.nan

    # 2. Duplicate records (14 rows)
    duplicates = df_sales.iloc[np.random.choice(df_sales.index, size=14, replace=False)].copy()
    df_sales = pd.concat([df_sales, duplicates], ignore_index=True)

    # 3. An invalid negative units row for data quality detection
    df_sales.loc[100, 'units_sold'] = -5

    df_sales.to_csv(os.path.join(data_dir, 'sales_daily.csv'), index=False)

    # 4. Inventory Snapshots
    # Latest snapshot as of 2026-03-01
    inventory_list = []
    latest_date = '2026-03-01'

    for sku in sku_ids:
        lead_time = int(np.random.choice([7, 10, 14, 21, 28]))
        avg_weekly_sales = sku_base_demand[sku] * 7
        
        # Simulate different inventory positions
        rand_type = np.random.rand()
        if rand_type < 0.25: # Low stock
            on_hand = int(avg_weekly_sales * (lead_time / 7.0) * 0.4)
            on_order = 0
        elif rand_type < 0.50: # Excess stock
            on_hand = int(avg_weekly_sales * 14) # 14 weeks of stock
            on_order = int(avg_weekly_sales * 4)
        elif rand_type < 0.65: # High on order + high on hand (investigate)
            on_hand = int(avg_weekly_sales * 10)
            on_order = int(avg_weekly_sales * 8)
        else: # Healthy
            on_hand = int(avg_weekly_sales * (lead_time / 7.0) * 1.5)
            on_order = int(avg_weekly_sales * 2)

        reorder_pt = int(avg_weekly_sales * (lead_time / 7.0) * 1.2)

        inventory_list.append({
            'date': latest_date,
            'sku_id': sku,
            'on_hand_units': max(0, on_hand),
            'on_order_units': max(0, on_order),
            'lead_time_days': lead_time,
            'reorder_point': reorder_pt
        })

    df_inventory = pd.DataFrame(inventory_list)

    # Inject missing inventory record for 2 SKUs to test data quality check
    df_inventory = df_inventory.iloc[:-2]

    df_inventory.to_csv(os.path.join(data_dir, 'inventory_snapshots.csv'), index=False)
    print(f"Generated raw data in {data_dir} successfully!")
    print(f"Sales records: {len(df_sales)}, SKUs: {len(df_sku_master)}, Inventory records: {len(df_inventory)}")

if __name__ == '__main__':
    generate_datasets()
