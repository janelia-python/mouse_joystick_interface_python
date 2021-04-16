FROM python_package_dev:latest

RUN cd python_package && python setup.py install

ENTRYPOINT ["/bin/bash"]
