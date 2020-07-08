FROM ubuntu:18.04
WORKDIR /code
ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 8000
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-dev \
    python3-pip libglib2.0-0 libsm6 libxext6 libxrender-dev \
    build-essential libssl-dev libffi-dev

RUN pip3 install -U pip setuptools 
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY app.py arg_parser.py box_types.py file_utils.py rrc_evaluation_funcs.py script.py validation.py ./ 

CMD ["flask", "run"]