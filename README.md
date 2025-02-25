This project is developed for Communications Lab II course @ University of Patras. 

##  Project Description
This project creates a networked environment where multiple clients, running inside **Docker containers**, communicate bidirectionally. Using socket programming and multithreading, the system ensures efficient message exchange, including acknowledgment messages for reliable communication.



## Technologies Used
- **Docker**  for containerized clients (one container per network client)
- **Python**  for Socket programming, Threading & Acknowledgment messages
- **Sockets** for network and client-to-client communication
- **Multithreading** for handling concurrent connections


## Installation

Before running the project, ensure that **Docker** and **Docker Compose** are installed on your system.

1) Clone the repository or manually download the files and place them in the same folder.

2) Open a Terminal in the Project Directory: open your terminal and navigate to the directory where the docker-compose.yml file is located.

3) Build and Start the Containers:  run the following command **docker-compose up --build**.
   
This command will:

-Build the required Docker images.

-Start all containers and set up the network for communication.



## 
The project implements the Network Topology found in the .puml file: 

-A **Ring** connecting 4 clients, with **Client 5 accessible only through Client 4**.

##
Project functionality can be confirmed by watching the **MP4 video** found in the repository. 


