"""Fórmulas estáveis para fila M/M/1 no regime estacionário."""
from dataclasses import dataclass

@dataclass(frozen=True)
class MM1:
    arrival_rate:float
    service_rate:float
    def __post_init__(self)->None:
        if not 0<=self.arrival_rate<self.service_rate: raise ValueError("requer 0 <= λ < μ")
    @property
    def utilization(self)->float:return self.arrival_rate/self.service_rate
    @property
    def expected_system_size(self)->float:return self.arrival_rate/(self.service_rate-self.arrival_rate)
    @property
    def expected_queue_size(self)->float:return self.arrival_rate**2/(self.service_rate*(self.service_rate-self.arrival_rate))
    @property
    def expected_system_time(self)->float:return 1/(self.service_rate-self.arrival_rate)
    @property
    def expected_wait_time(self)->float:return self.arrival_rate/(self.service_rate*(self.service_rate-self.arrival_rate))
    def stationary_probability(self,count:int)->float:
        if not isinstance(count,int) or count<0: raise ValueError("contagem inválida")
        rho=self.utilization;return (1-rho)*rho**count

__all__=["MM1"]
