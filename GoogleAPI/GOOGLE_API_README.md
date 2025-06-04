# GoogleAPI
### calendar_id: str = 'primary' oznacza że to głowny kalendarz, nie wiem jak działa dla innych wartości xd
| Funkcja     | Description                                                                                                                                             | 
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| getEvents   | zwraca Eventy na podstawie argumentow, Eventy posiadają działające id                                                                                   | 
| updateEvent | aktualizuje Event  na podstawie "id", wprowadzasz Event który musi posiadać id<br>jeśli "id" się zgadza zostanie podmieniony na tą wersje którą podałeś | 
| deleteEvent | usuwa Event na podstawie Eventu któy mu podajesz, Event podany musi mieć "id" reszta nie ma znaczenia                                                   | 
| addEvent    | dodajesz Event do kalendarza, argumentem jest Event *(id jest niepotrzebne i lepiej żeby go nie było)*                                                  | 

Jak zaktualizować? - x = getEvents(*user_creds*,*...*) , x = EventBuilder(x).with_summary("po aktualizacji nazwa eventu").build(), updateEvent(*user_creds*,x)

#   Event

Event - odpowienik eventu od google, tworzenie go bez builder jest niebezpieczne

EventBuilder - tworzy obiekt Event, dodajesz do niego atrybuty poprzez funkcje, np. *x = EventBuilder.with_description('opis').with_status('confirmed').build()* . Gwarantuje że obiekt jest poprawny. 