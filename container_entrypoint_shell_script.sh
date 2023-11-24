#!/bin/bash

set -e
set -o pipefail

# Constants

MOUNTED_MODULE_SEARCH_PATH='/mnt/mounted_module_search_path'

# MUST NOT end with a '/', otherwise breaks hityper
LOCAL_MODULE_SEARCH_PATH='/tmp/local_module_search_path'

OUTPUT_PATH='/mnt/output_path'

TYPE_ANNOTATIONS_JSON="${OUTPUT_PATH}/type_annotations.json"


# Variables from command-line arguments

# Module prefix, pass with `-p`
module_prefix=

while getopts ':p:' name
do
    case $name in
        p)
            module_prefix="$OPTARG"
            ;;
        :)
            echo "Option -$OPTARG requires an argument"
            ;;
        ?)
            echo "Invalid option -$OPTARG"
            ;;
    esac
done

# Sanity check

if [ ! -d "$MOUNTED_MODULE_SEARCH_PATH" ]
then
    echo "Module search path is not mounted to ${MOUNTED_MODULE_SEARCH_PATH}" >&2
    echo "Please provide a mount point with your Docker run command: " >&2
    echo "docker run --net=host -v <module_search_path>:${MOUNTED_MODULE_SEARCH_PATH}:ro -v <output_path>:${OUTPUT_PATH} ..." >&2
    exit 1
fi

if [ ! -d "$OUTPUT_PATH" ]
then
    echo "Output path is not mounted to ${OUTPUT_PATH}" >&2
    echo "Please provide a mount point with your Docker run command: " >&2
    echo "docker run --net=host -v <module_search_path>:${MOUNTED_MODULE_SEARCH_PATH}:ro -v <output_path>:${OUTPUT_PATH} ..." >&2
    exit 1
fi

# Preprocessing

# Copy contents from $MOUNTED_MODULE_SEARCH_PATH to $LOCAL_MODULE_SEARCH_PATH
cp -R "$MOUNTED_MODULE_SEARCH_PATH" "$LOCAL_MODULE_SEARCH_PATH"

# Install requirements.txt if it exists
if [ -f "$LOCAL_MODULE_SEARCH_PATH/requirements.txt" ]; then
    python -m pip install -r "$LOCAL_MODULE_SEARCH_PATH/requirements.txt"
fi

# Run main, modifying the contents of $LOCAL_MODULE_SEARCH_PATH
python /root/main.py -s "$LOCAL_MODULE_SEARCH_PATH" -p "$module_prefix" -o "$TYPE_ANNOTATIONS_JSON"
