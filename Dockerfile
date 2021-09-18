FROM python:3.9
EXPOSE 80
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -U -r requirements.txt
COPY . .
CMD streamlit run main.py --server.port 80
