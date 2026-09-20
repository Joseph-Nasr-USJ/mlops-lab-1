# mlops-lab-1 — git/dvc and data preparation

Lab 1: creating git and dvc repos, seeing how they work together, and preparing the Food-11 data files.

**Solution adopted for pushing the data:** option 1 — local remote. The DagsHub `dvc push` repeatedly failed with dropped connections and socket timeouts while uploading ~13,000 image files, so the DVC remote was set to a local folder outside the git repo:

```bash
dvc remote add -d localremote C:\Users\joseph.nasr\dvc-storage
```

---

## Question 1

> Observe the files created by `uv init`, what do you think they contain.

The `.toml` contains project configuration details similar to JSON. The `README.md` contains project documentation details and what other developers see/know if they work on it. The `.python-version` is the python version.

## Question 2

> What are the created files. What do you think they are used for? And which ones should be pushed to git?

- `.dvc` and `.dvcignore` were created.
- `.dvc` holds cache, tmp, and a config file while `.dvcignore` specifies which data paths should be ignored while versioning.
- `.dvc/config`, `.dvc/.gitignore` and `.dvcignore` were pushed to github.

## Question 3

> Where are the credentials stored? And what are the options other than `--global`? Should the credentials be pushed to github?

- Other than `--global`, I used `--local`.
- Using `--local`, credentials are stored in `.dvc/config.local`.
- Credentials should certainly never get pushed to github.

## Question 4

> Take a look at the `.gitignore` file. Explain what happened.

- `/data` was added to the `.gitignore` file.
- The data will be ignored by git and not pushed to GitHub.

## Question 5

> Do you see a `.dvc` file? What does it contain?

Yes. It contains the md5 hash and acts as the data pointer that gets tracked by git.

## Question 6

> You can check your main branch on the github web UI. Is the code there? Is the data there? Do you have any file that points to the data location. And what about dagshub web UI do you see the data?

- The code files are there on github (`.dvc/`, `.dvcignore`, `.gitignore`, `data.dvc`).
- The data is not on github.
- `data.dvc` points to the data location.
- DagsHub web UI shows nothing because I opted for a local dvc remote.

## Question 7

> In a completely new temporary folder clone your github repo. Do you see the data folder? What dvc command is needed to get the data folder?

```bash
git clone https://github.com/Joseph-Nasr-USJ/mlops-lab-1.git temp-clone
```

- The data folder is not cloned into the temp folder because it is not on GitHub.
- The dvc command needed is `dvc pull`.

## Question 8

> Do you still see the new folders you created? `food11_processed` and `food11_processed_mini`?

- After reverting to the "Track data folder with dvc" commit, I no longer see the new folders.
- The data files `food11_processed` and `food11_processed_mini` are gone because the checkout set the `data.dvc` pointer to an older commit.
