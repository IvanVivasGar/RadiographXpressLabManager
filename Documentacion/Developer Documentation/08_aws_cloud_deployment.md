# AWS Cloud Deployment Guide

This guide details the process of migrating the containerized RadiographXpress application from a local or on-premises environment to a fully managed, production-ready infrastructure on Amazon Web Services (AWS).

By utilizing managed AWS services, the application achieves high availability, automated backups, and scalable real-time WebSocket performance.

---

## 1. Architecture Overview (AWS)

While the `docker-compose.yml` file handles orchestration locally, translating this to AWS involves separating the stateless web containers from the stateful database and caching layers.

**AWS Service Mapping:**
- **Web & Nginx Containers** $\rightarrow$ **Amazon EC2** (or Amazon ECS / Fargate)
- **PostgreSQL Database** $\rightarrow$ **Amazon RDS**
- **Redis (Channel Layer)** $\rightarrow$ **Amazon ElastiCache**
- **Media Files (Signatures, Profiles)** $\rightarrow$ **Amazon S3**
- **Email Delivery** $\rightarrow$ **Amazon SES**

---

## 2. Amazon RDS (Relational Database Service)
Instead of running the `postgres` Docker container in production, use Amazon RDS for automated backups, updates, and durability.

### Setup Steps:
1. Navigate to the **RDS Console** and click **Create database**.
2. Select **PostgreSQL** (version 16 recommended).
3. Choose the **Free Tier** or **Production** template depending on your budget.
4. **Settings:**
   - DB instance identifier: `radiographxpress-db`
   - Master username: `radiograph_admin` (Store this in `.env` as `POSTGRES_USER`)
   - Master password: Auto-generate or set securely (`POSTGRES_PASSWORD`).
5. **Connectivity:**
   - Place the database in the same VPC as your EC2 instance.
   - **Public Access:** Set to `No` (for security).
   - Create a new VPC Security Group.
6. Once created, copy the **Endpoint** and update your EC2 `.env` file:
   ```env
   DATABASE_URL=postgres://radiograph_admin:<password>@<rds-endpoint>:5432/radiograph_db
   ```

---

## 3. Amazon ElastiCache (Redis)
Django Channels requires a reliable Redis layer for broadcasting WebSocket messages to patients and doctors.

### Setup Steps:
1. Navigate to the **ElastiCache Console** and click **Create cluster**.
2. Select **Redis OSS**.
3. Choose **Cluster Mode Disabled** (Django Channels only requires a single node/replica setup).
4. Select a small node type (e.g., `cache.t3.micro`).
5. Place it in the same VPC and Subnet Group as your EC2/RDS.
6. Once created, copy the **Primary Endpoint** and update your `.env`:
   ```env
   REDIS_URL=redis://<elasticache-endpoint>:6379/0
   ```

---

## 4. Amazon S3 (Simple Storage Service)
The application must store user-uploaded profile pictures and doctor PNG signatures in S3, as EC2/Docker container filesystems are ephemeral.

### Setup Steps:
1. Navigate to the **S3 Console** and click **Create bucket**.
2. Bucket name: `radiographxpress-media-prod` (must be globally unique).
3. **Block Public Access settings:** Clear the "Block all public access" checkbox (or use CloudFront).
4. Enable **Bucket Versioning** to prevent accidental deletion of doctor signatures.
5. Apply the following Bucket Policy to allow public reads for media:
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Sid": "PublicReadGetObject",
               "Effect": "Allow",
               "Principal": "*",
               "Action": "s3:GetObject",
               "Resource": "arn:aws:s3:::radiographxpress-media-prod/*"
           }
       ]
   }
   ```
6. **IAM User:** Create a specific IAM User in the IAM Console with purely S3 write permissions, generate Access Keys, and add them to your `.env`:
   ```env
   USE_S3=True
   AWS_ACCESS_KEY_ID=AKIA...
   AWS_SECRET_ACCESS_KEY=...
   AWS_STORAGE_BUCKET_NAME=radiographxpress-media-prod
   AWS_S3_REGION_NAME=us-east-1
   ```

---

## 5. Amazon SES (Simple Email Service)
RadiographXpress heavily relies on email for Account Verification and sending encrypted PDF reports. SES provides high-deliverability transactional emails.

### Setup Steps:
1. Navigate to the **SES Console**.
2. Go to **Verified Identities** $\rightarrow$ **Create Identity**.
3. Choose **Domain** (e.g., `radiographxpress.com`) and add the generated CNAME records to your DNS provider (Route53 or GoDaddy).
4. Request to be removed from the **SES Sandbox** by opening an AWS Support ticket, explaining that you send transactional medical reports.
5. Create SMTP Credentials in the SES console and update your `.env`:
   ```env
   EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=AKIA...
   EMAIL_HOST_PASSWORD=...
   DEFAULT_FROM_EMAIL=no-reply@radiographxpress.com
   ```

---

## 6. Hosting the Docker Containers (Amazon EC2)
The simplest production approach is to run your `docker-compose.yml` on a single Amazon EC2 instance.

### Deployment Workflow:
1. Launch an **Ubuntu 24.04 EC2 Instance** (t3.small or t3.medium).
2. Attach an **Elastic IP** so your domain's DNS always points to the same server.
3. Configure the EC2 Security Group:
   - Allow Port `80` (HTTP)
   - Allow Port `443` (HTTPS)
   - Allow Port `22` (SSH) from your IP only.
4. SSH into the instance and install Docker:
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose
   ```
5. Clone your repository.
6. **Modify `docker-compose.yml`**: Remove the `postgres` and `redis` blocks entirely, as these are now handled by RDS and ElastiCache.
7. Create your `.env` file on the server containing all the AWS endpoints and keys.
8. Bring up the application:
   ```bash
   sudo docker-compose up --build -d
   ```

### (Optional) Advanced: ECS / Fargate
For absolute high-availability, you can push your built Docker images to **Amazon ECR** (Elastic Container Registry) and deploy them via **Amazon ECS with Fargate**. This removes the need to manage the EC2 operating system entirely, placing Nginx, Daphne, and the `sync_pacs` cron job into autoscaling serverless task definitions.
