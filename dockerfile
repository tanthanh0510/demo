FROM nvidia/cuda:12.2.0-base-ubuntu22.04

WORKDIR /app

RUN apt-get update && DEBIAN_FRONTEND=noninteractive \
    apt-get install -y python3.10 python3-pip

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN mkdir uploads
# RUN wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=FILEID' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1sf20ZEFO8MyF0r6_yzYC43_FsNMdWzXa" -O checkpoint.zip && rm -rf /tmp/cookies.txt && unzip checkpoint.zip && rm checkpoint.zip
# RUN mv checkpoint-7700 checkpoint
# RUN pip install torch==2.0.0 torchvision==0.15.1 --index-url https://download.pytorch.org/whl/cu118
RUN pip install torch==2.0.0 --index-url https://download.pytorch.org/whl/cu118
RUN cd /usr/local/lib/python3.10/dist-packages/torch/lib \
    ln -s libnvrtc-672ee683.so.11.2 libnvrtc.so
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["bash", "run.sh"]
# docker run --gpus all -it -p 8080:8080 -t caption
# Setup container toolkit for docker using GPU
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuration