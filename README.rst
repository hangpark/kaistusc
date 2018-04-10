KAIST USC: KAIST Undergraduate Student Council Website on Django
================================================================

Welcome to **KAIST USC**!

**KAIST USC** is the open source project to construct `KAIST Undergraduate Student Council Website`_ on `Django`_ to make memebers participate in USC well. This project includes front-ent and back-end sources with a production enviornment settings by using `Docker`_.


Deploy
------

Go to 4) if you are updating already deployed one.

1) Install certbot and get letsencrypt certbot.

2) Write proxy server setting in the host. (SSL, proxypass to the port binded on the docker service "web")

3) Go to project root and write .env file as follows:

    MYSQL_USER=username

    MYSQL_PASSWORD=password

    MYSQL_DATABASE=database

    MYSQL_RANDOM_ROOT_PASSWORD=yes

    PORTAL_ADMIN_ID=portal_id

    PORTAL_ADMIN_PW=portal_password

    PORTAL_PUBLIC_KEY=portal_public_key

    CERT_PATH=/path/to/letsencrypt/cert
    
4) serveruser:/root/of/project $ **docker-compose up -d --build**


Website
-------

Available at https://student.kaist.ac.kr/


Documentation
-------------

See https://hangpark.github.io/kaistusc/ (Korean)

or https://student.kaist.ac.kr/docs/ (Korean)


.. _`KAIST Undergraduate Student Council Website`: https://student.kaist.ac.kr/
.. _Django: https://djangoproject.com/
.. _Docker: https://www.docker.com/
