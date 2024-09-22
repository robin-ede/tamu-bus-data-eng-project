
def upload_to_cosmos(extracted_stop_data, extracted_vehicle_data):
    import pandas as pd
    from azure.cosmos import CosmosClient, exceptions
    import hashlib
    from airflow.hooks.base import BaseHook
    from airflow.utils.log.logging_mixin import LoggingMixin
    
    # Initialize the logger
    logger = LoggingMixin().log

    # Initialize Cosmos client using Airflow Connection
    try:
        # Retrieve the connection details from Airflow Connections
        conn = BaseHook.get_connection('cosmos_db')
        COSMOS_DB_URL = conn.host
        COSMOS_DB_KEY = conn.password
        
        logger.info(f"COSMOS_DB_URL: {COSMOS_DB_URL}")
        logger.info(f"COSMOS_DB_KEY is set: {'Yes' if COSMOS_DB_KEY else 'No'}")
        logger.info("Successfully retrieved Cosmos DB connection details.")
    except Exception as e:
        logger.error(f"Error retrieving Cosmos DB connection: {e}")
        raise e

    DATABASE_NAME = 'bus_data'
    CONTAINER_NAME_VEHICLES = 'vehicle_data'
    CONTAINER_NAME_STOPS = 'stop_data'

    # Initialize Cosmos client
    try:
        client = CosmosClient(url=COSMOS_DB_URL, credential=COSMOS_DB_KEY)
        database = client.get_database_client(DATABASE_NAME)
        logger.info(f"Connected to Cosmos DB database: {DATABASE_NAME}")
    except Exception as e:
        logger.error(f"Error connecting to Cosmos DB: {e}")
        raise e

    # Get containers for vehicles and stops
    try:
        container_vehicles = database.get_container_client(CONTAINER_NAME_VEHICLES)
        container_stops = database.get_container_client(CONTAINER_NAME_STOPS)
        logger.info(f"Accessed containers: {CONTAINER_NAME_VEHICLES}, {CONTAINER_NAME_STOPS}")
    except Exception as e:
        logger.error(f"Error accessing containers: {e}")
        raise e

    # Upload vehicle data
    vehicle_count = 0
    for vehicle in extracted_vehicle_data:
        # Create a unique ID using a hash function
        id_string = f"{vehicle['Vehicle Name']}_{vehicle['Last GPS Date']}"
        unique_id = hashlib.md5(id_string.encode('utf-8')).hexdigest()
        vehicle['id'] = unique_id

        try:
            # Upload the data to Cosmos DB
            container_vehicles.upsert_item(vehicle)
            vehicle_count += 1
            logger.debug(f"Upserted vehicle data with ID: {unique_id}")
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Error upserting vehicle data with ID {unique_id}: {e}")
            # Handle the error as needed (e.g., log, continue, retry)

    logger.info(f"Uploaded {vehicle_count} vehicle records to Cosmos DB.")

    # Upload stop data without duplicates
    stop_count = 0
    for stop in extracted_stop_data:
        # Create a unique ID using a hash function
        id_string = f"{stop['Route Key']}_{stop['Pattern Key']}_{stop['Latitude']}_{stop['Longitude']}"
        unique_id = hashlib.md5(id_string.encode('utf-8')).hexdigest()
        stop['id'] = unique_id

        try:
            # Upsert the item to prevent duplicates
            container_stops.upsert_item(stop)
            stop_count += 1
            logger.debug(f"Upserted stop data with ID: {unique_id}")
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Error upserting stop data with ID {unique_id}: {e}")
            # Handle the error as needed

    logger.info(f"Uploaded {stop_count} stop records to Cosmos DB.")
    logger.info("Data upload to Cosmos DB completed successfully.")
