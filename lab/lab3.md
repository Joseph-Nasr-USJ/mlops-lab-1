## Question 1

> Question 1: Open the "Models" tab in the mlflow UI. What version number was your model given? What's the difference between a run's logged model artifact and a registered model?

- The model was given Version 1. 
- The difference between a run's logged model artifact and registered model is:
    - The Logged Model Artifact: Represents the files saved by the run. Each run within the experiment has a logged model artifact.
    - The Registered Model: A named and versioned entry that points to one of those logged model artifacts, it can also have aliases like 'champion'


## Question 2

> Question 2: What aliases replaced the old built-in stages in mlflow? Why version a model separately from the run that produced it, and why is an alias more flexible than a fixed stage name?

- Aliases like `champion` and `challenger` replaced the old built-in stages in mlflow. 
- We version a model separately from the run that produced it to be able to easily swap versions and roll back, without having to know which run produced the chosen model, using the chosen model's name and version history.
- An alias is more flexible than a fixed stage name because: we can create as many aliases as we want using names of our choosing, we can assign an alias to another version at any time, and helps keep the code more robust and stable (the code will always point to an alias regardless of what version that alias is assigned to) 


## Question 3

> Question 3: Why load the model through an mlflow model URI (`models:/food11@champion`) instead of pointing directly at the `.pth` file on disk? What would you have to change to serve a newer model version?

- Loading the model through an mlflow model URI (`models:/food11@champion`) means we don't need a specific Run ID. Instead, the alias in the URI tells Mlflow which model to use.
- To serve a newer model version, the code stays the same, but in MLflow we reassign the alias `champion` to the newer version.


## Question 4

> Question 4: Why copy `pyproject.toml`/`uv.lock` and run `uv sync` *before* copying the rest of the source code, instead of copying everything at once? What happens to the build cache when you only change a line in `serve.py`?

- Since docker rebuilds from the first layer whose inputs changed, copying `pyproject.toml`/`uv.lock` and running `uv sync` first ensures this layer remains cached since dependencies rarely change.
- Changing one line in `serve.py`, only `COPY src/` and the layers after it rebuild.


## Question 5

> Question 5: What's the size difference between a naive single-stage image and your multi-stage one? Use `docker history <image>` to see which layers are the biggest.

- The multi-stage image is 9.58 GB on disk. Docker history shows the biggest layer is COPY /app/.venv, at 6.19 GB.
- That said, a naive single-stage image would yet be bigger because it keeps the full Debian base with compilers and build tools which are not needed at runtime.
- IMAGE          CREATED       CREATED BY                                      SIZE      COMMENT
0dbec4a1a79c   2 hours ago   ENTRYPOINT ["uvicorn" "src.food11.serve:app"…   0B        buildkit.dockerfile.v0
<missing>      2 hours ago   EXPOSE [8000/tcp]                               0B        buildkit.dockerfile.v0
<missing>      2 hours ago   ENV PATH=/app/.venv/bin:/usr/local/bin:/usr/…   0B        buildkit.dockerfile.v0
<missing>      2 hours ago   COPY src/ ./src/ # buildkit                     49.2kB    buildkit.dockerfile.v0
<missing>      2 hours ago   COPY /app/.venv /app/.venv # buildkit           6.19GB    buildkit.dockerfile.v0
<missing>      2 hours ago   WORKDIR /app                                    8.19kB    buildkit.dockerfile.v0
<missing>      2 days ago    CMD ["python3"]                                 0B        buildkit.dockerfile.v0
<missing>      2 days ago    RUN /bin/sh -c set -eux;  for src in idle3 p…   16.4kB    buildkit.dockerfile.v0
<missing>      2 days ago    RUN /bin/sh -c set -eux;   savedAptMark="$(a…   41.4MB    buildkit.dockerfile.v0
<missing>      2 days ago    ENV PYTHON_SHA256=c2c4321961fab0fb999d66e0ce…   0B        buildkit.dockerfile.v0
<missing>      2 days ago    ENV PYTHON_VERSION=3.12.15                      0B        buildkit.dockerfile.v0
<missing>      2 days ago    ENV GPG_KEY=7169605F62C751356D054A26A821E680…   0B        buildkit.dockerfile.v0
<missing>      2 days ago    RUN /bin/sh -c set -eux;  apt-get update;  a…   4.94MB    buildkit.dockerfile.v0
<missing>      2 days ago    ENV LANG=C.UTF-8                                0B        buildkit.dockerfile.v0
<missing>      2 days ago    ENV PATH=/usr/local/bin:/usr/local/sbin:/usr…   0B        buildkit.dockerfile.v0
<missing>      3 days ago    # debian.sh --arch 'amd64' out/ 'trixie' '@1…   87.7MB    debuerreotype 0.17


## Question 6

> Question 6: What happens to build speed and image size if you forget the `.dockerignore`? Which of the excluded folders would actually break the build if they were sent to the Docker daemon?

- Without `.dockerignore`, all of the folders mentioned in it would be sent to the docker daemon on every build, making build speed much slower.
- The folder in `.dockerignore` that would break the build if sent to the daemon is the `.venv`


## Question 7

> Question 7: Why can't the container simply use `127.0.0.1:5000` to reach the mlflow server on your host? What does `host.docker.internal` resolve to?

- The container can't use `127.0.0.1:5000` because aside from `127.0.0.1` referring to the container itself, each container has its own isolated network so nothing is listening on port 5000
- `host.docker.internal` resolves to the host machine's IP address.


## Question 8

> Question 8: Stop the container and start a new one from the same image. Does the model still load correctly without you rebuilding? What does that tell you about what's baked into the image versus fetched at runtime?

Yes, the model loads without rebuilding. The image only contains the code and dependencies. Each new container fetches the model at startup from MLflow through `models:/food11@champion`


## Question 9

> Question 9: The Dockerfile and image are versioned differently — one lives in git, the other doesn't (yet). What's still missing before another machine (like a CI runner or a Kubernetes cluster) could reliably pull and run the exact image you just built?

For another machine to to pull and run the exact image I built, it needs the image to be pushed to a container registry, a fixed tag, and access to the MLflow artifacts.