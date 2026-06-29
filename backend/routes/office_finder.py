from flask import Blueprint, request, jsonify
from database import OfficeLocation

office_finder_bp = Blueprint('office_finder', __name__)

@office_finder_bp.route('/search', methods=['GET'])
def get_offices():
    office_type = request.args.get('type', '')
    district = request.args.get('district', '')
    state = request.args.get('state', '')
    
    stmt = OfficeLocation.query
    if office_type:
        stmt = stmt.filter(OfficeLocation.office_type == office_type)
    if district:
        stmt = stmt.filter(OfficeLocation.district == district)
    if state:
        stmt = stmt.filter(OfficeLocation.state == state)
        
    offices = stmt.all()
    results = []
    for o in offices:
        results.append({
            "id": o.id,
            "name": o.name,
            "office_type": o.office_type,
            "district": o.district,
            "state": o.state,
            "latitude": o.latitude,
            "longitude": o.longitude
        })
    return jsonify(results), 200

@office_finder_bp.route('/types', methods=['GET'])
def get_office_types():
    types = OfficeLocation.query.with_entities(OfficeLocation.office_type).distinct().all()
    output = [t[0] for t in types]
    return jsonify(output), 200
