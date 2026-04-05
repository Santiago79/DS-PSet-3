"""
Implementación concreta del EventBus en la capa de infraestructura.
Usa una lista simple de observadores para mantener el patrón Observable.
"""

from typing import List
from backend.domain.events import Evento
from backend.domain.interfaces.event_bus import EventBus
from backend.domain.interfaces.observador_evento import ObservadorEvento


class InMemoryEventBus(EventBus):
    """Implementación en memoria del bus de eventos"""
    
    def __init__(self):
        self._observers: List[ObservadorEvento] = []
    
    def subscribe(self, observador: ObservadorEvento) -> None:
        """Suscribe un observador al bus"""
        if observador not in self._observers:
            self._observers.append(observador)
    
    def unsubscribe(self, observador: ObservadorEvento) -> None:
        """Desuscribe un observador del bus"""
        if observador in self._observers:
            self._observers.remove(observador)
    
    def publish(self, evento: Evento) -> None:
        """Publica un evento a todos los observadores suscritos"""
        for observador in self._observers:
            observador.on_event(evento)
