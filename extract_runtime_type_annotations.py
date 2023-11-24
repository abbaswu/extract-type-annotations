import logging
import types
import typing

from query_result_dict import QueryDict


def extract_runtime_type_annotations(
        module_name_to_module_mapping: typing.Mapping[str, types.ModuleType],
        query_dict: QueryDict,
        runtime_type_annotation_callback: typing.Callable[
            [
                types.ModuleType,  # module
                str,  # module_name
                str,  # class_name_or_global
                str,  # function_name
                str,  # parameter_name_or_return
                typing.Any  # runtime_type_annotation
            ],
            None
        ]
):
    for module_name, module_level_query_dict in query_dict.items():
        if module_name not in module_name_to_module_mapping:
            logging.error('Module %s not found', module_name)
            continue

        module = module_name_to_module_mapping[module_name]

        for class_name_or_global, class_level_query_dict in module_level_query_dict.items():
            runtime_class_name_or_global: typing.Union[types.ModuleType, type]

            if class_name_or_global == 'global':
                runtime_class_name_or_global = module
            else:
                if (
                        class_name_or_global not in module.__dict__
                        or not isinstance(module.__dict__[class_name_or_global], type)
                ):
                    logging.error('Class %s not found in module %s', class_name_or_global, module_name)
                    continue

                runtime_class_name_or_global = module.__dict__[class_name_or_global]

            for function_name, function_level_query_dict in class_level_query_dict.items():
                runtime_function: types.FunctionType

                if (
                        function_name not in runtime_class_name_or_global.__dict__
                        or not isinstance(runtime_class_name_or_global.__dict__[function_name], types.FunctionType)
                ):
                    logging.error(
                        'Function %s not found in class %s in module %s',
                        function_name,
                        class_name_or_global,
                        module_name
                    )
                    continue

                runtime_function = runtime_class_name_or_global.__dict__[function_name]

                for parameter_name_or_return in function_level_query_dict:
                    if (
                            not hasattr(runtime_function, '__annotations__')
                            or parameter_name_or_return not in runtime_function.__annotations__
                    ):
                        logging.error(
                            'Function %s in class %s in module %s has no type annotation for parameter %s',
                            function_name,
                            class_name_or_global,
                            module_name,
                            parameter_name_or_return
                        )
                        continue

                    runtime_type_annotation = runtime_function.__annotations__[parameter_name_or_return]

                    runtime_type_annotation_callback(
                        module,
                        module_name,
                        class_name_or_global,
                        function_name,
                        parameter_name_or_return,
                        runtime_type_annotation
                    )
