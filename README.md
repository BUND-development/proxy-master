# Ultimate proxy master
ver 1.4.4  
Исправлены баги и критические ошибки. Добавлена возможность проверки стран через 2ip  
## Что это такое?
Это программа для парсинга, обработки, и фильтрации проксей. Она парсит прокси с разных сайтов и выкачивает оттуда архивы с проксями. Далее удаляет повторы и несуществующие прокси, удаляет прокси из введеных подсетей, стран, или конкретно заблокированных айпи, проверяет на наличие банов и выдает (при желании можно проверять обычным пингованием). Так же сам скрипт можно модифицировать, но об этом ниже.  (Добавлять страны в блеклист можно через подсети или через сами названия стран)  

## Как запускать?
1. Заходим на `https://www.python.org/` и ставим питон   
2. Запускаем `python main.py` или если 2 питона `python3 main.py`  
3. Ждем, прогресс можно наблюдать в выводах консоли  
4. Берем готовый продукт из `proxies.txt`, забаненные прокси в `banned.txt`, мертвые прокси в `died.txt`  

## Как настроить под себя?  
**АТЕНШН!** По дефолту все работает изкоробки! Настраивать не обязательно!  
В папке **texts** находятся файлы для фильтров  
`subnets.txt` - файл содержит в себе записи о подсетях в CIDR формате (пример: `0.0.0.0/8`), скрипт удаляет все прокси из этих подсетей  
`blacklist.txt` - файл содержит в себе айпи, которые скрипт будет убирать  
`input-proxies.txt` - сюда вы можете по желанию загрузить уже имеющиеся прокси  
`countries.txt` - сюда вписывать страны, айпи из которых будет убирать скрипт, уже стоит свежая база данных. Но при желании можно погуглить базы для `pygeoip`, которых много. Страны вписывать на английском с большой буквы.  
`ASN.txt` - сюда вписывать ASN номер провайдера, айпи которого будут удаляться. Это гораздол легче тонны подсетей. пример формата для вписывания: `AS16276` . По дефолт уже лежат ASN провайдеры, чьи айпи заблокированы на сосаче. [Что это такое?](https://ru.wikipedia.org/wiki/%D0%90%D0%B2%D1%82%D0%BE%D0%BD%D0%BE%D0%BC%D0%BD%D0%B0%D1%8F_%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%B0_(%D0%98%D0%BD%D1%82%D0%B5%D1%80%D0%BD%D0%B5%D1%82))  
### А в коде поменять что можно?  
#### В settings.ini:  
Менять на `true` или `false` (По дефолту `true` если не сказано обратного)  
`PARSE` - парсить ли прокси  
`SUBNETS` - использовать блеклист подсетей  
`BLACKLIST` - использовать блеклист айпи  
`COUNTRIES` - использовать фильтрование по странам по юзер геобазе, по дефолту `false`  
`CHECK` - проверять ли прокси вообще  
`CHECKON2CH` - проверять ли кроме рабоспособность бан  
`PROTOCOLOUT` - выводит прокси специально для вайпалки (пример: http://1.23.34.56:789)  
`CHECK_ADVANCED` - фильтровать ли прокси по ASN провайдера. [Что это такое?](https://ru.wikipedia.org/wiki/%D0%90%D0%B2%D1%82%D0%BE%D0%BD%D0%BE%D0%BC%D0%BD%D0%B0%D1%8F_%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%B0_(%D0%98%D0%BD%D1%82%D0%B5%D1%80%D0%BD%D0%B5%D1%82))  
`CHECK2IP` - фильтровать страны через 2ip.ru. Зачем? У них самая похожая база на сосачевскую. По дефолту `false`  
**Настройка 2ip**  
***ЗАПРОСЫ К 2ip ИДУТ НЕ ЧЕРЕЗ ПРОКСИ! ВАШ АЙПИ БУДЕТ ВИДЕН САЙТУ 2ip.ru***  
`2IPTOKEN` - ваш токент из личного кабинета в 2ip. Да, регистрация там по инвайту.  
`UNKNOWNOUT` - не убирать айпи с неизвестными странами  
`FILTERING_THREADS` - треды для фильтрования. Запросы к 2ip не используют прокси, поэтому много потоков = большая нагрузка на сеть  
**Далее идут более тонкие настройки, пердолить с умом:**    
`FILENAME_EXPORT` - имя файла, который будет содержать прокси на выходе  
`NORMALINPUT` - вводить ли через аргументы протокол. `false` по дефолту  
`BOARD` - доска на дваче.хэка куда будут отправляться репорты  
`MAXTRIES` - количество попыток подключений к прокси  
`TIMEOUT` - время в секундах ожидания ответа от сервера (НЕ ВСЕГО ЗАПРОСА, А ОТВЕТА ОТ СЕРВЕРА!)  
`THREADS_MULTIPLIER` - количество потоков (я использую multiprocessing для обхода GIL), ставить желательно четно количеству ядер в вашем цопе  
`WEBFORPING` - веб-сайт, который будет пинговаться. Сайты с защитой клоудфары не будут работать!!!  
`PARSE_THREADS` - количество потоков для парсинга проксей, слишком много не рекомендуется ставить. Из-за медленного интернета на больших потоках будут проблемы со скачиванием.  
`SAME_FILTERING` - удалять ли прокси, с одинаковыми айпи. Т.е. из кучи проксей с одинаковыми айпи и разными портами будет в итоге 1 прокси. Полезно во многих делах, советуем не вырубать.  


В модулях тоже есть, что поковырять, но не сильно это существенно. В общем можете полазить, главное не сломайте.  
По всем вопросам/багам/предложениям писать BUND-development@protonmail.com  

