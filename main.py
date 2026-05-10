# FEATURE: Управление пациентами - создание, редактирование, удаление
# FEATURE: Система записи на прием - расписание, услуги
"""
MedicalClinic - Учет и управление медицинской клиникой
Демонстрация ООП: абстрактные классы, наследование, композиция, агрегация,
миксины, интерфейсы, метакласс, фабрика, цепочка обязанностей,
шаблонный метод, декоратор, сериализация.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

# ------------------------- Настройка логирования -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("clinic.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MedicalClinic")

# ------------------------- 11. Исключения -------------------------
class InvalidPatientError(Exception):
    pass

class PermissionDeniedError(Exception):
    pass

class AppointmentNotFoundError(Exception):
    pass

# ------------------------- 4. Интерфейсы -------------------------
class Schedulable(ABC):
    @abstractmethod
    def schedule_appointment(self, doctor: 'Doctor', date: str) -> 'Appointment':
        pass

class Reportable(ABC):
    @abstractmethod
    def generate_report(self) -> str:
        pass

# ------------------------- 5. Миксины -------------------------
class LoggingMixin:
    def log_action(self, action: str):
        logger.info(f"[LOG] {self.__class__.__name__}: {action}")

class NotificationMixin:
    def send_notification(self, message: str):
        logger.info(f"[NOTIFICATION] {self.__class__.__name__}: {message}")
        print(f"🔔 Уведомление: {message}")

# ------------------------- 6. Метакласс PatientMeta -------------------------
class PatientMeta(type(ABC), type):
    _registry = {}
    
    def __new__(mcs, name, bases, dct):
        cls = super().__new__(mcs, name, bases, dct)
        if name not in ["Patient", "ABC"] and not name.startswith('_'):
            mcs._registry[name.lower()] = cls
        return cls
    
    @classmethod
    def get_registry(mcs) -> Dict[str, type]:
        return mcs._registry.copy()

# ------------------------- 1. Абстрактный класс Patient -------------------------
class Patient(ABC, metaclass=PatientMeta):
    def __init__(self, patient_id: str, name: str, age: int, gender: str, medical_history: str = ""):
        self._patient_id = patient_id
        self._name = name
        self._age = age
        self._gender = gender
        self._medical_history = [medical_history] if medical_history else []
    
    @property
    def patient_id(self) -> str:
        return self._patient_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str):
        self._name = value
    
    @property
    def age(self) -> int:
        return self._age
    
    @age.setter
    def age(self, value: int):
        self._age = value
    
    @property
    def gender(self) -> str:
        return self._gender
    
    @property
    def medical_history(self) -> List[str]:
        return self._medical_history.copy()
    
    def add_medical_record(self, record: str):
        self._medical_history.append(record)
        logger.info(f"Добавлена запись в историю {self._name}: {record}")
    
    @abstractmethod
    def get_medical_history(self) -> str:
        pass
    
    def __eq__(self, other):
        if not isinstance(other, Patient):
            return NotImplemented
        return self._age == other._age
    
    def __lt__(self, other):
        if not isinstance(other, Patient):
            return NotImplemented
        return self._age < other._age
    
    def __gt__(self, other):
        if not isinstance(other, Patient):
            return NotImplemented
        return self._age > other._age
    
    def __str__(self) -> str:
        return f"Пациент: {self._name}, Возраст: {self._age}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "patient_id": self._patient_id,
            "name": self._name,
            "age": self._age,
            "gender": self._gender,
            "medical_history": self._medical_history,
            "type": self.__class__.__name__.lower()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Patient':
        patient_type = data.pop("type")
        factory = PatientFactory()
        return factory.create_patient(patient_type, **data)

# ------------------------- 2. Подклассы Patient -------------------------
class AdultPatient(Patient):
    def __init__(self, patient_id: str, name: str, age: int, gender: str,
                 occupation: str, medical_history: str = ""):
        super().__init__(patient_id, name, age, gender, medical_history)
        self.occupation = occupation
    
    def get_medical_history(self) -> str:
        history = "; ".join(self._medical_history) if self._medical_history else "нет записей"
        return f"Взрослый пациент: {self._name}, Род занятий: {self.occupation}\nИстория: {history}"
    
    def __str__(self) -> str:
        return f"Взрослый пациент: {self._name}, {self._age} лет, {self.occupation}"
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["occupation"] = self.occupation
        return data

class ChildPatient(Patient):
    def __init__(self, patient_id: str, name: str, age: int, gender: str,
                 guardian: str, medical_history: str = ""):
        super().__init__(patient_id, name, age, gender, medical_history)
        self.guardian = guardian
    
    def get_medical_history(self) -> str:
        history = "; ".join(self._medical_history) if self._medical_history else "нет записей"
        return f"Ребенок: {self._name}, Опекун: {self.guardian}\nИстория: {history}"
    
    def __str__(self) -> str:
        return f"Ребенок: {self._name}, {self._age} лет, Опекун: {self.guardian}"
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["guardian"] = self.guardian
        return data

class SeniorPatient(Patient):
    def __init__(self, patient_id: str, name: str, age: int, gender: str,
                 chronic_conditions: str, medical_history: str = ""):
        super().__init__(patient_id, name, age, gender, medical_history)
        self.chronic_conditions = chronic_conditions
    
    def get_medical_history(self) -> str:
        history = "; ".join(self._medical_history) if self._medical_history else "нет записей"
        return f"Пожилой пациент: {self._name}, Хронические заболевания: {self.chronic_conditions}\nИстория: {history}"
    
    def __str__(self) -> str:
        return f"Пожилой пациент: {self._name}, {self._age} лет, Хроника: {self.chronic_conditions}"
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["chronic_conditions"] = self.chronic_conditions
        return data

# ------------------------- 7. Фабрика PatientFactory -------------------------
class PatientFactory:
    @staticmethod
    def create_patient(patient_type: str, **kwargs) -> Patient:
        registry = PatientMeta.get_registry()
        patient_type = patient_type.lower()
        if patient_type not in registry:
            raise InvalidPatientError(f"Неизвестный тип пациента: {patient_type}")
        return registry[patient_type](**kwargs)

# ------------------------- 3. Композиция и агрегация -------------------------
class Doctor:
    def __init__(self, doctor_id: str, name: str, specialty: str, phone: str):
        self.doctor_id = doctor_id
        self.name = name
        self.specialty = specialty
        self.phone = phone
    
    def __str__(self) -> str:
        return f"Доктор: {self.name}, {self.specialty}"
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "doctor_id": self.doctor_id,
            "name": self.name,
            "specialty": self.specialty,
            "phone": self.phone
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'Doctor':
        return cls(data["doctor_id"], data["name"], data["specialty"], data["phone"])

class Service:
    def __init__(self, name: str, cost: float):
        self.name = name
        self.cost = cost
    
    def __str__(self) -> str:
        return f"{self.name}: {self.cost} руб."

class Appointment(LoggingMixin, NotificationMixin, Schedulable, Reportable):
    def __init__(self, appointment_id: str, patient: Patient, doctor: Doctor, date: str):
        self.appointment_id = appointment_id
        self.patient = patient
        self.doctor = doctor
        self.date = date
        self.diagnosis = ""
        self.prescription = ""
        self.services: List[Service] = []
    
    def add_service(self, service: Service):
        self.services.append(service)
        self.log_action(f"Добавлена услуга {service.name} к приему {self.appointment_id}")
    
    def remove_service(self, service_name: str):
        self.services = [s for s in self.services if s.name != service_name]
        self.log_action(f"Удалена услуга {service_name} из приема {self.appointment_id}")
    
    def calculate_total(self) -> float:
        return sum(s.cost for s in self.services)
    
    def schedule_appointment(self, doctor: Doctor, date: str) -> 'Appointment':
        self.doctor = doctor
        self.date = date
        self.send_notification(f"Прием {self.appointment_id} запланирован на {date} к {doctor.name}")
        return self
    
    def generate_report(self) -> str:
        services_str = ", ".join([s.name for s in self.services])
        total = self.calculate_total()
        return (f"Отчет по приему {self.appointment_id}:\n"
                f"  Пациент: {self.patient.name}\n"
                f"  Врач: {self.doctor.name}\n"
                f"  Дата: {self.date}\n"
                f"  Диагноз: {self.diagnosis}\n"
                f"  Рецепт: {self.prescription}\n"
                f"  Услуги: {services_str}\n"
                f"  Итого: {total} руб.")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "appointment_id": self.appointment_id,
            "patient_id": self.patient.patient_id,
            "doctor": self.doctor.to_dict(),
            "date": self.date,
            "diagnosis": self.diagnosis,
            "prescription": self.prescription,
            "services": [{"name": s.name, "cost": s.cost} for s in self.services]
        }

# ------------------------- 8. Цепочка обязанностей -------------------------
class DiagnosisChangeRequest:
    def __init__(self, patient: Patient, old_diagnosis: str, new_diagnosis: str, reason: str):
        self.patient = patient
        self.old_diagnosis = old_diagnosis
        self.new_diagnosis = new_diagnosis
        self.reason = reason
        self.approved = False
        self.approved_by = None

class DiagnosisHandler(ABC):
    def __init__(self):
        self._next_handler = None
    
    def set_next(self, handler):
        self._next_handler = handler
        return handler
    
    def handle(self, request: DiagnosisChangeRequest):
        if self.can_approve(request):
            request.approved = True
            request.approved_by = self.__class__.__name__
            print(f"✅ {self.__class__.__name__} одобрил изменение диагноза для {request.patient.name}")
            logger.info(f"Изменение диагноза одобрено: {request.patient.name} -> {request.new_diagnosis}")
        elif self._next_handler:
            self._next_handler.handle(request)
        else:
            print(f"❌ Изменение диагноза отклонено для {request.patient.name}")
    
    @abstractmethod
    def can_approve(self, request: DiagnosisChangeRequest) -> bool:
        pass

class DoctorHandler(DiagnosisHandler):
    def can_approve(self, request: DiagnosisChangeRequest) -> bool:
        return len(request.new_diagnosis) - len(request.old_diagnosis) < 20

class DepartmentHeadHandler(DiagnosisHandler):
    def can_approve(self, request: DiagnosisChangeRequest) -> bool:
        return len(request.reason) > 10

class ChiefPhysicianHandler(DiagnosisHandler):
    def can_approve(self, request: DiagnosisChangeRequest) -> bool:
        return True

# ------------------------- 9. Шаблонный метод -------------------------
class AppointmentProcess(ABC):
    def schedule_appointment(self, patient: Patient, doctor: Doctor, date: str) -> Appointment:
        self.check_doctor_availability(doctor, date)
        appointment = self.create_appointment(patient, doctor, date)
        self.confirm_appointment(appointment)
        return appointment
    
    @abstractmethod
    def check_doctor_availability(self, doctor: Doctor, date: str):
        pass
    
    @abstractmethod
    def create_appointment(self, patient: Patient, doctor: Doctor, date: str) -> Appointment:
        pass
    
    @abstractmethod
    def confirm_appointment(self, appointment: Appointment):
        pass

class OnlineAppointmentProcess(AppointmentProcess):
    def check_doctor_availability(self, doctor: Doctor, date: str):
        print(f"🔍 Проверка онлайн: доктор {doctor.name} свободен {date}")
    
    def create_appointment(self, patient: Patient, doctor: Doctor, date: str) -> Appointment:
        appointment_id = f"ONL_{patient.patient_id}_{date.replace('-', '')}"
        appointment = Appointment(appointment_id, patient, doctor, date)
        print(f"💻 Онлайн-запись создана: {appointment_id}")
        return appointment
    
    def confirm_appointment(self, appointment: Appointment):
        appointment.send_notification(f"Ваша онлайн-запись на {appointment.date} подтверждена")

class OfflineAppointmentProcess(AppointmentProcess):
    def check_doctor_availability(self, doctor: Doctor, date: str):
        print(f"🏥 Проверка в регистратуре: доктор {doctor.name} принимает {date}")
    
    def create_appointment(self, patient: Patient, doctor: Doctor, date: str) -> Appointment:
        appointment_id = f"OFF_{patient.patient_id}_{date.replace('-', '')}"
        appointment = Appointment(appointment_id, patient, doctor, date)
        print(f"📋 Офлайн-запись создана: {appointment_id}")
        return appointment
    
    def confirm_appointment(self, appointment: Appointment):
        print(f"✅ Запись {appointment.appointment_id} подтверждена в регистратуре")

# ------------------------- 10. Декоратор прав доступа -------------------------
def check_permissions(required_role: str = "doctor"):
    def decorator(func):
        def wrapper(user_role: str, *args, **kwargs):
            if user_role != required_role and user_role != "admin":
                raise PermissionDeniedError(f"Требуется роль '{required_role}', у вас '{user_role}'")
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ------------------------- Клиника (управление данными) -------------------------
class MedicalClinic:
    def __init__(self):
        self.patients: Dict[str, Patient] = {}
        self.appointments: Dict[str, Appointment] = {}
        self.doctors: Dict[str, Doctor] = {}
    
    def add_patient(self, patient: Patient):
        self.patients[patient.patient_id] = patient
        logger.info(f"Добавлен пациент: {patient.name}")
    
    def remove_patient(self, patient_id: str):
        if patient_id in self.patients:
            del self.patients[patient_id]
            logger.info(f"Удален пациент {patient_id}")
    
    def get_all_patients(self) -> List[Patient]:
        return list(self.patients.values())
    
    def search_by_name(self, name: str) -> List[Patient]:
        return [p for p in self.patients.values() if name.lower() in p.name.lower()]
    
    def add_doctor(self, doctor: Doctor):
        self.doctors[doctor.doctor_id] = doctor
    
    def add_appointment(self, appointment: Appointment):
        self.appointments[appointment.appointment_id] = appointment
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "patients": [p.to_dict() for p in self.patients.values()],
            "doctors": [d.to_dict() for d in self.doctors.values()],
            "appointments": [a.to_dict() for a in self.appointments.values()]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MedicalClinic':
        clinic = cls()
        for p_data in data.get("patients", []):
            patient = PatientFactory.create_patient(p_data["type"], **{k: v for k, v in p_data.items() if k != "type"})
            clinic.add_patient(patient)
        for d_data in data.get("doctors", []):
            doctor = Doctor.from_dict(d_data)
            clinic.add_doctor(doctor)
        return clinic

# ------------------------- ТЕСТ -------------------------
if __name__ == "__main__":
    # Принудительная регистрация типов пациентов
    PatientMeta._registry["adult"] = AdultPatient
    PatientMeta._registry["child"] = ChildPatient
    PatientMeta._registry["senior"] = SeniorPatient
    
    print("=" * 60)
    print("МЕДИЦИНСКАЯ КЛИНИКА - ТЕСТ")
    print("=" * 60)
    
    try:
        # Создание пациентов через фабрику
        factory = PatientFactory()
        adult = factory.create_patient("adult", patient_id="P001", name="Иван Петров", 
                                       age=35, gender="М", occupation="Инженер")
        child = factory.create_patient("child", patient_id="P002", name="Маша Иванова",
                                       age=8, gender="Ж", guardian="Елена Иванова")
        senior = factory.create_patient("senior", patient_id="P003", name="Анна Смирнова",
                                        age=72, gender="Ж", chronic_conditions="Гипертония")
        
        # Доктора
        doctor = Doctor("D001", "Алексей Сидоров", "Терапевт", "+7(999)123-45-67")
        
        # Клиника
        clinic = MedicalClinic()
        clinic.add_patient(adult)
        clinic.add_patient(child)
        clinic.add_patient(senior)
        clinic.add_doctor(doctor)
        
        print("\n--- Пациенты ---")
        print(adult)
        print(child)
        print(senior)
        
        # Медицинская история
        print("\n--- Медицинская история ---")
        adult.add_medical_record("Грипп, 2024")
        print(adult.get_medical_history())
        print(child.get_medical_history())
        print(senior.get_medical_history())
        
        # Сравнение пациентов
        print(f"\nadult > child? {adult > child}")
        
        # Запись на прием (шаблонный метод)
        print("\n--- Запись на прием (шаблонный метод) ---")
        online_process = OnlineAppointmentProcess()
        appointment = online_process.schedule_appointment(adult, doctor, "2025-05-20")
        appointment.diagnosis = "ОРВИ"
        appointment.prescription = "Отдых, теплое питье"
        clinic.add_appointment(appointment)
        
        # Услуги (агрегация)
        service1 = Service("Анализ крови", 1500)
        service2 = Service("УЗИ", 3000)
        appointment.add_service(service1)
        appointment.add_service(service2)
        
        # Отчет
        print("\n--- Отчет о приеме ---")
        print(appointment.generate_report())
        
        # Цепочка обязанностей
        print("\n--- Цепочка обязанностей (изменение диагноза) ---")
        request = DiagnosisChangeRequest(adult, "ОРВИ", "Пневмония", "Рентген показал затемнение")
        doc = DoctorHandler()
        dept = DepartmentHeadHandler()
        chief = ChiefPhysicianHandler()
        doc.set_next(dept).set_next(chief)
        doc.handle(request)
        
        # Декоратор прав
        print("\n--- Декоратор прав ---")
        @check_permissions("admin")
        def delete_patient(patient_id: str):
            print(f"Пациент {patient_id} удален")
        
        delete_patient("admin", "P001")
        try:
            delete_patient("nurse", "P001")
        except PermissionDeniedError as e:
            print(f"Ошибка прав: {e}")
        
        # Сериализация
        print("\n--- Сериализация в JSON ---")
        clinic_data = clinic.to_dict()
        print(json.dumps(clinic_data, ensure_ascii=False, indent=2))
        
        print("\n✅ ВСЕ МОДУЛИ РАБОТАЮТ!")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()