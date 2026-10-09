# Lab 4 – Orchestrating the app with Docker Compose

## Question 1

> What happens to everything written to `/mlflow-data` if you never mount a volume there and just `docker run` this image standalone? Try it: run the container, register nothing, stop it, remove it, start a new one from the same image — what do you see in the UI?

- Without a volume, `/mlflow-data` lives in the container's writable layer. `docker rm` deletes that layer, so the database and artifacts are gone.
- A new container starts from the clean image, so mlflow creates a fresh, empty database: only the **Default** experiment and no registered models.

## Question 2

> Why a named volume here instead of a bind mount to a folder in your repo (the way you might for local dev)? Would a bind mount work just as well?

- A named volume is managed by Docker and doesn't depend on a host path, so the compose file works on any machine. It also avoids permission issues and slow file access, and keeps the database out of the repo.
- A bind mount would also keep the data, but it would tie the setup to one machine's folder layout.

## Question 3

> In Lab 3 you had to use `host.docker.internal` or `--network host` to reach mlflow from inside the container. In this lab, `MLFLOW_TRACKING_URI` will simply be `http://mlflow:5000`. Why does that hostname resolve now when it didn't before?

- In Lab 3, the inference container ran alone on Docker's default bridge network, and mlflow ran on the host, not in a container.
- Compose creates a private network that all the services join, and its embedded DNS resolves each **service name** to that container's IP. So `mlflow` resolves to the mlflow container.

## Question 4

> Why does the frontend read `INFERENCE_URL` from an environment variable instead of hardcoding `http://inference:8000`? Think about what happens if you ever `docker run` this frontend image on its own, outside Compose.

- `http://inference:8000` only works inside the Compose network, where the name `inference` resolves. If the frontend is run on its own with `docker run`, that name doesn't exist and every request fails.
- An environment variable lets the same image point at any address without rebuilding. Compose simply sets it to `http://inference:8000`.

## Question 5

> Only `mlflow` and `frontend` publish a port to the host. `inference` doesn't. Why not, and how does the frontend still reach it?

- `inference` is only called by the frontend, never directly by a human, so it doesn't need a port on the host.
- The traffic stays inside the Compose network: the frontend calls `http://inference:8000`, Compose's DNS resolves `inference` to that container, and port 8000 is reached directly on the private network.

## Question 6

> `depends_on` here only waits for the mlflow *container process* to start, not for the tracking server inside it to be ready to accept connections. If your `serve.py` tries to load the Staging model at startup and mlflow isn't ready yet, what happens to the `inference` container? Look at `docker compose logs inference` if it fails.

- If `serve.py` tries to load the model before mlflow is ready, the load fails with a connection error and the `inference` container **exits**.
- The compose file has no restart policy, so it stays stopped even after mlflow becomes ready.

## Question 7

> Run `docker compose ps`. Which services have a published port listed, and which don't? Does that match what you'd expect from the `docker-compose.yml`?

| Service     | Ports                     | Published? |
|-------------|---------------------------|------------|
| `mlflow`    | `0.0.0.0:5000->5000/tcp`  | Yes        |
| `frontend`  | `0.0.0.0:8501->8501/tcp`  | Yes        |
| `inference` | `8000/tcp`                | No         |

- `inference` shows `8000/tcp` with no `->` mapping: the port is open inside the Compose network but not published to the host.
- This matches `docker-compose.yml`, where only `mlflow` and `frontend` have a `ports:` section.

## Question 8

> Refresh the frontend and upload an image again. Does the prediction come from the new model version, or the old one? Your `serve.py` loads the model once, at startup — what single command lets you pick up the new Staging version without rebuilding any image?

- The prediction still comes from **Version 1**. `serve.py` loads `models:/food11@champion` once, at startup, and keeps that model in memory. Moving the alias in mlflow doesn't affect a container that's already running.
- The single command that picks up the new version is:

  ```bash
  docker compose restart inference
  ```

## Question 9

> Why does `restart` alone work here — no rebuild needed? What does that tell you about what's baked into the inference image versus fetched at container startup?

- The model isn't baked into the inference image. The image only contains the code and its dependencies.
- The model is fetched from mlflow **at container startup**. Restarting re-runs that startup, so the `champion` alias is resolved again, now pointing to Version 2, and that model is downloaded.

## Question 10

> Is your registered model and its Staging assignment still there after this `down`/`up` cycle? Now try `docker compose down -v` followed by `docker compose up` — what's different this time, and why?

- After `down`/`up`, the model and its `champion` alias were still there. After `down -v` and `up`, everything was gone: only the Default experiment and no registered models.
- `docker compose down` removes the containers and the network but keeps named volumes, so `mlflow.db` and the artifacts survived in `mlflow-data`. The `-v` flag also deletes the named volumes.

## Question 11

> This compose file is still meant to run on one machine. What would have to change for the `inference` service to run as three replicas behind a load balancer, or for the mlflow service to survive a machine failure? (You don't need to implement this — just name what Docker Compose can't give you here.)

- Compose runs everything on one machine, with no multi-node scheduling, self-healing or real load balancing.
- **Three inference replicas behind a load balancer** need an orchestrator like Kubernetes: a Deployment with replicas, a Service that load-balances, and health checks.
- **mlflow surviving a machine failure** needs its state moved off that host: PostgreSQL instead of SQLite, and S3 instead of the local volume.