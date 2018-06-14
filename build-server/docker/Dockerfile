FROM centos:7

# Script de demarrage du serveur Extensive Testing
COPY launch.sh /usr/sbin/

RUN chmod u+x /usr/sbin/launch.sh

RUN yum -y install vim iproute mariadb-server httpd

RUN yum -y install wget;wget https://extensivetesting.org/ftp/18.0.0/packages/ExtensiveTesting-18.0.0.tar.gz

RUN tar -xzvf ExtensiveTesting-18.0.0.tar.gz

# Modification du script d'installation pour l'adapter a docker (empecher le script de sortir en erreur)
RUN sed -i 's/echo_success/echo "ok"/g' ExtensiveTesting-18.0.0/custom.sh;\
    sed -i 's/echo_failure/echo "failure"/g' ExtensiveTesting-18.0.0/custom.sh;\
    sed -i -e  "33d" ExtensiveTesting-18.0.0/install.sh;\
    sed -i -e  "34d" ExtensiveTesting-18.0.0/custom.sh;\
    sed -i -e  "166d" ExtensiveTesting-18.0.0/custom.sh;\
    sed -i -e  "165d" ExtensiveTesting-18.0.0/custom.sh;\
    sed -i -e  "164d" ExtensiveTesting-18.0.0/custom.sh;\
    sed -i -e  "163d" ExtensiveTesting-18.0.0/custom.sh;\
    sed -i -e  "162d" ExtensiveTesting-18.0.0/custom.sh;\
    sed -i 's/exit_on_error()/echo "Error"/g' ExtensiveTesting-18.0.0/custom.sh;\
    sed -i 's/exit_on_error/echo "Error"/g' ExtensiveTesting-18.0.0/custom.sh

# Demarrage de mariadb et execution du script d'installation d'Extensive Testing
RUN /bin/bash -c "/usr/bin/mysqld_safe --skip-grant-tables &"; \
    sleep 5 ; \
    cd ExtensiveTesting-18.0.0;\
    echo Yes | ./install.sh

# Demarrage du serveur Extensive Testing
CMD ["./usr/sbin/launch.sh"]


