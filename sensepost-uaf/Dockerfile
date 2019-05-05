FROM debian:9

RUN apt update && apt install -y --reinstall git python python-pip python3 python3-pip locales gdb gcc wget tmux

# Set the locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN pip install pwntools

WORKDIR /tools
RUN git clone https://github.com/pwndbg/pwndbg
RUN cd pwndbg && ./setup.sh

WORKDIR /chal
COPY glibc_build.sh /chal/
RUN apt install -y gawk
RUN ./glibc_build.sh 2.25 4

COPY chal.py challenge-uaf.c /chal/
RUN gcc -g -o uaf challenge-uaf.c

CMD tmux new-session 'cd /chal && python chal.py'
