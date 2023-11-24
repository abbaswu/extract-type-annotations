# docker build --tag run_methods_container .

# Set the base image to Ubuntu (22.04)
FROM ubuntu

# Install base utilities
RUN apt-get update \
    && apt-get install -y build-essential git watchman \
    && apt-get clean

# Install miniconda
# Put conda in path so we can use conda init
COPY Miniconda3-latest-Linux-x86_64.sh /root
ENV CONDA_ROOT /root/miniconda3
ENV PATH=$CONDA_ROOT/bin:$PATH
RUN /bin/bash /root/Miniconda3-latest-Linux-x86_64.sh -b -p $CONDA_ROOT && conda init

# Install packages required in entrypoint and data processing scripts
RUN conda run --name base pip install lark pudb

# Copy entrypoint and data processing scripts
COPY static_import_analysis /root/static_import_analysis/
COPY *.py *.sh /root/

# command executable and version
ENTRYPOINT ["/bin/bash", "/root/container_entrypoint_shell_script.sh"]
