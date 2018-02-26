FROM ubuntu:16.04

LABEL maintainer="Craig Citro <craigcitro@google.com>"

# Pick up some TF dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libfreetype6-dev \
        libpng12-dev \
        libzmq3-dev \
        pkg-config \
        python3 \
        python3-dev \
        python3-pip \
        rsync \
        software-properties-common \
        unzip \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
    
RUN pip3 install --upgrade pip

RUN pip3 --no-cache-dir install \
        Pillow \
        h5py \
        ipykernel \
        jupyter \
        matplotlib \
        numpy \
        pandas \
        scipy \
        sklearn \
        && \
    python -m ipykernel.kernelspec

# COPY _PIP_FILE_ /
# RUN pip3 --no-cache-dir install /_PIP_FILE_
# RUN rm -f /_PIP_FILE_

# Install TensorFlow CPU version from central repo
RUN pip3 --no-cache-dir install --upgrade tensorflow
RUN ln -s /usr/bin/python3 /usr/bin/python#

# TensorBoard
EXPOSE 6006
# IPython
EXPOSE 8888

## END OF TENSORFLOW & Python


COPY VideoExpertSystem  /VideoExpertSystem/VideoExpertSystem
COPY Models/tf_files-v0.3-docker /VideoExpertSystem/Models/tf_files-v0.3
COPY WebInterface /VideoExpertSystem/WebInterface
COPY VideoCache /VideoExpertSystem/VideoCache
WORKDIR "/VideoExpertSystem"

CMD ["python3", "--allow-root"]