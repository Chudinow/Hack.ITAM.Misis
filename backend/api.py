@app.route('/api/organizer/hackathons', methods=['POST'])
@jwt_required()
def create_hackathon_minimal():
    organizer_id = get_jwt_identity()
    data = request.get_json()
    required_fields = ['name', 'start_date', 'end_date']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'error': f'Missing required field: {field}'
            }), 400
    start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
    end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
    if end_date <= start_date:
        return jsonify({
            'error': 'End date must be after start date'
        }), 400
    if start_date < datetime.utcnow():
        return jsonify({
            'error': 'Start date cannot be in the past'
        }), 400
    hackathon = Hackathon(
        name=data['name'],
        description=data.get('description', ''),
        start_date=start_date,
        end_date=end_date,
        organizer_id=organizer_id,
        status='draft',
        location_type=data.get('location_type', 'online'),
        location_address=data.get('location_address'),
        max_teams=data.get('max_teams', 50)
    )
    db.session.add(hackathon)
    db.session.commit()
    return jsonify({
        'success': True,
        'hackathon_id': hackathon.id,
        'edit_url': f'/api/organizer/hackathons/{hackathon.id}'
    }), 201
