def fetch_and_process_bus_data(route_data, route_dict):
    import requests
    # import pandas as pd
    from airflow.utils.log.logging_mixin import LoggingMixin
    logger = LoggingMixin().log

    headers = {
        'Accept': 'application/json',
    }

    # Get data and route dictionary
    payload = route_data

    # Make POST request
    try:
        response = requests.post(
            'https://aggiespirit.ts.tamu.edu/RouteMap/GetPatternPaths/',
            headers=headers,
            data=payload
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred during the POST request: {e}")
        raise e

    # Parse JSON response
    try:
        response_data = response.json()
    except ValueError as e:
        logger.error(f"Error parsing JSON response: {e}")
        raise e

    # Lists to hold extracted data
    extracted_stop_data = []
    extracted_vehicle_data = []

    # Process the data
    for route in response_data:
        route_key = route.get('routeKey')
        route_info = route_dict.get(route_key, ['Unknown', 'Unknown'])
        route_symbol, route_name = route_info

        # Extract pattern paths
        for pattern in route.get('patternPaths', []):
            pattern_key = pattern.get('patternKey')
            direction_key = pattern.get('directionKey')

            for point in pattern.get('patternPoints', []):
                stop = point.get('stop') or {}
                stop_name = stop.get('name')
                stop_code = stop.get('stopCode')

                latitude = point.get('latitude')
                longitude = point.get('longitude')

                extracted_stop_data.append({
                    'Route Key': route_key,
                    'Route Symbol': route_symbol,
                    'Route Name': route_name,
                    'Pattern Key': pattern_key,
                    'Direction Key': direction_key,
                    'Stop Name': stop_name,
                    'Stop Code': stop_code,
                    'Latitude': latitude,
                    'Longitude': longitude
                })

        # Extract vehicle data
        for direction in route.get('vehiclesByDirections', []):
            direction_key = direction.get('directionKey')
            for vehicle in direction.get('vehicles', []):
                vehicle_name = vehicle.get('name')
                passenger_capacity = vehicle.get('passengerCapacity')
                passengers_onboard = vehicle.get('passengersOnboard')
                amenities = ', '.join(
                    [amenity.get('name') for amenity in vehicle.get('amenities', [])]
                )
                location = vehicle.get('location', {})
                last_gps_date = location.get('lastGpsDate')
                latitude = location.get('latitude')
                longitude = location.get('longitude')
                speed = location.get('speed')
                heading = location.get('heading')
                is_extra_trip = vehicle.get('isExtraTrip')
                extracted_vehicle_data.append({
                    'Route Key': route_key,
                    'Route Symbol': route_symbol,
                    'Route Name': route_name,
                    'Direction Key': direction_key,
                    'Vehicle Name': vehicle_name,
                    'Passenger Capacity': passenger_capacity,
                    'Passengers Onboard': passengers_onboard,
                    'Amenities': amenities,
                    'Last GPS Date': last_gps_date,
                    'Latitude': latitude,
                    'Longitude': longitude,
                    'Speed': speed,
                    'Heading': heading,
                    'Is Extra Trip': is_extra_trip
                })

    # df_new_stops = pd.DataFrame(extracted_stop_data)
    # df_new_vehicles = pd.DataFrame(extracted_vehicle_data)

    # Return the extracted data
    return extracted_stop_data, extracted_vehicle_data
