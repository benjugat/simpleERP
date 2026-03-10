from controller.controller import ProductController, MaterialController, DealerController, SaleController
from datetime import datetime
from gcodeparser import GcodeParser
import math
import re

def calculate_number_sales_by_product_id(session, product_id):
    product_controller = ProductController(session)
    manufactured_items = product_controller.get_all_manufactured_item(product_id)
    total_sales = sum(1 for item in manufactured_items if item.sale_id is not None)
    return total_sales


def calculate_number_sales_by_product(session):
    product_controller = ProductController(session)
    products = product_controller.get_all_products()
    sales_count = {product.name: calculate_number_sales_by_product_id(session, product.product_id) for product in products}
    return sales_count

def calculate_number_sales_by_product_type(session):
    product_controller = ProductController(session)
    products = product_controller.get_all_products()
    sales_count = {}
    for product in products:
        if product.product_type not in sales_count:
            sales_count[product.product_type] = 0
        sales_count[product.product_type] =  sales_count[product.product_type] + calculate_number_sales_by_product_id(session, product.product_id)
    return sales_count

def calculate_sales_by_product_id(session, product_id):
    product_controller = ProductController(session)
    sale_controller = SaleController(session)
    total_sales = 0
    manufactured_items = product_controller.get_all_manufactured_item(product_id)
    for item in manufactured_items:
        if item.sale_id is not None:
            total_sales += sale_controller.get_sale(item.sale_id).price
    return total_sales

def calculate_sales_by_product(session):
    product_controller = ProductController(session)
    products = product_controller.get_all_products()
    sales_count = {product.name: calculate_sales_by_product_id(session, product.product_id) for product in products}
    return sales_count

def calculate_sales_by_product_type(session):
    product_controller = ProductController(session)
    products = product_controller.get_all_products()
    sales_count = {}
    for product in products:
        if product.product_type not in sales_count:
            sales_count[product.product_type] = 0
        sales_count[product.product_type] =  sales_count[product.product_type] + calculate_sales_by_product_id(session, product.product_id)
        print(sales_count[product.product_type])
    print(sales_count)
    return sales_count

def calculate_total_sales(session):
    sale_controller = SaleController(session)
    sales = sale_controller.get_all_sales()
    total_sales = sum(sale.price for sale in sales)
    return total_sales

def calculate_costs(session):
    material_controller = MaterialController(session)
    purchases = material_controller.get_all_purchases()
    total_costs = sum(purchase.price for purchase in purchases)
    return total_costs

def calculate_sales_of_a_year(session, year):
    sale_controller = SaleController(session)
    sales = sale_controller.get_year_sales(year)
    total_sales = sum(sale.price for sale in sales)
    return total_sales

def calculate_costs_of_a_year(session, year):
    material_controller = MaterialController(session)
    purchases = material_controller.get_year_purchases(year)
    total_costs = sum(purchase.price for purchase in purchases)
    return total_costs

def get_number_sales_by_month_of_a_year(session, year):
    sale_controller = SaleController(session)
    month_sales = []
    for month in range(1, 13):
        sales = sale_controller.get_month_sales(year, month)
        total_sales = sum(1 for sale in sales)
        month_sales.append(total_sales)
    return month_sales

def get_sales_by_month_of_a_year(session, year):
    sale_controller = SaleController(session)
    month_sales = []
    for month in range(1, 13):
        sales = sale_controller.get_month_sales(year, month)
        total_sales = sum(sale.price for sale in sales)
        month_sales.append(total_sales)
    return month_sales

def get_number_costs_by_month_of_a_year(session, year):
    material_controller = MaterialController(session)
    month_costs = []
    for month in range(1, 13):
        purchases = material_controller.get_month_purchases(year, month)
        total_costs = sum(1 for purchase in purchases)
        month_costs.append(total_costs)
    return month_costs

def get_costs_by_month_of_a_year(session, year):
    material_controller = MaterialController(session)
    month_costs = []
    for month in range(1, 13):
        purchases = material_controller.get_month_purchases(year, month)
        total_costs = sum(purchase.price for purchase in purchases)
        month_costs.append(total_costs)
    return month_costs

def get_sales_by_month_of_last_12_months(session):
    sale_controller = SaleController(session)
    month_sales = []
    current_year = datetime.now().year
    current_month = datetime.now().month
    for i in range(12):
        month = (current_month - i - 1) % 12 + 1
        year = current_year if month <= current_month else current_year - 1
        sales = sale_controller.get_month_sales(year, month)
        total_sales = sum(sale.price for sale in sales)
        month_sales.append(total_sales)
    return month_sales[::-1]

def get_costs_by_month_of_last_12_months(session):
    material_controller = MaterialController(session)
    month_costs = []
    current_year = datetime.now().year
    current_month = datetime.now().month
    for i in range(12):
        month = (current_month - i - 1) % 12 + 1
        year = current_year if month <= current_month else current_year - 1
        purchases = material_controller.get_month_purchases(year, month)
        total_costs = sum(purchase.price for purchase in purchases)
        month_costs.append(total_costs)
    return month_costs[::-1]

def calculate_number_sales_by_dealer(session):
    dealer_controller = DealerController(session)
    dealers = dealer_controller.get_all_dealers()
    sales_count = {dealer.name: len(dealer_controller.get_dealer_sales(dealer.dealer_id)) for dealer in dealers}
    return sales_count

def calculate_number_sales_by_year(session, year):
    sale_controller = SaleController(session)
    sales = sale_controller.get_year_sales(year)
    total_sales = sum(1 for sale in sales)
    return total_sales


def calculate_print_time(gcode_content):
    parser = GcodeParser(gcode_content)
    commands = list(parser)
    x, y, z, e = 0.0, 0.0, 0.0, 0.0
    total_time = 0.0
    
    for cmd in commands:
        if cmd['cmd'] in ('G0', 'G1'):  # Movimientos rápidos/lineales
            params = cmd.get('params', {})
            
            prev_x, prev_y, prev_z, prev_e = x, y, z, e
            
            x = params.get('X', x)
            y = params.get('Y', y)
            z = params.get('Z', z)
            e = params.get('E', e)
            
            f = params.get('F', 0)
            if f == 0:
                # Busca F en comandos previos (simplificado)
                continue
                
            dist = math.sqrt(
                (x - prev_x)**2 +
                (y - prev_y)**2 +
                (z - prev_z)**2 +
                (e - prev_e)**2
            )
            
            total_time += dist / (f / 60)  # f en mm/min -> seg
    
    # Formato HH:MM:SS
    hours = int(total_time // 3600)
    mins = int((total_time % 3600) // 60)
    secs = int(total_time % 60)
    time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
    return time_str

def calculate_weight(gcode_content):
    DENSITIES = {'PETG': 1.27, 'PLA': 1.24}
    if not filament_type:
        if re.search(r'PETG|petg', gcode_content, re.I):
            filament_type = 'PETG'
        else:
            filament_type = 'PLA'
    density = DENSITIES.get(filament_type.upper(), 1.24)
    diam = 1.75  # mm estándar
    parser = GcodeParser(gcode_content)
    total_extrusion = 0.0
    prev_e = 0.0
    
    for cmd in parser:
        if cmd['cmd'] in ('G0', 'G1') and 'E' in cmd.get('params', {}):
            curr_e = cmd['params']['E']
            total_extrusion += abs(curr_e - prev_e)
            prev_e = curr_e
    
    r = diam / 20  # cm
    volume = (total_extrusion / 10) * math.pi * (r ** 2)
    weight = round(volume * density, 1)
    
    print(f"Detectado: {filament_type}, Peso: {weight}g")  # Debug
    return weight