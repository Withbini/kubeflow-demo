from kfp.compiler import compiler
from kfp.dsl import component, Input, Output, Dataset


@component(base_image="python:3.12")
def train_from_csv(
        train_data_path: Input[Dataset],
        train_target_path: Input[Dataset],
        model_path: Output[Dataset],
        kernel: str
):
    import dill
    import pandas as pd
    from sklearn.svm import SVC

    train_data = pd.read_csv(train_data_path.path)
    train_target = pd.read_csv(train_target_path.path)

    clf = SVC(kernel=kernel)
    clf.fit(train_data, train_target)

    with open(model_path.path, mode="wb") as f:
        dill.dump(clf, f)


compiler.Compiler().compile(
    pipeline_func=train_from_csv,
    package_path="train_from_csv.yaml")
