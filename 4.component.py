from kfp import compiler
from kfp import dsl


@dsl.component(
    base_image="python:3.12"
)
def print_and_return_number(number: int) -> int:
    print(number)
    return number


compiler.Compiler().compile(
    pipeline_func=print_and_return_number,
    package_path="print_and_return_number.yaml")
