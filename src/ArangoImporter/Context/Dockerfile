FROM python:3.12-alpine

LABEL authors="Marwan Ait Addi-Russier"
LABEL source.repo = "https://github.com/CNRS-Teatime/TEATIME_PhD_Experiments"

ADD ../main.py .
ADD ../../../requirements.txt .


RUN git clone --no-checkout https://github.com/CNRS-Teatime/TEATIME_PhD_Experiments
RUN cd TEATIME_PhD_Experiments
RUN git sparse-checkout set src/ArangoImporter && git checkout

WORKDIR src/ArangoImporter

RUN pip install -r requirements.txt

#Setting up environment
ENV THESO_CONFIG=${THESO_CONFIG}
ENV GRAPH_CONFIG=${GRAPH_CONFIG}
ENV DUMP_PATH=${DUMP_PATH}

COPY Context/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]