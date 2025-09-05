from flask import Flask, render_template, request, redirect, url_for

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

from model.model import Product, Base
from controller.controller import ProductController, MaterialController, DealerController, SaleController

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

#####################################
#   PRODUCT MANAGEMENT              #
#####################################

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
        sale_price = request.form['price']
        
        product_controller = ProductController(session)
        product = product_controller.add_product(name, description, sale_price)
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

@app.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    product_controller = ProductController(session)
    product = product_controller.get_product(product_id)
    
    if not product:
        return "Product not found", 404
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        sale_price = request.form['price']
        
        kwargs = {
            'name': name,
            'description': description,
            'sale_price': sale_price
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

    
    # solucion rapida, disasociar todo, asociar de nuevo?
    # otra solucion disasociar si es 0

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
            print(quantity)
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


#####################################
#   STOCK MANAGEMENT                #
#####################################

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



#####################################
#   DEALER MANAGEMENT               #
#####################################

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


#####################################
#   SALES                           #
#####################################
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
    if not dealer:
        return "Dealer not found", 404
    
    if request.method == 'POST':
        
        # Obtener datos del formulario
        item_id = request.form['items_id']
        # meter checkbox con todos los manufactured itemss
        #partial fix:
        items_id = [item_id]
        date = request.form['date']
        price =  request.form['price']
        
        
        sale = dealer_controller.record_sale(items_id,date,price,dealer_id)
        print(f"Sale added to dealer: {sale}")
        
        # Redirigir a la página principal
        return redirect(url_for('sales', dealer_id=dealer_id))
    
    return render_template('add_sale_dealer.html', dealer=dealer)



if __name__ == '__main__':
    engine = create_engine('sqlite:///example.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    app.run(debug=True)