1️⃣ Project Title
# Decentralized Blockchain Voting System


2️⃣ Project Description
This is a Decentralized Voting System built using Blockchain, Flask, and Face Recognition.
The system ensures secure, transparent, and tamper-proof voting.

Key goals:
- One person = one vote
- Votes cannot be modified
- Admin-controlled elections
- Secure voter authentication using face recognition


3️⃣ Features
## ✨ Features

- Blockchain-based voting (Ethereum / Ganache)
- Secure admin login with face recognition
- Voter registration with face data
- One vote per voter (enforced on blockchain)
- Election creation & deletion
- Automatic reset of voter voting status on election deletion
- Real-time results from blockchain
- Dockerized setup (easy to run)


4️⃣ Tech Stack
## 🛠️ Tech Stack

### Backend
- Python (Flask)
- SQLAlchemy
- Face Recognition (OpenCV, face_recognition)

### Blockchain
- Solidity
- Ganache
- Web3.py

### Database
- MySQL

### Frontend
- HTML
- CSS
- JavaScript

### DevOps
- Docker
- Docker Compose


5️⃣ Project Architecture (High Level)
## 🧩 Project Architecture

- Frontend communicates with Flask backend
- Backend handles:
  - Admin logic
  - Voter management
  - Face verification
  - Blockchain interaction
- Blockchain smart contract stores:
  - Candidates
  - Votes
  - Vote counts
- Database stores:
  - Voters
  - Admin
  - Elections


6️⃣ Folder Structure
## 📁 Folder Structure

decentralized-voting/
│
├── backend/
│   ├── app.py
│   ├── routes/
│   │   ├── admin_routes.py
│   │   └── voter_routes.py
│   ├── services/
│   │   ├── user_service.py
│   │   ├── election_service.py
│   │   └── blockchain_service.py
│   ├── models/
│   └── utils/
│
├── frontend/
│   ├── public/
│   │   ├── admin.html
│   │   ├── index.html
│   │   ├── voter_auth.html
│   │   └── assets/
│
├── docker-compose.yml
├── Dockerfile.backend
└── README.md

7️⃣ Smart Contract Overview
## 🔐 Smart Contract Overview

The smart contract is written in Solidity.

Responsibilities:
- Store candidates
- Store vote count
- Prevent double voting
- Ensure immutable voting data

Important:
- Voter voted/not-voted state is handled in database
- Blockchain code is NOT modified for election reset

8️⃣ How Election Reset Works (IMPORTANT PART)
## 🔄 Election Reset Logic

When an election is deleted:
- Election data is removed from database
- Candidates are deleted
- All voters' `has_voted` status is reset to FALSE

This allows:
- Same voters to vote again in a new election
- No need to re-register voters

9️⃣ How to Run the Project
## ▶️ How to Run the Project

### Prerequisites
- Docker
- Docker Compose
### Steps
1. Clone the repository
```bash

git clone <repository-url>
cd decentralized-voting
2.
Build and start containers
docker compose up --build

3.
Open browser
http://127.0.0.1:5000

4.
To stop the project
docker compose down