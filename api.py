from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from faker import Faker

app = Flask(__name__)

base_dir = os.path.abspath(os.path.dirname(__file__))
db_dir = os.path.join(base_dir, 'data')
os.makedirs(db_dir, exist_ok=True)

db_path_assets = os.path.join(db_dir, 'assets.db')

app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path_assets}'
db = SQLAlchemy(app)

class Asset(db.Model):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    serial_no = db.Column(db.String(50))
    model = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    status = db.Column(db.String(50))

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    department = db.Column(db.String(100))
    admin = db.Column(db.Boolean)
    password = db.Column(db.String(80))

class AssignedAsset(db.Model):
    __tablename__ = 'assigned_assets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    serial_no = db.Column(db.Integer)
    model = db.Column(db.String(50))
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'))
    status = db.Column(db.Boolean)
    assigned_to = db.Column(db.String(100))
    assigned_date = db.Column(db.Date)

class RequestedAsset(db.Model):
    __tablename__ = 'requested_assets'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'))
    employee_id = db.Column(db.Integer)
    status = db.Column(db.String(50))

def init_db():
    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")

def generate_fake_data():
    fake = Faker()  # Moved Faker initialization inside the function
    with app.app_context():
        for _ in range(10):
            asset = Asset(
                name=fake.word(),
                serial_no=fake.random_int(min=1000, max=9999),
                model=fake.word(),
                brand=fake.company(),
                status=fake.random_element(elements=('Available', 'In Use', 'Maintenance'))
            )
            db.session.add(asset)

        for _ in range(5):
            employee = Employee(
                public_id=str(fake.uuid4()),
                name=fake.name(),
                department=fake.job(),
                admin=fake.boolean(),
                password=fake.password()
            )
            db.session.add(employee)

        for _ in range(8):
            assigned_asset = AssignedAsset(
                name=fake.word(),
                serial_no=fake.random_int(min=1000, max=9999),
                model=fake.word(),
                asset_id=fake.random_int(min=1, max=10),
                status=fake.boolean(),
                assigned_to=fake.name(),
                assigned_date=fake.date_this_year()
            )
            db.session.add(assigned_asset)

        for _ in range(7):
            requested_asset = RequestedAsset(
                asset_id=fake.random_int(min=1, max=10),
                employee_id=fake.random_int(min=1, max=5),
                status=fake.random_element(elements=('Pending', 'Approved', 'Rejected'))
            )
            db.session.add(requested_asset)

        db.session.commit()
        print("Fake data generated and added to the database.")

if __name__ == '__main__':
    init_db()
    generate_fake_data()
    app.run(debug=True)
