# from flask import request, jsonify
# from api import app, db, Asset, AssignedAsset

# @app.route('/assets', methods=['GET'])
# def get_all_assets():
#     assets = Asset.query.all()
#     asset_list = []
#     for asset in assets:
#         asset_data = {
#             'id': asset.id,
#             'name': asset.name,
#             'serial_no': asset.serial_no,
#             'model': asset.model,
#             'brand': asset.brand,
#             'status': asset.status
#         }
#         asset_list.append(asset_data)
#     return jsonify(asset_list)

# @app.route('/assets/<int:asset_id>', methods=['GET'])
# def get_asset(asset_id):
#     asset = Asset.query.get(asset_id)
#     if not asset:
#         return jsonify({'message': 'Asset not found'}), 404
#     asset_data = {
#         'id': asset.id,
#         'name': asset.name,
#         'serial_no': asset.serial_no,
#         'model': asset.model,
#         'brand': asset.brand,
#         'status': asset.status
#     }
#     return jsonify(asset_data)

# @app.route('/assets', methods=['POST'])
# def create_asset():
#     data = request.get_json()
#     asset = Asset(
#         name=data['name'],
#         serial_no=data['serial_no'],
#         model=data['model'],
#         brand=data['brand'],
#         status=data['status']
#     )
#     db.session.add(asset)
#     db.session.commit()
#     return jsonify({'message': 'Asset created successfully'}), 201

# @app.route('/assets/<int:asset_id>', methods=['PUT'])
# def update_asset(asset_id):
#     asset = Asset.query.get(asset_id)
#     if not asset:
#         return jsonify({'message': 'Asset not found'}), 404
#     data = request.get_json()
#     asset.name = data['name']
#     asset.serial_no = data['serial_no']
#     asset.model = data['model']
#     asset.brand = data['brand']
#     asset.status = data['status']
#     db.session.commit()
#     return jsonify({'message': 'Asset updated successfully'})

# @app.route('/assets/<int:asset_id>', methods=['DELETE'])
# def delete_asset(asset_id):
#     asset = Asset.query.get(asset_id)
#     if not asset:
#         return jsonify({'message': 'Asset not found'}), 404
#     db.session.delete(asset)
#     db.session.commit()
#     return jsonify({'message': 'Asset deleted successfully'})

# @app.route('/assigned_assets', methods=['POST'])
# def create_assigned_asset():
#     data = request.get_json()
#     assigned_asset = AssignedAsset(
#         name=data['name'],
#         serial_no=data['serial_no'],
#         model=data['model'],
#         asset_id=data['asset_id'],
#         status=data['status'],
#         assigned_to=data['assigned_to'],
#         assigned_date=data['assigned_date']
#     )
#     db.session.add(assigned_asset)
#     db.session.commit()
#     return jsonify({'message': 'Assigned Asset created successfully'}), 201

# @app.route('/assigned_assets/<int:asset_id>', methods=['PUT'])
# def update_assigned_asset(asset_id):
#     asset = AssignedAsset.query.get(asset_id)
#     if not asset:
#         return jsonify({'message': 'Assigned Asset not found'}), 404
#     data = request.get_json()
#     asset.name = data['name']
#     asset.serial_no = data['serial_no']
#     asset.model = data['model']
#     asset.asset_id = data['asset_id']
#     asset.status = data['status']
#     asset.assigned_to = data['assigned_to']
#     asset.assigned_date = data['assigned_date']
#     db.session.commit()
#     return jsonify({'message': 'Assigned Asset updated successfully'})

# @app.route('/assigned_assets/<int:asset_id>', methods=['DELETE'])
# def delete_assigned_asset(asset_id):
#     asset = AssignedAsset.query.get(asset_id)
#     if not asset:
#         return jsonify({'message': 'Assigned Asset not found'}), 404
#     db.session.delete(asset)
#     db.session.commit()
#     return jsonify({'message': 'Assigned Asset deleted successfully'})
