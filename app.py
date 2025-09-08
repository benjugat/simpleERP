from flask import Flask, render_template, request, redirect, url_for, send_from_directory

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

from model.model import Base
from controller.controller import ProductController, MaterialController, DealerController, SaleController, ManufacturedItemController
from modules.modules import *

from dotenv import load_dotenv
import os

app = Flask(__name__)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('', 'favicon.ico', mimetype='image/png')


@app.route('/')
def index():

    sales_count = calculate_number_sales_by_product(session)
    lctx1 = list()
    vctx1 = list()
    for k in sales_count.keys():
        lctx1.append(k)
        vctx1.append(sales_count[k])
    
    lctx2 = list()
    vctx2 = list()
    
    c = calculate_costs(session)
    s = calculate_total_sales(session)
    b = s - c

    lctx2 = ["Costs", "Sales", "Benefits"]
    vctx2 = [c, s, b]

    sales_count = calculate_sales_by_product(session)
    lctx3 = list()
    vctx3 = list()

    for k in sales_count.keys():
        lctx3.append(k)
        vctx3.append(sales_count[k])

    return render_template('index.html', lctx1=lctx1, vctx1=vctx1, lctx2=lctx2, vctx2=vctx2, lctx3=lctx3, vctx3=vctx3)

###########################
#       DASHBOARD         #
###########################

@app.route('/dashboard')
def dashboard():
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    lctx1 = ["Jan","Feb","March"]
    vctx1 = [1000, 2000, 1500]

    number_sales_by_month = get_number_sales_by_month(session, 2025)
    sales_by_month = get_sales_by_month(session, 2025)
    
    costs_by_month = get_costs_by_month(session, 2025)

    sales_count = calculate_sales_by_product(session)
    product_name = list()
    sales_by_product = list()
    for k in sales_count.keys():
        product_name.append(k)
        sales_by_product.append(sales_count[k])
    
    number_sales_count = calculate_number_sales_by_product(session)
    number_sales_by_product = list()
    for k in number_sales_count.keys():
        number_sales_by_product.append(number_sales_count[k])

    dealers = list()
    sales_by_dealer = list()
    dealer_sales_count = calculate_number_sales_by_dealer(session)
    for k in dealer_sales_count.keys():
        dealers.append(k)
        sales_by_dealer.append(dealer_sales_count[k])


    kpi_total_sales = calculate_total_sales(session)
    kpi_total_profit = kpi_total_sales - calculate_costs(session)
    kpi_sold_items = sum(number_sales_count.values())
    return render_template('dashboard.html', kpi_total_sales=kpi_total_sales, kpi_total_profit=kpi_total_profit, kpi_sold_items=kpi_sold_items, months=months, dealers=dealers, sales_by_dealer=sales_by_dealer, product_name=product_name, sales_by_product=sales_by_product, number_sales_by_product=number_sales_by_product, number_sales_by_month=number_sales_by_month, sales_by_month=sales_by_month, costs_by_month=costs_by_month)   




###########################
#   PRODUCT MANAGEMENT    #
###########################

@app.route('/products')
def products():
    # Aquí puedes obtener la lista de productos desde la base de datos

    product_controller = ProductController(session)
    products = product_controller.get_all_products()
    
    return render_template('products.html', products=products)

@app.route('/product/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        
        # Obtener datos del formulario
        name = request.form['name']
        description = request.form['description']
        sale_price = request.form['sale_price']
        minimum_price = request.form['minimum_price']
        product_controller = ProductController(session)
        product = product_controller.add_product(name, description, sale_price, minimum_price)
        print(f"Product added: {product}")
        
        # Redirigir a la página principal
        return redirect(url_for('products'))
    
    return render_template('add_product.html')

@app.route('/product/<int:product_id>/delete', methods=['GET'])
def delete_product(product_id):
    product_controller = ProductController(session)
    if product_controller.delete_product(product_id):
        print("Product deleted.")
    else:
        print("Product not found.")
    
    return redirect(url_for('products'))

@app.route('/product/<int:product_id>/duplicate', methods=['GET'])
def duplicate_product(product_id):
    product_controller = ProductController(session)
    product = product_controller.get_product(product_id)
    if not product:
        return "Product not found", 404

    new_product = product_controller.add_product(
        name = product.name + " (Copy)",
        description = product.description,
        sale_price = product.sale_price,
        minimum_price = product.minimum_price
    )

    materials = product_controller.get_all_associated_materials(product_id)
    for material in materials:
        product_controller.associate_material(new_product.product_id, material.material_id, material.quantity)


    if new_product:
        print(f"Product duplicated: {new_product}")
    else:
        print("Error duplicating product.")
    

    return redirect(url_for('products'))

@app.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    product_controller = ProductController(session)
    product = product_controller.get_product(product_id)
    
    if not product:
        return "Product not found", 404
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        sale_price = request.form['sale_price']
        minimum_price = request.form['minimum_price']
        
        kwargs = {
            'name': name,
            'description': description,
            'sale_price': sale_price,
            'minimum_price': minimum_price
        }
        
        updated_product = product_controller.update_product(product_id, **kwargs)
        if updated_product:
            print(f"Product updated: {updated_product}")
        else:
            print("Product not found.")
        
        return redirect(url_for('products'))
    
    return render_template('edit_product.html', product=product)


@app.route('/product/<int:product_id>/config', methods=['GET', 'POST'])
def config_product(product_id):

    product_controller = ProductController(session)
    product = product_controller.get_product(product_id)

    if not product:
        return "Product not found", 404
    
    material_controller = MaterialController(session)
    materials = material_controller.get_all_materials()

    show_associated_materials =[]

    for material in materials:
        a = {
            'material_id': material.material_id,
            'name' : material.name,
            'quantity' : 0
        }
        asso = product_controller.get_associated_material(product_id, material.material_id)
        if asso and asso.quantity != 0:
            a['quantity'] = asso.quantity
        show_associated_materials.append(a)
   

    if request.method == 'POST':
        r = request
        for mat_id in r.form:
            quantity=r.form[mat_id]
            if int(quantity) == 0:
                if product_controller.delete_associated_materials(product_id, mat_id):
                    print("Material dissasociated")
            else:
                mat = product_controller.associate_material(product_id, mat_id, quantity)
                if mat:
                    print(f"Material Associated: {mat}")
                else:
                    print("Error ar associating materials to a product")

        return redirect(url_for('products'))
    
    return render_template('config_product.html', product=product, show_materials=show_associated_materials)

@app.route('/product/manufactured', defaults={'product_id': None})
@app.route('/product/<int:product_id>/manufactured', methods=['GET'])
def manufactured_items(product_id):

    product_controller = ProductController(session)
    manufactured_products = product_controller.get_all_manufactured_item(product_id)
    product = product_controller.get_product(product_id)
    return render_template('manufactured_products.html', product=product, manufactured_products=manufactured_products)

@app.route('/product/<int:product_id>/manufactured/add', methods=['GET', 'POST'])
def add_manufactured_item(product_id):

    product_controller = ProductController(session)
    product = product_controller.get_product(product_id)

    if not product:
        return "Product not found", 404

    if request.method == 'POST':
        
        # Obtener datos del formulario
        quantity = request.form['quantity']
        description = request.form['description']
        material_controller = MaterialController(session)

        for i in range(int(quantity)):
            manuf = product_controller.add_manufactured_item(product_id, description)
            product_materials = product_controller.get_all_associated_materials(product_id)
            for product_material in product_materials:
                material = material_controller.get_material(product_material.material_id)
                material_controller.update_stock(product_material.material_id, -1*product_material.quantity) 
        print(f"Manufactured item added: {manuf}")

        
        # Redirigir a la página principal
        return redirect(url_for('manufactured_items', product_id=product_id))
    
    return render_template('add_manufactured_item.html', product=product)

@app.route('/product/<int:product_id>/manufactured/<int:item_id>/delete', methods=['GET'])
def delete_manufactured_item(product_id, item_id):
    product_controller = ProductController(session)
    if product_controller.delete_manufactured_item(item_id):
        print("Manufactured item deleted.")
        material_controller = MaterialController(session)
        product_materials = product_controller.get_all_associated_materials(product_id)
        for product_material in product_materials:
            material = material_controller.get_material(product_material.material_id)
            material_controller.update_stock(product_material.material_id, product_material.quantity)
    else:
        print("Manufactured item not found.")       

    return redirect(url_for('manufactured_items', product_id=product_id))

@app.route('/product/<int:product_id>/manufactured/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_manufactured_item(product_id, item_id):

    product_controller = ProductController(session)
    product = product_controller.get_product(product_id)

    if not product:
        return "Product not found", 404

    manufactured_item = product_controller.get_manufactured_item(item_id)
    
    if not manufactured_item:
        return "Manufactured item not found", 404

    if request.method == 'POST':
        description = request.form['description']
        
        kwargs = {
            'description': description
        }
        
        updated_item = product_controller.update_manufactured_item(item_id, **kwargs)
        if updated_item:
            print(f"Manufactured item updated: {updated_item}")
        else:
            print("Manufactured item not found.")
        
        return redirect(url_for('manufactured_items', product_id=product_id))
    
    return render_template('edit_manufactured_item.html', product=product, manufactured_item=manufactured_item)

##########################
#   STOCK MANAGEMENT     #
##########################

@app.route('/materials')
def materials():
    material_controller = MaterialController(session)
    materials = material_controller.get_all_materials()
    
    return render_template('stock.html', materials=materials)

@app.route('/material/add', methods=['GET', 'POST'])
def add_material():
    if request.method == 'POST':
        
        # Obtener datos del formulario
        name = request.form['name']
        description = request.form['description']
        stock = request.form['stock']
        
        material_controller = MaterialController(session)
        material = material_controller.add_material(name, description, stock)
        print(f"Material added: {material}")
        
        # Redirigir a la página principal
        return redirect(url_for('materials'))
    
    return render_template('add_material.html')

@app.route('/material/<int:material_id>/delete', methods=['GET'])
def delete_material(material_id):
    material_controller = MaterialController(session)
    if material_controller.delete_material(material_id):
        print("Material deleted.")
    else:
        print("Material not found.")
    
    return redirect(url_for('materials'))

@app.route('/material/<int:material_id>/edit', methods=['GET', 'POST'])
def edit_material(material_id):
    material_controller = MaterialController(session)
    material = material_controller.get_material(material_id)
    
    if not material:
        return "Material not found", 404
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        stock = request.form['stock']
        
        kwargs = {
            'name': name,
            'description': description,
            'stock': stock
        }
        
        updated_material = material_controller.update_material(material_id, **kwargs)
        if updated_material:
            print(f"Material updated: {updated_material}")
        else:
            print("Material not found.")
        
        return redirect(url_for('materials'))
    
    return render_template('edit_material.html', material=material)

@app.route('/material/<int:material_id>/purchase/add', methods=['GET', 'POST'])
def purchase_material(material_id):
    material_controller = MaterialController(session)
    material = material_controller.get_material(material_id)
    
    if not material:
        return "Material not found", 404
    
    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        date_str = request.form['date']
        date = datetime.strptime(date_str, '%Y-%m-%d')
        
        purchase = material_controller.purchase_material(material_id, quantity, price, date)
        if purchase:
            print(f"Material purchased: {purchase}")
        else:
            print("Error in purchasing material.")
        
        return redirect(url_for('materials'))
    
    return render_template('purchase_material.html', material=material)

@app.route('/material/purchases', defaults={'material_id': None})
@app.route('/material/<int:material_id>/purchase/')
def view_material_purchases(material_id):
    material_controller = MaterialController(session)
    if material_id:
        material = material_controller.get_material(material_id)
        
        if not material:
            return "Material not found", 404

        purchases = material.purchases
        material_name = material.name
    else:
        purchases =[]
        materials = material_controller.get_all_materials()
        for material in materials:
            if material.purchases:
                purchases += material.purchases
        material_name = "All materials"
    
    return render_template('view_material_purchases.html', material_name=material_name, purchases=purchases)

@app.route('/material/<int:material_id>/purchase/<int:purchase_id>/delete', methods=['GET'])
def delete_material_purchase(material_id, purchase_id):
    material_controller = MaterialController(session)
    material = material_controller.get_material(material_id)
    
    if not material:
        return "Material not found", 404
    
    purchase = None
    for p in material.purchases:
        if p.purchase_id == purchase_id:
            purchase = p
            break
    
    if not purchase:
        return "Purchase not found", 404
    
    quantity = purchase.quantity
    if material_controller.delete_material_purchase(purchase_id):
        print("Purchase deleted.")
    else:
        print("Error deleting purchase.")
    
    return redirect(url_for('view_material_purchases', material_id=material_id))

@app.route('/material/<int:material_id>/purchase/<int:purchase_id>/edit', methods=['GET', 'POST'])
def edit_material_purchase(material_id, purchase_id):
    material_controller = MaterialController(session)
    material = material_controller.get_material(material_id)
    
    if not material:
        return "Material not found", 404
    
    purchase = None
    for p in material.purchases:
        if p.purchase_id == purchase_id:
            purchase = p
            break
    
    if not purchase:
        return "Purchase not found", 404
    
    if request.method == 'POST':
        old_quantity = purchase.quantity
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        date_str = request.form['date']
        date = datetime.strptime(date_str, '%Y-%m-%d')
        
        purchase.quantity = quantity
        purchase.price = price
        purchase.date = date
        
        material_controller.update_stock(material_id, quantity - old_quantity)
        material_controller.session.commit()
        
        print(f"Purchase updated: {purchase}")
        
        return redirect(url_for('view_material_purchases', material_id=material_id))
    
    return render_template('edit_material_purchase.html', material=material, purchase=purchase)

############################
#   DEALER MANAGEMENT      #
############################

@app.route('/dealers')
def dealers():
    dealer_controller = DealerController(session)
    dealers = dealer_controller.get_all_dealers()
    
    return render_template('dealers.html', dealers=dealers)


@app.route('/dealer/add', methods=['GET', 'POST'])
def add_dealer():
    if request.method == 'POST':
        
        # Obtener datos del formulario
        name = request.form['name']
        
        dealer_controller = DealerController(session)
        dealer = dealer_controller.add_dealer(name)
        print(f"Dealer added: {dealer}")
        
        # Redirigir a la página principal
        return redirect(url_for('dealers'))
    
    return render_template('add_dealer.html')

@app.route('/dealer/<int:dealer_id>/delete', methods=['GET'])
def delete_dealer(dealer_id):
    dealer_controller = DealerController(session)
    if dealer_controller.delete_dealer(dealer_id):
        print("Dealer deleted.")
    else:
        print("Dealer not found.")
        
    return redirect(url_for('dealers'))

@app.route('/dealer/<int:dealer_id>/edit', methods=['GET', 'POST'])
def edit_dealer(dealer_id):
    dealer_controller = DealerController(session)
    dealer = dealer_controller.get_dealer(dealer_id)
    if not dealer:
        return "Dealer not found", 404
    
    if request.method == 'POST':
        name = request.form['name']
        
        kwargs = {
            'name': name
        }
        
        updated_dealer = dealer_controller.update_dealer(dealer_id, **kwargs)
        if updated_dealer:
            print(f"Dealer updated: {updated_dealer}")
        else:
            print("Dealer not found.")
        
        return redirect(url_for('dealers'))
    
    return render_template('edit_dealer.html', dealer=dealer)


######################
#       SALES        #
######################
@app.route('/sales', defaults={'dealer_id': None})
@app.route('/dealer/<int:dealer_id>/sales')
def sales(dealer_id):
    if dealer_id:
        dealer_controller = DealerController(session)
        dealer = dealer_controller.get_dealer(dealer_id)
        if not dealer:
            return "Dealer not found", 404
        sales = dealer_controller.get_dealer_sales(dealer_id)

    else:
        sale_controller = SaleController(session)
        sales = sale_controller.get_all_sales()

    return render_template('sales.html', sales=sales)
    
@app.route('/dealer/<int:dealer_id>/sale/add', methods=['GET', 'POST'])
def add_sale_dealer(dealer_id):
    dealer_controller = DealerController(session)
    dealer = dealer_controller.get_dealer(dealer_id)
    proudct_controller = ProductController(session)

    manufactureditems_controller = ManufacturedItemController(session)
    items = manufactureditems_controller.get_not_sold_items()

    if not dealer:
        return "Dealer not found", 404
    
    if request.method == 'POST':
        
        # Obtener datos del formulario
        date_str = request.form['date']
        items = []
        for item_id in request.form.getlist('items[]'):
            print(f"Selected item ID: {item_id}")
            items.append(proudct_controller.get_manufactured_item(item_id))

        
        
        date = datetime.strptime(date_str, '%Y-%m-%d')
        price =  request.form['price']
        
        
        sale = dealer_controller.record_sale(items,date,price,dealer_id)
        print(f"Sale added to dealer: {sale}")
        
        # Redirigir a la página principal
        return redirect(url_for('sales', dealer_id=dealer_id))
    
    return render_template('add_sale_dealer.html', dealer=dealer, items=items)

@app.route('/dealer/<int:dealer_id>/sale/<int:sale_id>/edit', methods=['GET', 'POST'])
def edit_sale(dealer_id, sale_id):
    dealer_controller = DealerController(session)
    dealer = dealer_controller.get_dealer(dealer_id)
    if not dealer:
        return "Dealer not found", 404

    sale_controller = SaleController(session)
    sale = sale_controller.get_sale(sale_id)
    if not sale:
        return "Sale not found", 404
    
    if request.method == 'POST':
        #item_id = request.form['items_id']  # For simplicity, we won't change items here
        date_str = request.form['date']
        date = datetime.strptime(date_str, '%Y-%m-%d')
        price = request.form['price']
        
        kwargs = {
            #'items': items,  # Not changing items for simplicity
            'date': date,
            'price': price
        }
        
        updated_sale = sale_controller.update_sale(sale_id, **kwargs)
        if updated_sale:
            print(f"Sale updated: {updated_sale}")
        else:
            print("Sale not found.")
        
        return redirect(url_for('sales', dealer_id=dealer_id))
    
    return render_template('edit_sale_dealer.html', dealer=dealer, sale=sale)


@app.route('/dealer/<int:dealer_id>/sale/<int:sale_id>/delete', methods=['GET'])
def delete_sale(dealer_id, sale_id):
    sale_controller = SaleController(session)
    if sale_controller.delete_sale(sale_id):
        print("Sale deleted.")
    else:
        print("Sale not found.")
    return redirect(url_for('sales', dealer_id=dealer_id))
 

if __name__ == '__main__':
    load_dotenv()

    engine = create_engine(os.getenv('DATABASE_URL'))
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    app.run(debug=True, host=os.getenv('SERVER_HOST'), port=os.getenv('SERVER_PORT'))