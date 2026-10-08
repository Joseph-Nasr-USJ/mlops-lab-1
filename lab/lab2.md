## Question 1

> Look at pyproject.toml and uv.lock. What changed?

In `pyproject.toml`, inside dependencies, the following were added:
    "mlflow>=3.16.1",
    "scikit-learn>=1.9.1",
    "torch>=2.14.0",
    "torchvision>=0.29.0",

As for `uv.lock`, 119 "[[package]]" blocks were added as well as 'resolution-markers'

## Question 2

> Question 2: What is `--backend-store-uri` used for? What is `--default-artifact-root` used for? What is the difference between the metadata mlflow stores and the artifacts it stores?

`--backend-store-uri` is where mlflow stores metadata (in mlflow.db) while `--default-artifact-root` is where mlflow stores artifacts ('mlruns' is still not visible).
Artifacts are the files produced by a run while metadata is details describing a particulat run.


## Question 3

> Question 3: Why shouldn't `mlflow.db` and `mlruns/` be tracked by git, and why shouldn't they be tracked by dvc either?

As I mentioned, `mlflow.db` mlflow stores metadata pertaining to a specific run, so every run this data changes, which committing every run tedious. `mlruns/` contains large files, so pushing to github is not recommended. As for DVC, it is meant to be versioning the dataset not what's being updated during runs.

## Question 4

> Question 4: What happens the first time you call `set_experiment` with a name that doesn't exist yet? Check the mlflow UI.

I got a message in terminal saying the experiment does not exist and that a new one is being created.
`2026/09/26 23:03:19 INFO mlflow.tracking.fluent: Experiment with name 'food11' does not exist. Creating a new experiment.`

## Question 5

> Question 5: What is the difference between `mlflow.log_param` and `mlflow.log_metric`? Why does `log_metric` take a `step` argument and `log_param` doesn't?

`mlflow.log_param` logs a parameter that remains fixed for the entire run and cannot change during runtime like the batch size whereas `mlflow.log_metric` logs a value produced after runtime like loss and accuracy. `log_metric` takes a `step` argument to log that metric's value at that step during runtime; param doesn't change during runtime so there's no step to log.

## Question 6

> Question 6: Open the run in the mlflow UI. Find the params, the metric charts, and the logged model artifact. Where does the model artifact actually live on disk?

Found the metric charts in the mlflow UI under 'Model metrics' and the params:
train_loss
0.3962289502403953
-
val_loss
2.0642884602076816
-
val_accuracy
0.5136861313868614
-
test_accuracy
0.5775547445255474

I also Found the model artifact in the newly created `mlruns\1\models\m-9617d0f5b74948d9adaa92eb026893b1\artifacts` folder on disk. 


## Question 7

> Question 7: In the mlflow UI, open the `food11` experiment. Select these runs and click "Compare". Which learning rate gave the best `val_accuracy`? Is higher always better?

Learning rate `0.0001` gave the best `val_accuracy` of 71.4% which shows that a higher learning rate is not always 'better' because the highest learning rate of `0.01` gave a `val_accuracy` of 17.4% (lowest `val_accuracy`)

## Question 8

> Question 8: Use the parallel coordinates plot on the compare page to look at `lr`, `batch_size` and `val_accuracy` together. What pattern do you see?

In 2 runs, `lr` was set to 0.01 but once with `batch_size` set to 32 and in another to 64. Both runs resulted in very close `val_accuracy`. 
In comparison, with `batch_size` set to 32 but in one run with `lr` set to 0.01 and in another to 0.0001, resulted in the worst and best `val_accurarcy` respectively.
It is noticeable that `batch_size` is not affecting `val_accuracy` as much as `lr`.

## Question 9

> Question 9: Sort the runs table by `val_accuracy` descending. Which run is the best one? Note its run ID, you'll need it in the next lab.

After sorting, the ID of the run with highest `val_accuracy` is `7da115eea286458cb86fb07a44804a6b`

