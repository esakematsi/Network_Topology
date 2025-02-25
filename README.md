This project is developed for Communications Lab II course @ University of Patras. 

## 📌 Project Description
This project creates a networked environment where multiple clients, running inside **Docker containers**, communicate bidirectionally. Using socket programming and multithreading, the system ensures efficient message exchange, including acknowledgment messages for reliable communication.

##  Features
- **Bidirectional communication** between clients.
- **Acknowledgment messages** for reliable data transmission.
- **Docker containers** to simulate networked clients.
- **Socket programming** for client-to-client communication.
- **Multithreading** for handling multiple connections.


## Technologies Used
- **Docker**  for containerized clients
- **Python**  for socket programming & threading
- **Sockets** for network communication
- **Multithreading** for concurrent connections


## Installation

Before running the project, ensure that **Docker** and **Docker Compose** are installed on your system.

1) Clone the repository or manually download the files and place them in the same folder.

2) Open a Terminal in the Project Directory: open your terminal and navigate to the directory where the docker-compose.yml file is located.

3) Build and Start the Containers:  run the following command **docker-compose up --build**.


