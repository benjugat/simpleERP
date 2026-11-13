from model.model import Material, MaterialPurchase, Product, ManufacturedItem, Dealer, Sale, ProductMaterial, Model, ProductModel


class ProductController:
    def __init__(self, session):
        self.session = session

    def add_product(self, name, description, sale_price, product_type):
        new_product = Product(name=name, description=description, sale_price=sale_price, product_type=product_type)    
        self.session.add(new_product)
        self.session.commit()
        return new_product

    def get_product(self, product_id):
        return self.session.query(Product).filter_by(product_id=product_id).first()
    
    def get_all_products(self):
        return self.session.query(Product).all()

    def update_product(self, product_id, **kwargs):
        product = self.get_product(product_id)
        if not product:
            return None
        for key, value in kwargs.items():
            setattr(product, key, value)
        self.session.commit()
        return product

    def delete_product(self, product_id):
        product = self.get_product(product_id)
        if not product:
            return False
        self.session.delete(product)
        self.session.commit()
        return True
    
    def add_manufactured_item(self, product_id, description, sale_id=None):
        new_item = ManufacturedItem(product_id=product_id, description=description, sale_id=sale_id)
        self.session.add(new_item)
        self.session.commit()
        return new_item

    def delete_manufactured_item(self, item_id):
        item = self.session.query(ManufacturedItem).filter_by(item_id=item_id).first()
        if not item:
            return False
        self.session.delete(item)
        self.session.commit()
        return True

    def get_manufactured_item(self, item_id):
        return self.session.query(ManufacturedItem).filter_by(item_id=item_id).first()

    def update_manufactured_item(self, item_id, **kwargs):
        item = self.get_manufactured_item(item_id)
        if not item:
            return None
        for key, value in kwargs.items():
            setattr(item, key, value)
        self.session.commit()
        return item

    def get_all_manufactured_item(self, product_id):
        return self.session.query(ManufacturedItem).filter_by(product_id=product_id).all()

    def associate_material(self, product_id, material_id, quantity):
        new_association = ProductMaterial(product_id=product_id, material_id=material_id, quantity=quantity)
        self.session.add(new_association)
        self.session.commit()
        return new_association
    
    def associate_model(self, product_id, model_id, checked):
        new_association = ProductModel(product_id=product_id, model_id=model_id, checked=checked)
        self.session.add(new_association)
        self.session.commit()
        return new_association

    def get_all_associated_materials(self, product_id):
        return self.session.query(ProductMaterial).filter_by(product_id=product_id).all()

    def get_associated_material(self, product_id, material_id):
        return self.session.query(ProductMaterial).filter_by(product_id=product_id).filter_by(material_id=material_id).first()

    def delete_associated_materials(self, product_id, material_id):
        material = self.get_associated_material(product_id, material_id)
        if not material:
            return False
        self.session.delete(material)
        self.session.commit()
        return True

    def update_associated_material(self, product_id, material_id, quantity):
        association = self.get_associated_material(product_id, material_id)
        if not association:
            return None
        association.quantity = quantity
        self.session.commit()
        return association
    
    def get_associated_model(self, product_id, model_id):
        return self.session.query(ProductModel).filter_by(product_id=product_id).filter_by(model_id=model_id).first()
    
    def get_all_associated_models(self, product_id):
        return self.session.query(ProductModel).filter_by(product_id=product_id).all()
    
    def delete_associated_model(self, product_id, model_id):
        association = self.get_associated_model(product_id, model_id)
        if not association:
            return False
        self.session.delete(association)
        self.session.commit()
        return True
    
    def delete_all_associated_models(self, product_id):
        associations = self.session.query(ProductModel).filter_by(product_id=product_id).all()
        for association in associations:
            self.session.delete(association)
        self.session.commit()
        return True
    
    def update_associated_model(self, product_id, model_id, checked):
        association = self.get_associated_model(product_id, model_id)
        if not association:
            return None
        association.checked = checked
        self.session.commit()
        return association
    
    def calculate_product_cost(self, product_id):
        breakdown = self.calculate_product_cost_breakdown(product_id)
        return breakdown['total']

    def calculate_product_cost_breakdown(self, product_id):
        consumables_cost = 0
        printing_cost = 0
        consumables = []
        printing = []
        price_kwh = 0.06
        potency_ender3 = 120 #watts
        material_controller = MaterialController(self.session)

        # consumables
        associated_materials = self.get_all_associated_materials(product_id)
        for association in associated_materials:
            material = material_controller.get_material(association.material_id)
            unit_cost = float(material_controller.calculate_cost_by_unity(association.material_id))
            line_cost = round(unit_cost * float(association.quantity or 0), 2)
            consumables_cost += line_cost
            consumables.append({
                'name': material.name if material else f"Material {association.material_id}",
                'quantity': association.quantity or 0,
                'unit_cost': unit_cost,
                'total_cost': line_cost
            })

        # filament
        associated_models = self.get_all_associated_models(product_id)

        for association in associated_models:
            model = self.session.query(Model).filter_by(model_id=association.model_id).first()
            if not model:
                continue
            print_time_minutes = int(model.print_time_minutes or 0)
            hours = print_time_minutes / 60
            material = material_controller.get_material(model.filament_material_id) if model.filament_material_id else None
            weight = float(model.filament_weight_g or 0)
            filament_unit_cost = float(material_controller.calculate_cost_by_unity(model.filament_material_id)) if model.filament_material_id else 0
            filament_cost = round(filament_unit_cost * weight, 2)
            electricity_cost = round(hours * (potency_ender3 / 1000) * price_kwh, 2)
            model_printing_cost = round(filament_cost + electricity_cost, 2)
            printing_cost += model_printing_cost
            print_hours, remaining_minutes = divmod(print_time_minutes, 60)
            print_time_label = f"{print_hours} h {remaining_minutes} min" if print_hours else f"{remaining_minutes} min"
            printing.append({
                'model_name': model.name,
                'print_time': print_time_label,
                'material_name': material.name if material else 'Sin filamento seleccionado',
                'weight': weight,
                'filament_cost': filament_cost,
                'electricity_cost': electricity_cost,
                'total_cost': model_printing_cost
            })

        product = self.get_product(product_id)
        consumables_cost = round(consumables_cost, 2)
        printing_cost = round(printing_cost, 2)
        total_cost = round(consumables_cost + printing_cost, 2)
        product.consumables_cost = consumables_cost
        product.printing_cost = printing_cost
        product.cost_price = total_cost
        self.session.commit()
        return {
            'consumables': consumables,
            'printing': printing,
            'consumables_total': consumables_cost,
            'printing_total': printing_cost,
            'total': total_cost
        }
    


class ManufacturedItemController:
    def __init__(self, session):
        self.session = session

    def get_manufactured_item(self, item_id):
        return self.session.query(ManufacturedItem).filter_by(item_id=item_id).first()

    def get_all_manufactured_items(self):
        return self.session.query(ManufacturedItem).all()
    
    def get_not_sold_items(self):
        return self.session.query(ManufacturedItem).filter_by(sale_id=None).all()

class MaterialController:
    def __init__(self, session):
        self.session = session

    def add_material(self, name, description, stock=0, material_type='consumable'):
        new_material = Material(name=name, description=description, stock=stock, material_type=material_type)
        self.session.add(new_material)
        self.session.commit()
        return new_material

    def get_material(self, material_id):
        return self.session.query(Material).filter_by(material_id=material_id).first()
    
    def get_all_materials(self):
        return self.session.query(Material).all()

    def get_all_filaments(self):
        return self.session.query(Material).filter_by(material_type='filament').all()

    def get_all_consumables(self):
        return self.session.query(Material).filter_by(material_type='consumable').all()
    
    def update_material(self, material_id, **kwargs):
        material = self.get_material(material_id)
        if not material:
            return None
        for key, value in kwargs.items():
            setattr(material, key, value)
        self.session.commit()
        return material

    def delete_material(self, material_id):
        material = self.get_material(material_id)
        if not material:
            return False
        self.session.delete(material)
        self.session.commit()
        return True


    def purchase_material(self, material_id, quantity, price, date):
        material = self.get_material(material_id)
        if not material:
            return None
        new_purchase = MaterialPurchase(material_id=material_id, quantity=quantity, price=price, date=date)
        self.update_stock(material_id, quantity)
        self.session.add(new_purchase)
        self.session.commit()
        return new_purchase
    
    def get_purchase(self, purchase_id):
        return self.session.query(MaterialPurchase).filter_by(purchase_id=purchase_id).first()
    
    def get_all_purchases(self):
        return self.session.query(MaterialPurchase).all()

    def calculate_cost_by_unity(self, material_id):
        purchases = self.session.query(MaterialPurchase).filter_by(material_id=material_id).all()
        total_quantity = sum(purchase.quantity for purchase in purchases)
        total_cost = sum(purchase.price for purchase in purchases)
        if total_quantity == 0:
            return 0
        return total_cost / total_quantity
    
    def delete_material_purchase(self, purchase_id):
        purchase = self.get_purchase(purchase_id)
        if not purchase:
            return False
        self.update_stock(purchase.material_id, -purchase.quantity)
        self.session.delete(purchase)
        self.session.commit()
        return True

    def update_material_purchase(self, purchase_id, **kwargs):
        purchase = self.get_purchase(purchase_id)
        self.update_stock(purchase.material_id, -purchase.quantity)
        if not purchase:
            return None
        for key, value in kwargs.items():
            setattr(purchase, key, value)
        self.update_stock(purchase.material_id, purchase.quantity)
        self.session.commit()
        return purchase
    
    def update_stock(self, material_id, quantity):
        material = self.get_material(material_id)
        if not material:
            return None
        material.stock = (material.stock or 0) + quantity
        self.session.commit()

    def get_year_purchases(self, year):
        return self.session.query(MaterialPurchase).filter(MaterialPurchase.date.between(f'{year}-01-01', f'{year}-12-31')).all()        

    def get_month_purchases(self, year, month):
        start_date = f'{year}-{month:02d}-01'
        if month == 12:
            end_date = f'{year + 1}-01-01'
        else:
            end_date = f'{year}-{month + 1:02d}-01'
        return self.session.query(MaterialPurchase).filter(MaterialPurchase.date.between(start_date, end_date)).all()
    
class DealerController:
    def __init__(self, session):
        self.session = session

    def add_dealer(self, name):
        new_dealer = Dealer(name=name)
        self.session.add(new_dealer)
        self.session.commit()
        return new_dealer

    def get_dealer(self, dealer_id):
        return self.session.query(Dealer).filter_by(dealer_id=dealer_id).first()
    
    def get_all_dealers(self):
        return self.session.query(Dealer).all()

    def update_dealer(self, dealer_id, **kwargs):
        dealer = self.get_dealer(dealer_id)
        if not dealer:
            return None
        for key, value in kwargs.items():
            setattr(dealer, key, value)
        self.session.commit()
        return dealer

    def delete_dealer(self, dealer_id):
        dealer = self.get_dealer(dealer_id)
        if not dealer:
            return False
        self.session.delete(dealer)
        self.session.commit()
        return True

    def record_sale(self, items, date, price, dealer_id):
        dealer = self.get_dealer(dealer_id)
        if not dealer:
            return None
        new_sale = Sale(items=items, date=date, price=price, dealer_id=dealer_id)
        self.session.add(new_sale)
        self.session.commit()
        return new_sale
    
    def get_dealer_sales(self, dealer_id):
        return self.session.query(Sale).filter_by(dealer_id=dealer_id).all()
    
    def get_dealer_sales_by_year(self, dealer_id, year):
        return self.session.query(Sale).filter_by(dealer_id=dealer_id).filter(Sale.date.between(f'{year}-01-01', f'{year}-12-31')).all()
    
    
class SaleController:
    def __init__(self, session):
        self.session = session

    def get_sale(self, sale_id):
        return self.session.query(Sale).filter_by(sale_id=sale_id).first()
    
    def get_all_sales(self):
        return self.session.query(Sale).all()
    
    def update_sale(self, sale_id, **kwargs):
        sale = self.get_sale(sale_id)
        if not sale:
            return None
        for key, value in kwargs.items():
            setattr(sale, key, value)
        self.session.commit()
        return sale
    
    def delete_sale(self, sale_id):
        sale = self.get_sale(sale_id)
        if not sale:
            return False
        self.session.delete(sale)
        self.session.commit()
        return True
    
    def get_year_sales(self, year):
        return self.session.query(Sale).filter(Sale.date.between(f'{year}-01-01', f'{year}-12-31')).all()
    
    def get_month_sales(self, year, month):
        start_date = f'{year}-{month:02d}-01'
        if month == 12:
            end_date = f'{year + 1}-01-01'
        else:
            end_date = f'{year}-{month + 1:02d}-01'
        return self.session.query(Sale).filter(Sale.date.between(start_date, end_date)).all()
    
class MaterialPurchaseController:
    def __init__(self, session):
        self.session = session
    
    def get_all_purchases(self):
        return self.session.query(MaterialPurchase).all()


class ModelController:
    def __init__(self, session):
        self.session = session

    def get_all_models(self):
        return self.session.query(Model).all()
    
    def get_model(self, model_id):
        return self.session.query(Model).filter_by(model_id=model_id).first()
    
    def add_model(self, name, description, filepath, filament_material_id=None, filament_weight_g=0, print_time_minutes=0):
        new_model = Model(
            name=name,
            description=description,
            filepath=filepath,
            filament_material_id=filament_material_id,
            filament_weight_g=filament_weight_g,
            print_time_minutes=print_time_minutes
        )
        self.session.add(new_model)
        self.session.commit()
        return new_model
    
    def update_model(self, model_id, **kwargs):
        model = self.session.query(Model).filter_by(model_id=model_id).first()
        if not model:
            return None
        for key, value in kwargs.items():
            setattr(model, key, value)
        self.session.commit()
        return model
    
    def delete_model(self, model_id):
        model = self.session.query(Model).filter_by(model_id=model_id).first()
        if not model:
            return False
        self.session.delete(model)
        self.session.commit()
        return True
    
