

# docker build -t waggle/app-image-viewer .
# docker run -ti --rm -p 8000:80 waggle/app-image-viewer

#FROM python:3.9.7-bullseye
#FROM python:3.8.12-bullseye
FROM python:3.6

# alpine image is too slow
# see https://stackoverflow.com/questions/49037742/why-does-it-take-ages-to-install-pandas-on-alpine-linux

COPY main.py requirements.txt ./

RUN pip3 install -U -r requirements.txt

# cache does not work inside docker container (see https://github.com/streamlit/streamlit/issues/2387)
RUN sed -i -e 's/@st.cache/#@st.cache/' ./main.py


CMD streamlit run ./main.py --server.port 80