FROM python:3.9
WORKDIR /code
COPY . /code
RUN apt-get -y update
RUN apt-get -y install texlive-fonts-recommended texlive-latex-recommended texlive-latex-extra 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD ["python", "main.py"]
