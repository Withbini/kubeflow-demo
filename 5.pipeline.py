from kfp import dsl


@dsl.component(
    base_image="python:3.12"
)
def print_and_return_number(number: int) -> int:
    print(number)
    return number


@dsl.component(
    base_image="python:3.12"
)
def sum_and_print_numbers(number_1: int, number_2: int) -> int:
    sum_num = number_1 + number_2
    print(sum_num)
    return sum_num


@dsl.pipeline(
    name="example",
)
def example_pipeline(number_1: int, number_2: int):
    number_1_result = print_and_return_number(number=number_1)
    number_2_result = print_and_return_number(number=number_2)
    sum_result = sum_and_print_numbers(number_1=number_1_result.output, number_2=number_2_result.output)


if __name__ == "__main__":
    from kfp import compiler

    compiler.Compiler().compile(pipeline_func=example_pipeline,
                                package_path="example_pipeline.yaml")
