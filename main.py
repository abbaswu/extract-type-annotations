import argparse
import importlib
import json
import logging
import sys
import types
import typing

import static_import_analysis
from extract_runtime_type_annotations import extract_runtime_type_annotations
from parse_runtime_type_annotation import parse_runtime_type_annotation
from query_result_dict import QueryDict, generate_query_dict, RawResultDefaultdict, get_raw_result_defaultdict


def main(
        module_search_path: str,
        module_prefix: str,
        output_json: str
):
    # Find modules
    (
        module_name_to_file_path_dict,
        module_name_to_function_name_to_parameter_name_list_dict,
        module_name_to_class_name_to_method_name_to_parameter_name_list_dict,
        module_name_to_import_tuple_set_dict,
        module_name_to_import_from_tuple_set_dict
    ) = static_import_analysis.do_static_import_analysis(module_search_path, module_prefix)

    # Generate query dict
    query_dict: QueryDict = generate_query_dict(
        module_name_to_file_path_dict,
        module_name_to_function_name_to_parameter_name_list_dict,
        module_name_to_class_name_to_method_name_to_parameter_name_list_dict
    )

    # Import modules
    sys.path.insert(0, module_search_path)

    module_name_to_module_dict: dict[str, types.ModuleType] = {}
    for module_name, file_path in module_name_to_file_path_dict.items():
        try:
            module_name_to_module_dict[module_name] = importlib.import_module(module_name)
        except ImportError:
            logging.exception('Failed to import module `%s`', module_name)

    raw_result_defaultdict: RawResultDefaultdict = get_raw_result_defaultdict()

    def runtime_type_annotation_callback(
            module: types.ModuleType,
            module_name: str,
            class_name_or_global: str,
            function_name: str,
            parameter_name_or_return: str,
            runtime_type_annotation: typing.Any
    ):
        type_annotation = parse_runtime_type_annotation(
            runtime_type_annotation,
            module
        )

        raw_result_defaultdict[module_name][class_name_or_global][function_name][parameter_name_or_return].append(
            str(type_annotation)
        )

    # Extract runtime type annotations
    extract_runtime_type_annotations(
        module_name_to_module_dict,
        query_dict,
        runtime_type_annotation_callback
    )

    with open(output_json, 'w') as output_json_io:
        json.dump(raw_result_defaultdict, output_json_io, indent=4)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s'
    )

    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--module-search-path', type=str, required=True,
                        help='Module search path')
    parser.add_argument('-p', '--module-prefix', type=str, required=False, default='',
                        help="Module prefix")
    parser.add_argument('-o', '--output-json', type=str, required=True)
    args = parser.parse_args()

    main(
        args.module_search_path,
        args.module_prefix,
        args.output_json
    )
