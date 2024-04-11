from flask import Flask, request, jsonify, make_response, render_template, session
from flask_sqlalchemy import SQLAlchemy
import os
import uuid
from faker import Faker
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash 
import jwt
import datetime
from datetime import timedelta
from functools import wraps



app = Flask(__name__)
jwt = JWTManager(app)

base_dir = os.path.abspath(os.path.dirname(__file__))
db_dir = os.path.join(base_dir, 'data')
os.makedirs(db_dir, exist_ok=True)

db_path_assets = os.path.join(db_dir, 'assets.db')

app.config['SECRET_KEY'] = '4023cdeb28be4c9dbfd5b6c03dd8a847'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path_assets}'
db = SQLAlchemy(app)
fake = Faker()  

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


def token_required(func):
    @wraps(func)
    def decorated(*args):
        token = request/args.get('token')
        if not token:
            return jsonify({'Alert!': 'Token is missing!'})
        try:
            payload =jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'Alert!': 'Invalid Token!'})
        
    return decorated

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return 'Logged in currently!'
    
@app.route('/public')
def public():
    return 'For Public'

@app.route('/auth')
@jwt_required()
def auth():
    return 'JWT is verified. Welcome to your dahsboard!'
    
@app.route('/login', methods=['POST'])
def login():
   if request.form['username'] and request.form['password'] == '123456':
        session['logged_in'] =  True
        token = jwt.encode({
            'user': request.form['username'],
            'expiration': str(datetime.utcnow() + timedelta(seconds=120))
        },
           app.config['SECRET_KEY'])
        return jsonify({'token':token.decode('utf-8')})
   else:
       return make_response('Unable to verify', 403, {'WWW-Authenticate': 'Basic ealm:"Authentication Failed!'})

@app.route('/assets', methods=['GET'])
# @jwt_required()
def get_all_assets():
    assets = Asset.query.all()
    asset_list = []
    for asset in assets:
        asset_data = {
            'id': asset.id,
            'name': asset.name,
            'serial_no': asset.serial_no,
            'model': asset.model,
            'brand': asset.brand,
            'status': asset.status
        }
        asset_list.append(asset_data)
    return jsonify(asset_list)

@app.route('/assets/<int:asset_id>', methods=['GET'])
def get_asset(asset_id):
    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({'message': 'Asset not found'}), 404
    asset_data = {
        'id': asset.id,
        'name': asset.name,
        'serial_no': asset.serial_no,
        'model': asset.model,
        'brand': asset.brand,
        'status': asset.status
    }
    return jsonify(asset_data)

@app.route('/assets', methods=['POST'])
def create_asset():
    data = request.get_json()
    asset = Asset(
        name=data['name'],
        serial_no=data['serial_no'],
        model=data['model'],
        brand=data['brand'],
        status=data['status']
    )
    db.session.add(asset)
    db.session.commit()
    return jsonify({'message': 'Asset created successfully'}), 201

@app.route('/assets/<int:asset_id>', methods=['PUT'])
def update_asset(asset_id):
    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({'message': 'Asset not found'}), 404
    data = request.get_json()
    asset.name = data['name']
    asset.serial_no = data['serial_no']
    asset.model = data['model']
    asset.brand = data['brand']
    asset.status = data['status']
    db.session.commit()
    return jsonify({'message': 'Asset updated successfully'})

@app.route('/assets/<int:asset_id>', methods=['DELETE'])
def delete_asset(asset_id):
    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({'message': 'Asset not found'}), 404
    db.session.delete(asset)
    db.session.commit()
    return jsonify({'message': 'Asset deleted successfully'})

@app.route('/assigned_assets', methods=['POST'])
def create_assigned_asset():
    data = request.get_json()
    assigned_asset = AssignedAsset(
        name=data['name'],
        serial_no=data['serial_no'],
        model=data['model'],
        asset_id=data['asset_id'],
        status=data['status'],
        assigned_to=data['assigned_to'],
        assigned_date=data['assigned_date']
    )
    db.session.add(assigned_asset)
    db.session.commit()
    return jsonify({'message': 'Assigned Asset created successfully'}), 201

@app.route('/assigned_assets/<int:asset_id>', methods=['PUT'])
def update_assigned_asset(asset_id):
    asset = AssignedAsset.query.get(asset_id)
    if not asset:
        return jsonify({'message': 'Assigned Asset not found'}), 404
    data = request.get_json()
    asset.name = data['name']
    asset.serial_no = data['serial_no']
    asset.model = data['model']
    asset.asset_id = data['asset_id']
    asset.status = data['status']
    asset.assigned_to = data['assigned_to']
    asset.assigned_date = data['assigned_date']
    db.session.commit()
    return jsonify({'message': 'Assigned Asset updated successfully'})

@app.route('/assigned_assets/<int:asset_id>', methods=['DELETE'])
def delete_assigned_asset(asset_id):
    asset = AssignedAsset.query.get(asset_id)
    if not asset:
        return jsonify({'message': 'Assigned Asset not found'}), 404
    db.session.delete(asset)
    db.session.commit()
    return jsonify({'message': 'Assigned Asset deleted successfully'})


@app.route('/employees', methods=['GET'])
def get_all_employees():
    employees = Employee.query.all()
    employee_list = []
    for employee in employees:
        employee_data = {
            'id': employee.id,
            'public_id': employee.public_id,
            'name': employee.name,
            'department': employee.department,
            'admin': employee.admin
        }
        employee_list.append(employee_data)
    return jsonify(employee_list)

@app.route('/employees/<public_id>', methods=['GET'])
def get_employee(public_id):
    employee = Employee.query.filter_by(public_id=public_id).first()
    if not employee:
        return jsonify({'message': 'Employee not found'}), 404
    employee_data = {
        'id': employee.id,
        'public_id': employee.public_id,
        'name': employee.name,
        'department': employee.department,
        'admin': employee.admin
    }
    return jsonify(employee_data)

@app.route('/employees', methods=['POST'])
def create_employee():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_employee = Employee(
        public_id=str(uuid.uuid4()),
        name=data['name'],
        department=data['department'],
        admin=data['admin'],
        password=hashed_password
    )
    db.session.add(new_employee)
    db.session.commit()
    return jsonify({'message': 'Employee created successfully'}), 201

@app.route('/employees/<public_id>', methods=['PUT'])
def update_employee(public_id):
    employee = Employee.query.filter_by(public_id=public_id).first()
    if not employee:
        return jsonify({'message': 'Employee not found'}), 404
    data = request.get_json()
    employee.name = data['name']
    employee.department = data['department']
    employee.admin = data['admin']
    db.session.commit()
    return jsonify({'message': 'Employee updated successfully'})

@app.route('/employees/<public_id>', methods=['DELETE'])
def delete_employee(public_id):
    employee = Employee.query.filter_by(public_id=public_id).first()
    if not employee:
        return jsonify({'message': 'Employee not found'}), 404
    db.session.delete(employee)
    db.session.commit()
    return jsonify({'message': 'Employee deleted successfully'})

@app.route('/requested_assets', methods=['GET'])
def get_all_requested_assets():
    requested_assets = RequestedAsset.query.all()
    requested_assets_list = []
    for asset in requested_assets:
        asset_data = {
            'id': asset.id,
            'asset_id': asset.asset_id,
            'employee_id': asset.employee_id,
            'status': asset.status
        }
        requested_assets_list.append(asset_data)
    return jsonify(requested_assets_list)

@app.route('/requested_assets/<int:requested_asset_id>', methods=['GET'])
def get_requested_asset(requested_asset_id):
    requested_asset = RequestedAsset.query.get(requested_asset_id)
    if not requested_asset:
        return jsonify({'message': 'Requested Asset not found'}), 404
    asset_data = {
        'id': requested_asset.id,
        'asset_id': requested_asset.asset_id,
        'employee_id': requested_asset.employee_id,
        'status': requested_asset.status
    }
    return jsonify(asset_data)

@app.route('/requested_assets', methods=['POST'])
def create_requested_asset():
    data = request.get_json()
    requested_asset = RequestedAsset(
        asset_id=data['asset_id'],
        employee_id=data['employee_id'],
        status=data['status']
    )
    db.session.add(requested_asset)
    db.session.commit()
    return jsonify({'message': 'Requested Asset created successfully'}), 201

@app.route('/requested_assets/<int:requested_asset_id>', methods=['PUT'])
def update_requested_asset(requested_asset_id):
    requested_asset = RequestedAsset.query.get(requested_asset_id)
    if not requested_asset:
        return jsonify({'message': 'Requested Asset not found'}), 404
    data = request.get_json()
    requested_asset.asset_id = data['asset_id']
    requested_asset.employee_id = data['employee_id']
    requested_asset.status = data['status']
    db.session.commit()
    return jsonify({'message': 'Requested Asset updated successfully'})

@app.route('/requested_assets/<int:requested_asset_id>', methods=['DELETE'])
def delete_requested_asset(requested_asset_id):
    requested_asset = RequestedAsset.query.get(requested_asset_id)
    if not requested_asset:
        return jsonify({'message': 'Requested Asset not found'}), 404
    db.session.delete(requested_asset)
    db.session.commit()
    return jsonify({'message': 'Requested Asset deleted successfully'})


if __name__ == '__main__':
    init_db()
    generate_fake_data()
    app.run(debug=True)
