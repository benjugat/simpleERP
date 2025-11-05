from controller.controller import ProductController, MaterialController, DealerController, SaleController

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

def get_number_sales_by_month(session, year):
    sale_controller = SaleController(session)
    month_sales = []
    for month in range(1, 13):
        sales = sale_controller.get_month_sales(year, month)
        total_sales = sum(1 for sale in sales)
        month_sales.append(total_sales)
    return month_sales

def get_sales_by_month(session, year):
    sale_controller = SaleController(session)
    month_sales = []
    for month in range(1, 13):
        sales = sale_controller.get_month_sales(year, month)
        total_sales = sum(sale.price for sale in sales)
        month_sales.append(total_sales)
    return month_sales

def get_number_costs_by_month(session, year):
    material_controller = MaterialController(session)
    month_costs = []
    for month in range(1, 13):
        purchases = material_controller.get_month_purchases(year, month)
        total_costs = sum(1 for purchase in purchases)
        month_costs.append(total_costs)
    return month_costs

def get_costs_by_month(session, year):
    material_controller = MaterialController(session)
    month_costs = []
    for month in range(1, 13):
        purchases = material_controller.get_month_purchases(year, month)
        total_costs = sum(purchase.price for purchase in purchases)
        month_costs.append(total_costs)
    return month_costs

def calculate_number_sales_by_dealer(session):
    dealer_controller = DealerController(session)
    dealers = dealer_controller.get_all_dealers()
    sales_count = {dealer.name: len(dealer_controller.get_dealer_sales(dealer.dealer_id)) for dealer in dealers}
    return sales_count