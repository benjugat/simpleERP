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
    commands = parser.lines
    x, y, z, e = 0.0, 0.0, 0.0, 0.0
    total_time = 0.0
    current_feed = 0.0  # F actual
        
    for cmd in commands:
        # DEBUG: print(cmd.command, cmd.params)
        
        # cmd.command es TUPLA ('G', 0) o ('G', 1)
        if isinstance(cmd.command, tuple) and cmd.command[0] == 'G':
            g_code = int(cmd.command[1])
            
            if g_code in (0, 1):  # G0 o G1
                params = cmd.params
                
                # Feedrate (puede venir en misma línea)
                new_feed = params.get('F', current_feed)
                if new_feed > 0:
                    current_feed = new_feed
                
                # Posiciones nuevas (si no hay, mantener anteriores)
                new_x = params.get('X', x)
                new_y = params.get('Y', y)
                new_z = params.get('Z', z)
                new_e = params.get('E', e)
                
                # Solo calcular si hay movimiento Y feedrate
                if current_feed > 0 and (new_x != x or new_y != y or new_z != z):
                    dist = math.sqrt(
                        (new_x - x)**2 + (new_y - y)**2 + 
                        (new_z - z)**2 + (new_e - e)**2
                    )
                    
                    time_segment = dist / (current_feed / 60)  # mm/min → seg
                    total_time += time_segment
                                    
                # Actualizar posición
                x, y, z, e = new_x, new_y, new_z, new_e
    
    # Formato HH:MM:SS
    hours = int(total_time // 3600)
    mins = int((total_time % 3600) // 60)
    secs = int(total_time % 60)
    time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
    
    return time_str

def calculate_weight(gcode_content, filament_type=None):
    DENSITIES = {'PETG': 1.27, 'PLA': 1.24}
    
    # Auto-detectar tipo
    if not filament_type:
        if re.search(r'PETG|petg', gcode_content, re.I):
            filament_type = 'PETG'
        else:
            filament_type = 'PLA'
    
    density = DENSITIES.get(filament_type, 1.24)
    diam = 1.75  # mm
    r = diam / 2 / 10  # cm (radio)
    
    parser = GcodeParser(gcode_content)
    total_extrusion = 0.0
    prev_e = 0.0
        
    for cmd in parser.lines:
        
        # FIX 1: cmd.command es TUPLA ('G', 1)
        if isinstance(cmd.command, tuple) and cmd.command[0] == 'G':
            g_code = cmd.command[1]
            
            # FIX 2: Solo G0/G1 con E (extrusión)
            if g_code in (0, 1) and 'E' in cmd.params:
                curr_e = float(cmd.params['E'])
                extrusion = abs(curr_e - prev_e)
                total_extrusion += extrusion
                prev_e = curr_e
                
    
    # Volumen (mm³) = π * r² * longitud_extrusion
    r_mm = diam / 2  # mm
    volume_mm3 = math.pi * (r_mm ** 2) * total_extrusion
    weight_g = round((volume_mm3 / 1000) * density, 1)  # g
    
    print(f"Filamento: {filament_type} | Extrusión total: {total_extrusion:.1f}mm | Volumen: {volume_mm3/1000:.1f}cm³ | Peso: {weight_g}g")
    return weight_g