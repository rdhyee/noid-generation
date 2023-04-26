FROM jupyter/scipy-notebook:2023-02-28

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
RUN pip install git+https://github.com/rdhyee/noid-1.git@master#egg=noid


# USER $NB_UID

# VOLUME ["/user/jovan/", "/data"]


# USER root
# RUN apt-get update && apt-get -yq dist-upgrade \
#     && apt-get install -yq --no-install-recommends \
#     libxml2-dev \
#     libxslt1-dev \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# # USER jovyan

# RUN pip install lxml
# RUN pip install mwclient
# # RUN pip install git+git://github.com/mwclient/mwclient@v0.7.1
# # RUN pip install https://bitbucket.org/rdhyee/mwclient/get/wpp.tar.bz2
# # RUN pip install git+git://github.com/rdhyee/mwclient@wpp_integrate

# RUN pip install responses && \
#     pip install pytest && \
#     pip install boltons && \
#     pip install pywikibot && \
#     pip install cssselect

# COPY notebooks/ /home/jovyan/work
# # A bit ugly but unfortunately necessary: https://github.com/docker/docker/issues/6119
# USER root
# RUN chown -R jovyan:users /home/jovyan/work

# #USER jovyan


