FROM public.ecr.aws/panorama/panorama-application

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt /panorama/requirements.txt
RUN pip install --no-cache-dir -r /panorama/requirements.txt

COPY src /panorama
