from model.model import Material, MaterialPurchase, Product, ManufacturedItem, Dealer, Sale, ProductMaterial


class ProductController:
    def __init__(self, session):
        self.session = session

    def add_product(self, name, description, sale_price):
        new_product = Product(name=name, description=description, sale_price=sale_price)
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
    
    def add_manufactured_item(self, product_id, description, cost_price, sale_id=None):
        new_item = ManufacturedItem(product_id=product_id, description=description, cost_price=cost_price, sale_id=sale_id)
        self.session.add(new_item)
        self.session.commit()
        return new_item

    def associate_material(self, product_id, material_id, quantity):
        new_association = ProductMaterial(product_id=product_id, material_id=material_id, quantity=quantity)
        self.session.add(new_association)
        self.session.commit()
        return new_association



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

    def update_stock(self, material_id, quantity):
        material = self.get_material(material_id)
        if not material:
            return None
        material.stock = (material.stock or 0) + quantity
        self.session.commit()
        

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

    def record_sale(self, items_id, date, price, dealer_id):
        dealer = self.get_dealer(dealer_id)
        if not dealer:
            return None
        new_sale = Sale(items_id=items_id, date=date, price=price, dealer_id=dealer_id)
        self.session.add(new_sale)
        self.session.commit()
        return new_sale