FROM python:3.12.2-bookworm
WORKDIR /app
COPY ./app /app
RUN pip install -r /app/requirements.txt
CMD ["streamlit", "run", "pyFinanceTrackerWebapp.py"]
