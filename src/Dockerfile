FROM python:3.7.4-alpine3.10

LABEL name="Extensive Automation" \
      description="ExtensiveAutomation is a generic automation framework for integration, regression and end-to-end usages" \
      url="https://github.com/ExtensiveAutomation" \
      maintainer="d.machard@gmail.com"

WORKDIR /home/extensive

COPY . /home/extensive/

RUN true \
    && adduser -D extensive \
    && apk add --update --no-cache g++ make libxslt-dev curl \
    && pip install --no-cache-dir wrapt pycnic lxml jsonpath_ng \
    && apk del --no-cache g++ make \
    && cd /home/extensive \
    && chmod 755 start.sh \
    && chown -R extensive:extensive /home/extensive \
    && sed -i 's/python=.*/python=\/usr\/local\/bin\/python/' /home/extensive/ea/settings.ini \
    && true
    
USER extensive

EXPOSE 8081/tcp 8082/tcp 8083/tcp

ENTRYPOINT ["/home/extensive/start.sh"]
