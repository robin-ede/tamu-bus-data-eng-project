# Texas A&M Bus Data Engineering Project

## Introduction

This project aims to build a scalable, automated data pipeline for collecting, processing, and visualizing real-time bus transit data for **Texas A&M University's bus system**. The project utilizes Apache Airflow for orchestration, Docker for deployment, and Azure Cosmos DB for data storage. By leveraging cloud technologies and automation, the system processes live bus data efficiently and provides interactive visualizations for analysis.

## Architecture Diagram
![Architecture Diagram](images/architecture_diagram.png)

## Project Goals

The primary objectives of this project are:
1. **Automate Data Collection**: Automate the retrieval of real-time bus data (routes, stops, and vehicle positions) for Texas A&M’s bus system using Apache Airflow.
2. **Data Processing & Storage**: Process the bus data and store it in **Azure Cosmos DB** for easy access and querying.
3. **Interactive Visualization**: Provide an easy-to-use Jupyter Notebook for visualizing bus routes and positions at any given timestamp, enabling users to analyze Texas A&M's bus operations in real time.
4. **Scalability & Modularity**: Ensure the pipeline is modular and scalable, allowing for the addition of new data sources or further processing as needed.

## Technologies Used

- **Apache Airflow**: For task orchestration and pipeline automation.
- **Docker & Docker Compose**: For containerization and simplifying deployment.
- **Azure Cosmos DB**: For scalable, cloud-based data storage.
- **Python**: For data retrieval, processing, and analysis.
- **Plotly**: For creating interactive visualizations of bus routes and positions.
- **Jupyter Notebook**: For analyzing and visualizing the data in an easy-to-use format.

## How It Works

### Data Pipeline

The data pipeline is managed by Apache Airflow, which automates the following tasks:

1. **Retrieve Route Data**: The pipeline first gathers active route data for Texas A&M’s bus system, including route keys, named and unnamed bus stops.
2. **Fetch and Process Bus Data**: It then fetches real-time bus data, including vehicle position, speed, capacity, and amenities. Each vehicle record is timestamped with the scheduled task time for easy querying.
3. **Upload to Cosmos DB**: The processed data is uploaded to Azure Cosmos DB, where it is stored for future querying and visualization.

### Cosmos DB Configuration

The data is stored in Azure Cosmos DB with the following structure:
- **Database Name**: `bus_data`
- **Container for Vehicle Data**: `vehicle_data`
- **Container for Stop Data**: `stop_data`

You can change the database or container names by modifying the **`dags/upload.py`** file:
```python
DATABASE_NAME = 'bus_data'
CONTAINER_NAME_VEHICLES = 'vehicle_data'
CONTAINER_NAME_STOPS = 'stop_data'
```

### Interactive Visualization

A Jupyter Notebook is provided to visualize the bus routes and vehicle positions on an interactive map. The notebook allows users to select a specific timestamp and query the corresponding data from Cosmos DB.

## How to Set Up

### Prerequisites

1. **Docker** and **Docker Compose** installed on your machine.
2. **Azure Cosmos DB**: You need an Azure account and a Cosmos DB instance.
3. **Python environment**: For running the Jupyter Notebook.

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/bus-data-engineering.git
   cd bus-data-engineering
   ```

2. **Build and Start the Docker Containers**
   ```bash
   docker-compose up -d
   ```

3. **Verify Airflow is Running**
   - Open your browser and go to `http://localhost:8080`.
   - Set up default credentials for the Airflow UI.

4. **Configure Airflow Connections**
   - In the Airflow UI, create a connection named `cosmos-db` using the **HTTP** type.
   - Enter your Cosmos DB URL in the **Host** field and the Primary Key in the **Password** field.

5. **Launch the Jupyter Notebook**
   ```bash
   jupyter notebook
   ```
   Open `plotting.ipynb` in the Jupyter interface and modify the connection details and database info as needed.


## **Project Structure**:

```
bus-data-engineering/
│
├── .gitignore                   # Ignore cache, virtual env, etc.
├── docker-compose.yaml          # Docker Compose setup for Airflow
├── Dockerfile                   # Dockerfile for building Airflow environment
├── README.md                    # Project overview and setup guide
├── requirements.txt             # Python dependencies for visualization
├── plotting.ipynb               # Jupyter Notebook for visualizing bus data
│
├── dags/                        # Airflow DAGs and scripts
│   ├── bus_data_pipeline.py     # Main DAG for data pipeline
│   ├── get_bus.py               # Fetches and processes bus data
│   ├── get_route.py             # Retrieves route and stop data
│   └── upload.py                # Uploads processed data to Cosmos DB
│
├── images/                      # Documentation images
│   ├── architecture_diagram.png # Architecture diagram
│   └── bus_route_visualization.png # Example visualization
│
└── sample_data/                 # Sample bus and vehicle data
    ├── bus_stops.csv            # Bus stop sample data
    └── vehicles.csv             # Vehicle sample data
```

### **Key Points**:
- **Airflow DAGs**: All pipeline-related scripts are in the `dags/` folder.
- **Visualization**: The Jupyter Notebook (`plotting.ipynb`) provides an interactive map of bus routes and positions.
- **Images**: The `images/` directory holds documentation visuals.
- **Sample Data**: `sample_data/` contains example CSV files of the data handled by the pipeline.

## Results

After setting up and running the pipeline, the following outputs are generated:

1. **Real-Time Bus Data**: The system continuously collects and stores bus route and vehicle data for Texas A&M’s bus system in Azure Cosmos DB.
2. **Interactive Map Visualizations**: Using the provided Jupyter Notebook, users can visualize bus routes and positions at specific timestamps, view bus information such as speed, heading, and capacity, and analyze the system in real time.
   
   ![Sample Bus Route Visualization](images/bus_route_visualization.png)

## Future Work

1. **Enhance Visualization**: Improve the visual representation of the bus stops and routes using custom SVG icons or integrate with third-party visualization tools like Folium.
2. **Data Analysis & Prediction**: Add advanced data analysis tasks, such as predicting bus arrival times or monitoring route efficiency.
3. **Expand Data Sources**: Incorporate additional transit systems or traffic data to enhance the scope of the project.
4. **Optimize for Scale**: Implement more efficient data storage and querying methods to handle larger datasets as the system scales.
