[Python Web Application with MariaDB.pdf](https://github.com/user-attachments/files/24674208/Python.Web.Application.with.MariaDB.pdf)# Python Web Application with MariaDB and Load Balancer

A scalable, high-availability Python Flask web application deployed on AWS with load balancing and dedicated database architecture.

## Architecture Overview

This project demonstrates a production-grade deployment of a Flask-based web application on AWS using a three-tier architecture:

- **Application Tier**: Two EC2 instances running Python Flask applications
- **Database Tier**: Dedicated EC2 instance running MariaDB
- **Load Balancing**: Application Load Balancer (ALB) distributing traffic across application servers

The architecture ensures scalability, high availability, and separation of concerns through proper segmentation of application and database layers.

## Features

- Load-balanced Flask application across multiple EC2 instances
- Dedicated MariaDB database server for data persistence
- Secure VPC communication between application and database tiers
- Health monitoring and automatic traffic distribution
- User registration system with database storage

## Architecture Diagram

```
Internet
    |
    v
Application Load Balancer (ALB)
    |
    +-- HTTP:80 --> Target Group (Web-App-TG)
                         |
                         +-- webapp-server-1 (HTTP:5000)
                         |       |
                         +-- webapp-server-2 (HTTP:5000)
                                 |
                                 v
                        MariaDB-server (Port:3306)
```

## Infrastructure Components

### EC2 Instances

1. **Web Server 1** - Flask application server
2. **Web Server 2** - Flask application server (created from AMI)
3. **MariaDB Server** - Database server

### Security Groups

- **ALB-SG**: Allows HTTP traffic (port 80) from anywhere
- **App-Server-SG**: Allows SSH (port 22) from admin IP, Custom TCP (port 5000) from ALB
- **DB-Server-SG**: Allows SSH (port 22) and MySQL (port 3306) from application servers

### Load Balancing

- **Application Load Balancer**: Flask-App-ALB
- **Target Group**: Web-App-TG (HTTP:5000)
- **Health Check Path**: `/`

## Prerequisites

- AWS Account with appropriate permissions
- Basic knowledge of AWS EC2, Security Groups, and Load Balancers
- SSH key pair for EC2 access
- Git installed locally (for cloning the repository)

## Installation and Deployment

### Step 1: Database Server Setup

**Launch EC2 Instance for MariaDB:**

```bash
# Update system packages
sudo yum update -y  # For Amazon Linux 2
# OR
sudo apt update && sudo apt upgrade -y  # For Ubuntu

# Install MariaDB
sudo yum install mariadb-server -y  # For Amazon Linux 2
# OR
sudo apt install mariadb-server -y  # For Ubuntu

# Start and enable MariaDB service
sudo systemctl start mariadb
sudo systemctl enable mariadb
sudo systemctl status mariadb
```

**Configure MariaDB Database:**

```sql
-- Access MariaDB shell
sudo mariadb -u root

-- Create database
CREATE DATABASE flask_app_db;
USE flask_app_db;

-- Create table
CREATE TABLE user_deltils (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    country VARCHAR(100)
);

-- Create database user with remote access
CREATE USER 'flask_user'@'%' IDENTIFIED BY 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON flask_app_db.* TO 'flask_user'@'%';
FLUSH PRIVILEGES;

EXIT;
```

**Enable Remote Connections:**

```bash
# Edit MariaDB configuration
sudo nano /etc/my.cnf.d/mariadb-server.cnf  # Amazon Linux 2
# OR
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf  # Ubuntu

# Set bind-address
bind-address = 0.0.0.0

# Restart MariaDB
sudo systemctl restart mariadb
```

### Step 2: Web Application Server Setup

**Install Dependencies:**

```bash
# Update system
sudo yum update -y  # Amazon Linux 2
# OR
sudo apt update && sudo apt upgrade -y  # Ubuntu

# Install Python, pip, venv, and Git
sudo yum install python3 python3-pip python3-venv git -y  # Amazon Linux 2
# OR
sudo apt install python3 python3-pip python3-venv git -y  # Ubuntu

# Verify installations
python3 --version
pip3 --version
git --version
```

**Clone Application Repository:**

```bash
# Clone the repository
git clone https://github.com/your-repo/python-app-RDS-MariaDB-Project.git
cd python-app-RDS-MariaDB-Project
```

**Setup Python Virtual Environment:**

```bash
# Create virtual environment
python3 -m venv virtual_venv

# Activate virtual environment
source virtual_venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install Flask and MySQL connector
pip install flask mysql-connector-python

# Verify installations
pip list
```

**Configure Application:**

Edit `app.py` to configure database connection and server settings:

```python
# Database configuration
db_config = {
    'user': 'flask_user',
    'password': 'your_secure_password',
    'host': 'MARIADB_PRIVATE_IP',  # Replace with MariaDB server private IP
    'database': 'flask_app_db'
}

# Server configuration
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

Update SQL queries to use the correct table name:

```python
# Change table name from 'users' to 'user_deltils' in all queries
INSERT INTO user_deltils (name, email, country) VALUES (%s, %s, %s)
SELECT * FROM user_deltils
```

**Run the Application:**

```bash
# Activate virtual environment (if not already activated)
source virtual_venv/bin/activate

# Start Flask application
python app.py
```

### Step 3: Create Second Web Server from AMI

**Create AMI from Web Server 1:**

1. Navigate to EC2 Console
2. Select Web Server 1 instance
3. Actions → Image and templates → Create image
4. Name: "Web Server 1 AMI"
5. Disable "Delete on termination" for root volume
6. Create image

**Launch Web Server 2:**

1. Navigate to AMIs in EC2 Console
2. Select "Web Server 1 AMI"
3. Launch instance from AMI
4. Name: "App Server 2"
5. Use the same security group as Web Server 1
6. Launch instance

### Step 4: Configure Application Load Balancer

**Create Target Group:**

1. Navigate to EC2 → Target Groups
2. Create a target group
   - Name: `Web-App-TG`
   - Target type: Instances
   - Protocol: HTTP
   - Port: 5000
   - Health check path: `/`
3. Register targets: Add both Web Server 1 and Web Server 2
4. Create a target group

**Create Application Load Balancer:**

1. Navigate to EC2 → Load Balancers
2. Create load balancer → Application Load Balancer
   - Name: `Flask-App-ALB`
   - Scheme: Internet-facing
   - IP address type: IPv4
3. Network mapping: Select at least 2 Availability Zones
4. Security groups: Create or select ALB-SG (allow HTTP:80)
5. Listener: HTTP:80 → Forward to Web-App-TG
6. Create a load balancer

## Testing and Verification

**Test Load Balancer Distribution:**

To verify traffic distribution, modify `templates/index.html` on each server:

- Web Server 1: Change title to "User Details - 1"
- Web Server 2: Change title to "User Details - 2"

Access the application using the ALB DNS name and refresh the page to see alternating servers.

**Test Database Connectivity:**

```bash
# From application server
mariadb -u flask_user -p -h MARIADB_PRIVATE_IP flask_app_db

# Run query
SELECT * FROM user_deltils;
```

**Access the Application:**

```
http://Flask-App-ALB-XXXXXXXXXX.region.elb.amazonaws.com
```

## Security Best Practices

- Database server accepts connections only from application servers
- SSH access restricted to administrator IP addresses
- Application servers not directly accessible from the internet
- All traffic routed through ALB with security group controls
- Database credentials stored securely (consider AWS Secrets Manager)

## Project Structure

```
python-app-RDS-MariaDB-Project/
├── app.py                  # Main Flask application
├── templates/
│   ├── index.html         # User registration form
│   ├── view.html          # Display all users
│   └── thankyou.html      # Confirmation page
└── virtual_venv/          # Python virtual environment
```

## Database Schema

**Table: user_deltils**

| Column  | Type         | Constraints                  |
|---------|--------------|------------------------------|
| id      | INT          | PRIMARY KEY, AUTO_INCREMENT  |
| name    | VARCHAR(100) |                              |
| email   | VARCHAR(100) |                              |
| country | VARCHAR(100) |                              |

## Monitoring and Maintenance

- Monitor ALB metrics in CloudWatch
- Check target health status regularly
- Review application logs on EC2 instances
- Maintain database backups
- Update security patches regularly

## Troubleshooting

**Application Not Accessible:**
- Verify security groups allow traffic on the correct ports
- Check target health in the Target Group
- Ensure Flask app is running on both servers

**Database Connection Issues:**
- Verify MariaDB bind-address is set to 0.0.0.0
- Check the security group allows port 3306 from app servers
- Confirm database credentials in app.py

**Load Balancer Not Distributing Traffic:**
- Verify both targets are healthy
- Check listener rules configuration
- Ensure the health check path is valid

## Future Enhancements

- Implement RDS for managed database service
- Add HTTPS with SSL/TLS certificates
- Implement Auto Scaling for the application tier
- Add CloudWatch alarms and notifications
- Implement database connection pooling
- Add caching layer (Redis/ElastiCache)

## Technologies Used

- **Application**: Python 3.12, Flask
- **Database**: MariaDB
- **Cloud Provider**: AWS (EC2, ALB, Target Groups)
- **OS**: Amazon Linux 2 / Ubuntu
- **Version Control**: Git

## Author

KULDIP VAGHASIYA
Cloud & DevOps Enthusiast
Cloud Engineer Intern at CoreXtech

## Acknowledgments

[Python Web Application with MariaDB.pdf](https://github.com/user-attachments/files/24674209/Python.Web.Application.with.MariaDB.pdf)

