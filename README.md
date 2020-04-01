# Aviata

**Objective:** Backend developer position

## Task

Test task was send by HR manager in _docx_ file _(in current repository)_

**Date:** January 24, 2020

**Deadline:** 2-3 days

**Submission type:** this repository

## Review and Rework

Review was done by one of leaders of product teams in Aviata

> Есть пустые модули в проекте: admin.py, models.py, tests.py. 
> Не надо их создовать если они не нужны.

* Delete unused files

> Не соблюдается некоторые нормы и рекомендации PEP8

* Fix all indentations with **PEP8**

> View для отображения офферов назван search_ticket, название не подходит по смыслу.

* Rename **FBV**

> Не использованы формы (django forms)

* ...

> В ответе (response) от View, есть статус 'status': 'OK', что является лишним, 
> можно использовать статусы HTTP (200, 404 и т.д)

* Remove fields status, add status codes _(200, 400, 404 etc)_

> Неэффективное хранения офферов в кэше, можно было использовать такую структуру 
> {date}_{route} (например: '01-01-2020_ALATSE') тогда код в View был бы примерно таким:

```
cache_key = f'{date}_{fly_from}{fly_to}'
offers = cache.get(cache_key)

if offers:
  return JsonResponse({'offers': offers})

return JsonResponse({'message': 'Offers not found'}, status=404)
```

* Reconstruct cache structure

> В модуле tasks.py используется cache из djcelery.backends.cache, 
> когда у django есть свой cache

* Import _django.core.cache_

> При каждом запуске задачи search_tickets, сбрасывается весь кэш. 
> Это неправильно, что если есть (будут) другие данные, не относящиеся к офферам, 
> они также будут сброшаны. Лучше использовать таймауты при записи данных в кэш 
> или удалять по ключам.

* Add timeout for cache save

> Нету таймаутов между запросами на сторонний API. Это неправильно, 
> так мы нагружаем этот ресурс, нам могут ограничить доступ к этому ресурсу.

* Add timeout for requesting

> Много где в коде есть принты (print) и другие вещи, для дебагинга и разработки 
> можно использовать, но отправлять код на ревью с ними нельзя.

* Remove all prints

> В каждом цикле, для каждого направления формируются одинаковые даты для поиска, 
> лучше сформировать их один раз.

* Remove unnecessary intermediate function

> Данные из стороннего API, дублируется в двух переменных. (Зачем?):
  
```
data = response.json().get('data')
...
tickets = response.json().get('data')
```

* Remove unnecessary variables

> Неэффективное использование кэша в tasks.py, рушится атомарность.

* Save cache atomically

## Conclusion

Done all reworks except **django forms**

Interesting task which gives simple understanding how Aviata services work