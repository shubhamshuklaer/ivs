[Reference](https://www.bearfruit.org/2008/04/17/telnet-for-testing-ssl-https-websites/)

1. Http server check
        
        telnet www.somesite 80
        GET /index.html HTTP/1.1
        Host: www.somesite

(Note you need to press enter twice at the end)

2. Https server check

        openssl s_client -connect www.somesite:443
        [watch the ssl certificate details scroll by]
        GET /index.html HTTP/1.1
        Host: www.somesite

    (again you need to press enter twice)

3. Generatign self signed cert

		openssl req -x509 -newkey rsa:2048 -keyout server.pem -out server.pem -days XXX -nodes
