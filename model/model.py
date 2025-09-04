from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table, Numeric
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    
    product_id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    sale_price = Column(Numeric(10, 2), nullable=False)
    manufactured_items  = relationship("ManufacturedItem", back_populates="product", cascade="all, delete-orphan")  
    materials = relationship("ProductMaterial", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(product_id={self.product_id}, name={self.name}, sale_price={self.sale_price})>"

class ProductMaterial(Base):
    __tablename__ = 'product_materials'
    
    product_material_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    material_id = Column(Integer, ForeignKey('materials.material_id'), nullable=False)
    quantity = Column(Integer)

    product = relationship("Product", back_populates="materials")
    material = relationship("Material", back_populates="products")

    def __repr__(self):
        return f"<ProductMaterial(product_id={self.product_id}, material_id={self.material_id}, quantity={self.quantity})>"


class ManufacturedItem(Base):
    __tablename__ = 'manufactured_items'
    
    item_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    description = Column(String)
    cost_price = Column(Numeric(10, 2), nullable=False)
    sale_id = Column(Integer, ForeignKey('sales.sale_id'))
    product = relationship("Product", back_populates="manufactured_items")

    manufactured = relationship("Sale", back_populates="items_id")

    def __repr__(self):
        return f"<manufacturedItem(item_id={self.item_id}, name={self.name}, cost_price={self.cost_price})>"


class Material(Base):
    __tablename__ = 'materials'
    
    material_id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    stock = Column(Integer)
    purchases = relationship("MaterialPurchase", back_populates="material", cascade="all, delete-orphan")
    products = relationship("ProductMaterial", back_populates="material", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Material(material_id={self.material_id}, name={self.name})>"

class MaterialPurchase(Base):
    __tablename__ = 'material_purchases'
    
    purchase_id = Column(Integer, primary_key=True)
    material_id = Column(Integer, ForeignKey('materials.material_id'), nullable=False)
    date  = Column(Date)
    quantity = Column(Integer)
    price = Column(Numeric(10, 2), nullable=False)

    material = relationship("Material", back_populates="purchases")

    def __repr__(self):
        return f"<MaterialPurchase(material_id={self.material_id}, quantity={self.quantity}, price={self.price})>"


class Dealer(Base):
    __tablename__ = 'dealers'
    
    dealer_id = Column(Integer, primary_key=True)
    name = Column(String)

    sales = relationship("Sale", back_populates="dealer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Dealer(dealer_id={self.dealer_id}, name={self.name})>"


class Sale(Base):
    __tablename__ = 'sales'
    
    sale_id = Column(Integer, primary_key=True)
    items_id = relationship("ManufacturedItem", back_populates="manufactured", cascade="all, delete-orphan")
    date = Column(Date)
    price = Column(Numeric(10, 2), nullable=False)
    dealer_id = Column(Integer, ForeignKey('dealers.dealer_id'), nullable=False)

    dealer = relationship("Dealer", back_populates="sales")

    def __repr__(self):
        return f"<Sale(product_id={self.product_id}, quantity={self.quantity})>"



