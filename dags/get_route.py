
def get_route_keys():
    import requests
    from airflow.utils.log.logging_mixin import LoggingMixin
    logger = LoggingMixin().log

    try:
        response = requests.post('https://aggiespirit.ts.tamu.edu/RouteMap/GetBaseData/')
        response.raise_for_status()
        routes_data = response.json()
        logger.info("Successfully fetched route data.")
    except requests.exceptions.HTTPError as err:
        logger.error(f"HTTP error occurred: {err}")
        routes_data = {}
        raise err  # Re-raise the exception to allow Airflow to handle it
    except Exception as err:
        logger.error(f"An error occurred: {err}")
        routes_data = {}
        raise err  # Re-raise the exception

    route_keys = []
    route_dict = {}

    for route in routes_data.get('routes', []):
        route_key = route.get('key')
        short_name = route.get('shortName')
        name = route.get('name')
        if route_key:
            route_keys.append(route_key)
            route_dict[route_key] = (short_name, name)
            logger.debug(f"Added route key: {route_key}, Short Name: {short_name}, Name: {name}")

    payload = [('routeKeys[]', key) for key in route_keys]
    logger.info(f"Prepared payload with {len(route_keys)} route keys.")

    return payload, route_dict


