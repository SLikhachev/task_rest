# TODO 2024

## Внесение в январь талонов в декабре предыдущего года

Вносим в декабре часть оставшихся талонов в январь следующего года. В настоящее время JS приложение
не доработатано, если выбрать следующий год в приложении "Клиника", вносить талоны не получится.

## Формирование реестров в январе текущего года за декабрь предыдущего

Если за декабрь остались МЭКи, исправляем и подаем их в январе отдельным пакетом. Атрибуты пакетов
должны быть этого года, а сами случаи прошлого. В формировании пакетов выбираем декабрь предыдущего,
чтобы случаи выбирались из прошлогодней таблицы. Нужно сделать и протестировать.

## Сделать проверку пола пациента

Для проверки пола, сравниваем имя пациента с выборкой из таблицы имен. Сделать таблицу мужских имен.
Проверка производится только в задаче проверки пакетовю Если не исправлено, то при реальном формировании
оставляем так как есть.

## Обновление тарифов на услуги

При появлении новых тарифов по взаимроасчетам, обновляем таблицу **traifs_pmu_vzaimoras**.
В начтоящее время задача написана и работает (не забыть тримминг из файла csv), но обновление производится в
режиме тестирования вручную.

Можно сделать дополнительный пункт меню в приложении Справочники -> Тарифы
для автоматизации этого дела. Но можно и не делать.

