Docker Desktop ON →  docker compose up
Backend me code change kiya ho → docker compose up --build
Docker hang ho jaye → docker compose down
docker compose up
Jab bhi project run karna hai -> docker compose up

✅ 1️⃣ docker compose down -v

Poora project band karta hai

Saare running containers stop

Saare volumes delete (db data reset)
= Clean fresh start

✅ 2️⃣ docker compose build --no-cache

Docker ko fresh build karne bolta hai

Purani images ignore

Saare Dockerfile commands dobara run
= New clean backend + ganache images banengi

✅ 3️⃣ docker compose up


Project ko run karta hai

Backend

MySQL

Ganache
= Teeno containers start ho kar connect ho jate hain

we have to change contract address each time when we want ot run the project

Ganache container start karo -> docker start voting-ganache

private key and account addresss -> docker logs voting-ganache
