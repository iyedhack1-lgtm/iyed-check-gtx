from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Supported regions based on your preferences (IN, BD, PK, NA, SG٫ ME)
# You can extend this dictionary with region-specific configurations if needed
REGION_CONFIG = {
    'IN': {'region_code': 'IN', 'language': 'en', 'source': 'mb'},
    'BD': {'region_code': 'BD', 'language': 'en', 'source': 'mb'},
    'PK': {'region_code': 'PK', 'language': 'en', 'source': 'mb'},
    'NA': {'region_code': 'NA', 'language': 'en', 'source': 'mb'},
    'SG': {'region_code': 'SG', 'language': 'en', 'source': 'mb'},
    'ME': {'region_code': 'ME', 'language': 'ar', 'source': 'mb'},
}

@app.route('/check', methods=['GET'])
def check_player():
    target_id = request.args.get('uid')
    region = request.args.get('region', 'IN').upper()  # Default to IN if not provided
    
    if not target_id:
        return jsonify({"success": False, "message": "Missing 'uid' parameter"}), 400
    
    if region not in REGION_CONFIG:
        return jsonify({"success": False, "message": f"Unsupported region: {region}. Supported: {', '.join(REGION_CONFIG.keys())}"}), 400
    
    # Get region-specific config
    config = REGION_CONFIG[region]
    
    # Base cookies (updated to be more generic; you may need to refresh session_key and datadome periodically)
    cookies = {
        '_ga': 'GA1.1.2123120599.1674510784',  # These may need updating
        '_fbp': 'fb.1.1674510785537.363500115',
        '_ga_7JZFJ14B0B': 'GS1.1.1674510784.1.1.1674510789.0.0.0',
        'source': config['source'],
        'region': config['region_code'],
        'language': config['language'],
        '_ga_TVZ1LG7BEB': 'GS1.1.1674930050.3.1.1674930171.0.0.0',
        'datadome': '6h5F5cx_GpbuNtAkftMpDjsbLcL3op_5W5Z-npxeT_qcEe_7pvil2EuJ6l~JlYDxEALeyvKTz3~LyC1opQgdP~7~UDJ0jYcP5p20IQlT3aBEIKDYLH~cqdfXnnR6FAL0',  # Refresh if expired
        'session_key': 'efwfzwesi9ui8drux4pmqix4cosane0y',  # Refresh if expired
    }

    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Origin': 'https://shop2game.com',
        'Referer': 'https://shop2game.com/app/100067/idlogin',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Redmi Note 8)',
        'accept': 'application/json',
        'content-type': 'application/json',
        'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'x-datadome-clientid': cookies['datadome'],  # Use the datadome from cookies
    }

    json_data = {
        'app_id': 100067,
        'login_id': target_id,
        'app_server_id': 0,
    }

    try:
        res = requests.post('https://shop2game.com/api/auth/player_id_login', cookies=cookies, headers=headers, json=json_data)
        res.raise_for_status()  # Raise error for non-200 status
        
        player_data = res.json()
        if not player_data.get('nickname'):
            return jsonify({"success": False, "message": "Error: ID NOT FOUND"}), 404

        nickname = player_data.get('nickname', 'N/A')
        retrieved_region = player_data.get('region', 'N/A')

        # Ban check
        ban_url = f'https://ff.garena.com/api/antihack/check_banned?lang=en&uid={target_id}&region={region}'
        ban_response = requests.get(ban_url, headers=headers)
        ban_response.raise_for_status()
        
        ban_data = ban_response.json()
        is_banned = False
        ban_period = 0
        if ban_data.get("status") == "success" and "data" in ban_data:
            is_banned = bool(ban_data["data"].get("is_banned", 0))
            ban_period = int(ban_data["data"].get("period", 0))

        return jsonify({
            "success": True,
            "nickname": nickname,
            "region": retrieved_region,
            "is_banned": is_banned,
            "ban_period": ban_period,
            "message": "Player found and data retrieved successfully."
        })
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": f"Request failed: {str(e)}"}), 500
    except ValueError as e:
        return jsonify({"success": False, "message": f"Invalid response: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
