from model.model import Material, MaterialPurchase, Product, ManufacturedItem, Dealer, Sale, ProductMaterial


class ProductController:
    def __init__(self, session):
        self.session = session

    def add_product(self, name, description, sale_price, minimum_price, product_type):
        new_product = Product(name=name, description=description, sale_price=sale_price, minimum_price=minimum_price, product_type=product_type)    
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

    def add_material(self, name, description, stock=0):
        new_material = Material(name=name, description=description, stock=stock)
        self.session.add(new_material)
        self.session.commit()
        return new_material

    def get_material(self, material_id):
        return self.session.query(Material).filter_by(material_id=material_id).first()
    
    def get_all_materials(self):
        return self.session.query(Material).all()

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