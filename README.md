# City Weather Application

## 📚 Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Repository Structure](#repository-structure)
- [Usage](#usage)

## Overview
City Weather is a simple web application built using Python Flask to fetch and display real-time weather data. It integrates Prometheus for metrics monitoring and Grafana for visualizing the application performance.

## Requirements

### Environment
- **OS**: Developed and tested on **Windows 11**
- **Python Version**: Requires **Python 3.10**
- **Docker**: Pre-installed [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) on Windows

### Setup API Key
To fetch weather data, you will need a free API key from [OpenWeather](https://openweathermap.org/).
- Sign up at [OpenWeatherMap](https://openweathermap.org/api)
- Get your API key
- In the project root directory `city-weather`, create a file named `.env` with this content:
```bash
    OPENWEATHER_API_KEY=your_actual_key_here
```

### Clone the Repository

```bash
    git clone https://github.com/Muhamamd-Rehman/city-weather.git
```

## Repository Structure

```bash
city-weather/ (project-root)
├── prometheus/
│   └── prometheus.yml
└── grafana/
    ├── dashboards/
    │   └── city_weather_dashboard.json
    └── provisioning/
        ├── dashboards/
        │   └── dashboards.yml
        └── datasources/
            └── datasource.yml                        
├── templates/
│   ├── index.html  # html and CSS index file   
├── README.md   
├── app.py 
├──weather_api.py 
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .gitignore  
```

## Usage
1. Open Docker Desktop and wait until you see `Engine running` sign on the bottom left corner.
2. Open your Windows terminal inside the project root directory `city-weather` and start the docker containers:
    ```bash
    docker-compose up --build
    ```

- Start the application on: http://localhost:5000
- Start Prometheus on: http://localhost:9090
- Start Grafana on: http://localhost:3030

📊 Default Grafana login:
- User: `admin`
- Password: `admin`

You will find prebuilt dashboard in Grafana under `Dashboards` → `City Weather Dashboard`

Use `docker-compose stop` to stop the running containers. This command keeps the built docker images, containers, 
volumes etc. and does not remove them. To rerun the city weather application, use `docker-compose start`.