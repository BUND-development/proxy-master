# Ultimate proxy master
ver 1.3.2  


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
### А в коде поменять что можно?  
#### В settings.ini:  
Менять на `true` или `false` (По дефолту `true` если не сказано обратного)  
`PARSE` - парсить ли прокси  
`SUBNETS` - использовать блеклист подсетей  
`BLACKLIST` - использовать блеклист айпи  
`COUNTRIES` - использовать фильтрование по странам  
`CHECK` - проверять ли прокси вообще  
`CHECKON2CH` - проверять ли кроме рабоспособность бан  
`PROTOCOLOUT` - выводит прокси специально для вайпалки (пример: http://1.23.34.56:789)  
**Далее идут более тонкие настройки, пердолить с умом:**    
`FILENAME_EXPORT` - имя файла, который будет содержать прокси на выходе  
`NORMALINPUT` - вводить ли через аргументы протокол. `false` по дефолту  
`BOARD` - доска на дваче.хэка куда будут отправляться репорты  
`MAXTRIES` - количество попыток подключений к прокси  
`TIMEOUT` - время в секундах ожидания ответа от сервера (НЕ ВСЕГО ЗАПРОСА, А ОТВЕТА ОТ СЕРВЕРА!)  
`THREADS_MULTIPLIER` - количество потоков (я использую multiprocessing для обхода GIL), ставить желательно четно количеству ядер в вашем цопе  
`WEBFORPING` - веб-сайт, который будет пинговаться. Сайты с защитой клоудфары не будут работать!!!  


В модулях тоже есть, что поковырять, но не сильно это существенно. В общем можете полазить, главное не сломайте.  
По всем вопросам/багам/предложениям писать BUND-development@protonmail.com  
