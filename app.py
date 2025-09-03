from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from model.model import Product, Base
from controller.controller import ProductController

def main_menu():
    while True:
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
        #elif choice == 2:
        #    stock_menu()
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

        elif choice == 5:
            material_id = int(input("Enter material ID to purchase: "))
            quantity = int(input("Enter quantity to purchase: "))
            price = float(input("Enter purchase price: "))
            date = input("Enter purchase date (YYYY-MM-DD): ")
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
