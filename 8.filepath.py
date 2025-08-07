from kfp.compiler import compiler
from kfp.dsl import component, Input, Output, Dataset, pipeline


@component(base_image="python:3.12",
           packages_to_install=['dill', 'pandas', 'sklearn'])
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


@component(base_image="python:3.12", packages_to_install=['pandas', 'sklearn'])
def load_iris_data(
        data_path: Output[Dataset],
        target_path: Output[Dataset],
):
    import pandas as pd
    from sklearn.datasets import load_iris

    iris = load_iris()

    data = pd.DataFrame(iris["data"], columns=iris["feature_names"])
    target = pd.DataFrame(iris["target"], columns=["target"])

    data.to_csv(data_path.path, index=False)
    target.to_csv(target_path.path, index=False)


@pipeline(name="complex_pipeline")
def complex_pipeline(kernel: str = "linear"):
    iris_data = load_iris_data()
    model = train_from_csv(
        train_data_path=iris_data.outputs["data_path"],
        train_target_path=iris_data.outputs["target_path"],
        kernel=kernel,
    )


compiler.Compiler().compile(
    pipeline_func=complex_pipeline,
    package_path="complex_pipeline.yaml")
