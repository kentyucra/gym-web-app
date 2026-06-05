# Site Fitness Frontend

Next.js frontend for the Site Fitness gym management system.

## Getting Started

Run the development server locally:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Docker Development Frontend

From the project root, build and start only the frontend:

```bash
docker-compose up -d --build frontend
```

The frontend runs on:

```txt
http://localhost:3000
```

The compose setup bind-mounts `./frontend` into the container at `/app`, so code
changes on your machine are visible inside the running container. Next.js dev
mode will reload the page for normal frontend file changes.

Useful commands:

```bash
docker-compose logs -f frontend
docker-compose restart frontend
docker-compose stop frontend
```

The frontend expects the Flask API at:

```txt
NEXT_PUBLIC_API_URL=http://127.0.0.1:5001/api
```

That value is set in `docker-compose.yml` for the container and in
`.env.local` for local development.

## Full Local Stack

When you want the app and API together, start the backend first, then frontend:

```bash
docker-compose up -d --build backend
docker-compose up -d --build frontend
```
