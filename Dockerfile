FROM jupyter/scipy-notebook:2023-04-24
# 2023-02-28

# https://www.phind.com/search?cache=225c8894-dc96-4e39-8f12-494486109003


# Set environment variables to avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

USER root

# Update package list and install required dependencies
RUN apt-get update && \
    apt-get install -y software-properties-common

# Install system dependencies
# add-apt-repository -y ppa:bitcoin/bitcoin
RUN apt-get update && \
    apt-get install -y libdb-dev && \
    apt-get install -y libzmq3-dev curl libssl-dev && \
    apt-get install -y libnet-ssleay-perl libcrypt-ssleay-perl zlib1g-dev && \
    apt-get install -y jq && \
    apt-get install -y jupyter-console && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install cpanminus
RUN curl -L https://cpanmin.us | perl - App::cpanminus

# Install the required Perl modules with specific versions
RUN cpanm --notest ZMQ::LibZMQ3 && \
    cpanm --notest ZMQ::FFI && \
    cpanm --notest Devel::IPerl && \
    cpanm --notest BerkeleyDB && \
    cpanm --notest Noid

# https://github.com/rdhyee/noid-1 forked from https://github.com/paulkorir/noid
RUN pip install git+https://github.com/rdhyee/noid-1.git@master#egg=noid \
    click==8.0.3 \
    colorama==0.4.4 


RUN pip install git+https://github.com/rdhyee/ezid-client-tools.git@installable#egg=ezid_client_tools


USER $NB_UID

VOLUME ["/user/jovan/", "/data"]


