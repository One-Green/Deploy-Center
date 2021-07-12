FROM python:3.9.6

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED TRUE

EXPOSE 8501
ENTRYPOINT ["streamlit","run"]
CMD ["ui.py"]