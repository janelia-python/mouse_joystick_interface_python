FROM python:3.8-slim-buster

RUN groupadd --gid 5000 developer \
&& useradd --home-dir /home/developer --create-home --uid 5000 \
--gid 5000 --shell /bin/sh --skel /dev/null developer

WORKDIR /home/developer

ENV VIRTUAL_ENV=/home/developer/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN chown -R developer:developer $VIRTUAL_ENV

ENV SETUPTOOLS_SCM_PRETEND_VERSION="1.2.3"

ENV DEVELOPMENT_PACKAGE_PATH=/home/developer/python_package/
COPY . $DEVELOPMENT_PACKAGE_PATH
RUN chown -R developer:developer $DEVELOPMENT_PACKAGE_PATH

USER developer

RUN pip install ipython

ENTRYPOINT ["/bin/bash"]
