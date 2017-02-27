배포하기
===============================================

Docker를 이용한 배포
--------------------

kaistusc 프로젝트는 Docker_ 를 이용하여 손쉽게 배포할 수 있습니다.

.. code-block:: bash

    $ sudo wget -qO- https://get.docker.com/ | sh
    $ sudo docker rm `sudo docker ps -aq`
    $ sudo docker rmi hello-world

Linux 기준 위 명령어를 통해 docker를 설치합니다. 다른 OS의 경우 이곳__ 을 참고하세요.

프로젝트 소스를 다운받지 않았다면 아래 명령어를 통해 받아주세요.

.. code-block:: bash

    $ git clone https://github.com/hangpark/kaistusc.git

Docker로 DB 서버 구축
---------------------

kaistusc는 기본적으로 MySQL_ 을 사용합니다. 다른 DBMS의 경우 :file:`settings.py` 등을 적절히 수정해야 합니다. 여기서는 MySQL 서버를 구축하도록 하겠습니다. MySQL 서버 이미지를 다운받기 위해 아래의 명령어를 입력합니다.

.. code-block:: bash

    $ sudo docker pull mysql/mysql-server:5.7

받아진 이미지를 바탕으로 :dfn:`kaistusc-db` 이름의 컨테이너를 만듭니다.

.. code-block:: bash

    $ sudo docker run --name kaistusc-db \
    > -v {{ project_path }}/mysql.cnf:/etc/my.cnf \
    > -v {{ data_store_dir }}:/var/lib/mysql \
    > -e MYSQL_USER={{ mysql_user }} \
    > -e MYSQL_PASSWORD={{ mysql_password }} \
    > -e MYSQL_DATABASE=kaistusc \
    > -e MYSQL_RANDOM_ROOT_PASSWORD=yes \
    > -d mysql/mysql-server:5.7

`{{ project_path }}` 에는 프로젝트의 최상위 디렉토리 절대경로를, `{{ data_store_dir }}` 에는 호스트 서버에서 데이터를 저장할 디렉토리 절대경로를, `{{ mysql_user }}` 와 `{{ mysql_password }}` 에는 root가 아닌 추가 계정을 입력하면 됩니다. 위 명령어를 실행하면 :dfn:`kaistusc` 이름의 database가 생성되고 입력한 계정에 해당 db의 접근권한이 생깁니다. 여기서 `{{ data_store_dir }}` 설정하는 행은 생략 가능하나, 그럴 경우 데이터가 호스트 서버가 아닌 컨테이너 안에 저장되어 관리하기가 불편할 수 있습니다.

Docker로 웹서버 구축
--------------------

Nginx_ 와 uWSGI_ 를 이용하여 Django_ 를 서비스하는 웹서버를 dockerize 시킨 내용이 :file:`Dockerfile` 에 담겨 있습니다. 해당 docker 파일을 이용해 :dfn:`kaistusc` 이름의 이미지를 생성하기 위해 아래의 명령을 입력합니다. (시간이 오래 걸릴 수 있습니다.)

.. code-block:: bash

    $ sudo docker build --tag kaistusc .

이후 실행되고 있는 DB 서버와 연동하여 실행되는 컨테이너를 생성합니다.

.. code-block:: bash

    $ sudo docker run --name kaistusc \
    > -v {{ cert_path }}:/etc/kaistusc \
    > -e PORTAL_ADMIN_ID={{ portal_admin_id }} \
    > -e PORTAL_ADMIN_PW={{ portal_admin_pw }} \
    > -e PORTAL_PUBLIC_KEY={{ portal_public_key }} \
    > --link kaistusc-db:db \
    > -p 80:80 \
    > -p 443:443 \
    > -d kaistusc

호스트 서버에서 80번, 443번 포트를 사용 중이면 컨테이너 실행을 할 수 없으므로 유의하시길 바랍니다. `{{ cert_path }}` 는 https 인증서가 위치한 절대경로이며, 해당 폴더에는 아래의 파일들이 담겨 있어야 합니다.

* :file:`fullchain.pem`
* :file:`privkey.pem`
* :file:`dhparam.pem`

:file:`dhparam.pem` 은 :program:`openssl` 을 이용하여 아래 명령어로 쉽게 생성할 수 있습니다.

.. code-block:: bash

    $ openssl dhparam -out dhparam.pem 4096

`PORTAL` 로 시작하는 세 개의 환경변수는 :dfn:`KAIST Single Auth Service 3.0` 을 설정하기 위한 인증정보입니다. `{{ portal_public_key }}` 의 경우 마지막 `==` 까지 입력해주셔야 합니다. KAIST 학교 당국으로부터 발급 받은 인증정보를 제대로 입력하셨다면, 배포환경에서 KAIST 포탈 계정으로 로그인할 수 있게 됩니다. 다만, 서비스가 등록된 서버의 443 포트에서만 허용되기 때문에 개발환경에서 테스트할 수 없을 가능성이 큽니다.

Docker 컨테이너 관리
--------------------

`kaistusc-db` 와 `kaistusc` 두 개의 컨테이너는 :command:`docker run` 을 통해 즉시 실행됩니다. 이를 종료하거나 이후 다시 시작하기 위해서는 각각 다음의 명령어를 입력하십시오.

.. code-block:: bash

    $ sudo docker stop kaistusc-db kaistusc
    $ sudo docker start kaistusc-db kaistusc

실행 중인 컨테이너의 shell에 직접 접속하려면 아래의 명령어를 입력하시면 됩니다.

.. code-block:: bash

    $ sudo docker exec -it kaistusc bash

`kaistusc-db` 의 경우도 마찬가지 방법으로 접속할 수 있습니다.

:command:`docker run` 을 통해 처음 컨테이너를 실행하셨으면 django에서 제공하는 :command:`createsuperuser` 기능을 이용하여 관리자 계정을 생성하시는 게 좋습니다.

.. code-block:: bash

    $ sudo docker exec -it kaistusc bash -c \
    > "source /app/kaistusc/venv/bin/activate \
    > && python /app/kaistusc/manage.py createsuperuser"

이후 django admin 페이지(:file:`/admin`)에 접속해 위에서 생성한 관리자 계정으로 로그인하시면 사이트에 관련된 설정을 하실 수 있습니다.

.. _Docker: https://www.docker.com/
.. __: https://pyrasis.com/book/DockerForTheReallyImpatient/Chapter02/
.. _MySQL: https://www.mysql.com/
.. _Nginx: https://www.nginx.com/resources/wiki/
.. _uWSGI: https://uwsgi-docs.readthedocs.io/en/latest/
.. _Django: https://djangoproject.com/
