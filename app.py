from flask import Flask, render_template, request, redirect, url_for

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

from model.model import Product, Base
from controller.controller import ProductController, MaterialController

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


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


if __name__ == '__main__':
    engine = create_engine('sqlite:///example.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    app.run(debug=True)

'''
def main_menu():
    while True:
        print("\n\n--- Main Menu ---");
        print("1. Manage Products")
        print("2. Manage Stock")
        print("3. Manage Sales")
        print("4. Exit")
        
        try:
            choice = int(input("Seleccione una opción: "))
        except ValueError:
            print("Por favor, ingrese un número válido.")
            continue


        if choice == 1:
            product_menu()
        elif choice == 2:
            stock_menu()
        #elif choice == 3:
        #    sales_menu()
        elif choice == 4:
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

def product_menu():
    product_controller = ProductController(session)
    while True:
        print("\n--- Products ---")
        products = product_controller.get_all_products()
        for prod in products:
            print(prod)

        print("\n\n--- Product Management ---")
        print("1. Add Product")
        print("2. View All Products")
        print("3. Update Product")
        print("4. Delete Product")
        print("5. Associate Material to Product")
        print("6. Back to Main Menu")
        
        try:
            choice = int(input("Seleccione una opción: "))
        except ValueError:
            print("Por favor, ingrese un número válido.")
            continue

        # 1. Add Product
        if choice == 1:
            name = input("Enter product name: ")
            description = input("Enter product description: ")
            sale_price = float(input("Enter sale price: "))
            product = product_controller.add_product(name, description, sale_price)
            print(f"Product added: {product}")

        # 2. View All Products
        elif choice == 2:
            products = product_controller.get_all_products()
            for prod in products:
                print(prod)

        # 3. Update Product
        elif choice == 3:
            product_id = int(input("Enter product ID to update: "))
            name = input("Enter new name (leave blank to keep current): ")
            description = input("Enter new description (leave blank to keep current): ")
            sale_price_input = input("Enter new sale price (leave blank to keep current): ")
            kwargs = {}
            if name:
                kwargs['name'] = name
            if description:
                kwargs['description'] = description
            if sale_price_input:
                kwargs['sale_price'] = float(sale_price_input)
            updated_product = product_controller.update_product(product_id, **kwargs)
            if updated_product:
                print(f"Product updated: {updated_product}")
            else:
                print("Product not found.")
        
        # 4. Delete Product
        elif choice == 4:
            product_id = int(input("Enter product ID to delete: "))
            if product_controller.delete_product(product_id):
                print("Product deleted.")
            else:
                print("Product not found.")
        
        # 5. Associate Material to Product
        elif choice == 5:
            product_id = int(input("Enter product ID: "))
            material_id = int(input("Enter material ID to associate: "))
            quantity = int(input("Enter quantity of material: "))
            association = product_controller.associate_material(product_id, material_id, quantity)
            print(f"Material associated: {association}")


        # 6. Back to menu
        elif choice == 6:
            break
        else:
            print("Opción no válida. Intente de nuevo.")


def stock_menu():
    material_controller = MaterialController(session)
    while True:
        print("\n--- Stock Management ---")
        print("1. Add Material type")
        print("2. View All Materials types")
        print("3. Update Material type")
        print("4. Delete Material")
        print("5. Buy Material")
        print("6. Back to Main Menu")
        
        try:
            choice = int(input("Seleccione una opción: "))
        except ValueError:
            print("Por favor, ingrese un número válido.")
            continue

        # 1. Add Material
        if choice == 1:
            name = input("Enter material name: ")
            description = input("Enter material description: ")
            material = material_controller.add_material(name, description)
            print(f"Material added: {material}")

        # 2. View All Materials
        elif choice == 2:
            materials = material_controller.get_all_materials()
            for mat in materials:
                print(mat)

        # 3. Update Material
        elif choice == 3:
            material_id = int(input("Enter material ID to update: "))
            name = input("Enter new name (leave blank to keep current): ")
            description = input("Enter new description (leave blank to keep current): ")
            kwargs = {}
            if name:
                kwargs['name'] = name
            if description:
                kwargs['description'] = description
            updated_material = material_controller.update_material(material_id, **kwargs)
            if updated_material:
                print(f"Material updated: {updated_material}")
            else:
                print("Material not found.")
        
        # 4. Delete Material
        elif choice == 4:
            material_id = int(input("Enter material ID to delete: "))
            if material_controller.delete_material(material_id):
                print("Material deleted.")
            else:
                print("Material not found.")

        # 5. Buy Material
        elif choice == 5:
            material_id = int(input("Enter material ID to purchase: "))
            quantity = int(input("Enter quantity to purchase: "))
            price = float(input("Enter purchase price: "))
            date_input = input("Enter purchase date (YYYY-MM-DD): ")
            date = datetime.strptime(date_input, "%Y-%m-%d").date()
            purchase = material_controller.purchase_material(material_id, quantity, price, date)
            if purchase:
                print(f"Material purchased: {purchase}")
            else:
                print("Material not found.")
        
        elif choice == 6:
            break
        else:
            print("Opción no válida. Intente de nuevo.")


if __name__ == "__main__":

    # Database setup
    engine = create_engine('sqlite:///example.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    main_menu()
'''


