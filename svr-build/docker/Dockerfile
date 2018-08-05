FROM centos:7

# Script de demarrage du serveur Extensive Automation
COPY launch.sh /usr/sbin/

RUN chmod u+x /usr/sbin/launch.sh

RUN yum -y install vim iproute mariadb-server httpd

RUN yum -y install wget;wget https://www.extensiveautomation.org/ftp/19.0.0/packages/ExtensiveAutomation-19.0.0.tar.gz

RUN tar -xzvf ExtensiveAutomation-19.0.0.tar.gz

# Modification du script d'installation pour l'adapter a docker (empecher le script de sortir en erreur)
RUN sed -i 's/echo_success/echo "ok"/g' ExtensiveAutomation-19.0.0/custom.sh;\
    sed -i 's/echo_failure/echo "failure"/g' ExtensiveAutomation-19.0.0/custom.sh;\
    sed -i -e  "33d" ExtensiveAutomation-19.0.0/install.sh;\
    sed -i -e  "34d" ExtensiveAutomation-19.0.0/custom.sh;\
    sed -i -e  "166d" ExtensiveAutomation-19.0.0/custom.sh;\
    sed -i -e  "165d" ExtensiveAutomation-19.0.0/custom.sh;\
    sed -i -e  "164d" ExtensiveAutomation-19.0.0/custom.sh;\
    sed -i -e  "163d" ExtensiveAutomation-19.0.0/custom.sh;\
    sed -i -e  "162d" ExtensiveAutomation-19.0.0/custom.sh;\
    sed -i 's/exit_on_error()/echo "Error"/g' ExtensiveAutomation-19.0.0/custom.sh;\
    sed -i 's/exit_on_error/echo "Error"/g' ExtensiveAutomation-19.0.0/custom.sh

# Demarrage de mariadb et execution du script d'installation d'Extensive Automation
RUN /bin/bash -c "/usr/bin/mysqld_safe --skip-grant-tables &"; \
    sleep 5 ; \
    cd ExtensiveAutomation-19.0.0;\
    echo Yes | ./install.sh

# Demarrage du serveur Extensive Automation
CMD ["./usr/sbin/launch.sh"]


