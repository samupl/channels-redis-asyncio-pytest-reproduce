FROM python:3.11-slim

WORKDIR /app

RUN pip install pipenv
ADD Pipfile.lock .
ADD Pipfile .

RUN pipenv install --dev --system --ignore-pipfile

ADD . .

RUN python --version
#ENTRYPOINT ["pytest", "example_app/tests/test_reproduce.py::TestChatCommunicator::test_reproduce_exception", "example_app/tests/test_reproduce.py::TestChatCommunicator::test_reproduce_ok", "--reuse-db"]
#ENTRYPOINT ["bash"]
CMD ["bash"]
