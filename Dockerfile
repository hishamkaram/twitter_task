FROM python:3.7-slim
LABEL "MAINTAINER"="Hisham Karam"
ENV PYTHONUNBUFFERED 1
ARG APP_USER=app
ARG APP_DIR=/usr/src/app
ARG APP_GROUP=app_group
ARG RUN_GID=1000
ARG RUN_UID=1000
COPY . ${APP_DIR}
RUN groupadd -r -g ${RUN_GID} ${APP_GROUP} \
	&& useradd -r -u ${RUN_UID} -g ${APP_GROUP} ${APP_USER}
RUN mkdir -p ${APP_DIR} \
	&& chown -R ${APP_USER}:${APP_GROUP} ${APP_DIR} && chmod g+s ${APP_DIR}
# switch to project dir
WORKDIR ${APP_DIR}
RUN pip install -r requirements.txt
# cleanup image
RUN rm -rf ~/.cache/pip && rm -rf /root/.cache
USER ${APP_USER}
CMD ["/bin/bash"]