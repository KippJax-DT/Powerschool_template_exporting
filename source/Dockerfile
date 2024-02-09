FROM public.ecr.aws/lambda/python:3.11 as stage 

RUN yum install -y unzip && \
    curl -Lo "/tmp/chromedriver.zip" "https://chromedriver.storage.googleapis.com/98.0.4758.48/chromedriver_linux64.zip" && \
    curl -Lo "/tmp/chrome-linux.zip" "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F950363%2Fchrome-linux.zip?alt=media" && \
    unzip /tmp/chromedriver.zip -d /opt/ && \
    unzip /tmp/chrome-linux.zip -d /opt/

RUN yum install atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel -y

RUN pip install --upgrade pip
RUN pip install selenium

COPY requirements.txt ${LAMBDA_TASK_ROOT}
COPY app.py ${LAMBDA_TASK_ROOT}
RUN python3.11 -m pip install -r requirements.txt -t .

# Install AWS CLI and configure
RUN pip install awscli
RUN aws configure set aws_access_key_id ${aws_access_key_id}
RUN aws configure set aws_secret_access_key ${aws_secret_access_key}
RUN aws configure set region us-east-1
RUN aws configure set output json

#  Unzipping zip file in python script

CMD ["app.lambda_handler"]