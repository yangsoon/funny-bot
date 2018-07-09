FROM python:3
ADD /bot /tgbot
WORKDIR /tgbot
RUN pip install -r requirements.txt
CMD ["python3", "main.py"]
