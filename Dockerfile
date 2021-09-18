
# docker build -t waggle/app-image-viewer .
# docker run -ti --rm -p 8000:80 waggle/app-image-viewer

FROM python:3.9.7
EXPOSE 80
WORKDIR /app
COPY main.py requirements.txt ./
RUN pip3 install -U -r requirements.txt

CMD streamlit run main.py --server.port 80
