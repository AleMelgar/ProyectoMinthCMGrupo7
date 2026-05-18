from datetime import datetime, date
from sqlalchemy import Integer, String, Float, Text, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class EvaluationPeriod(Base):
    __tablename__ = "evaluation_periods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(200))
    periodo: Mapped[str] = mapped_column(String(20))  # Q1, Q2, Q3, Q4, Anual
    fecha_inicio: Mapped[date] = mapped_column(Date)
    fecha_fin: Mapped[date] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(20), default="borrador")  # borrador, activo, cerrado
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    forms: Mapped[list["EvaluationForm"]] = relationship(back_populates="period", cascade="all, delete-orphan")
    goals: Mapped[list["EmployeeGoal"]] = relationship(back_populates="period", cascade="all, delete-orphan")


class EvaluationForm(Base):
    __tablename__ = "evaluation_forms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    period_id: Mapped[int] = mapped_column(Integer, ForeignKey("evaluation_periods.id"))
    nombre: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    escala_min: Mapped[int] = mapped_column(Integer, default=1)
    escala_max: Mapped[int] = mapped_column(Integer, default=5)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    period: Mapped["EvaluationPeriod"] = relationship(back_populates="forms")
    sections: Mapped[list["FormSection"]] = relationship(back_populates="form", cascade="all, delete-orphan")
    assignments: Mapped[list["FormAssignment"]] = relationship(back_populates="form", cascade="all, delete-orphan")
    kpi_records: Mapped[list["KPIRecord"]] = relationship(back_populates="form", cascade="all, delete-orphan")
    results: Mapped[list["EvaluationResult"]] = relationship(back_populates="form", cascade="all, delete-orphan")


class FormSection(Base):
    __tablename__ = "form_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    form_id: Mapped[int] = mapped_column(Integer, ForeignKey("evaluation_forms.id"))
    nombre: Mapped[str] = mapped_column(String(200))
    peso: Mapped[float] = mapped_column(Float)  # porcentaje, suma = 100
    orden: Mapped[int] = mapped_column(Integer, default=0)

    form: Mapped["EvaluationForm"] = relationship(back_populates="sections")


class FormAssignment(Base):
    __tablename__ = "form_assignments"
    __table_args__ = (UniqueConstraint("form_id", "employee_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    form_id: Mapped[int] = mapped_column(Integer, ForeignKey("evaluation_forms.id"))
    employee_id: Mapped[str] = mapped_column(String(100))
    asignado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    form: Mapped["EvaluationForm"] = relationship(back_populates="assignments")


class EmployeeGoal(Base):
    __tablename__ = "employee_goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[str] = mapped_column(String(100))  # ID en MintHCM
    period_id: Mapped[int] = mapped_column(Integer, ForeignKey("evaluation_periods.id"))
    descripcion: Mapped[str] = mapped_column(Text)
    objetivo_okr: Mapped[str] = mapped_column(Text)
    peso: Mapped[float] = mapped_column(Float)  # % de peso en evaluación
    progreso: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    fecha_limite: Mapped[date] = mapped_column(Date)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    period: Mapped["EvaluationPeriod"] = relationship(back_populates="goals")


class KPIRecord(Base):
    __tablename__ = "kpi_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[str] = mapped_column(String(100))
    form_id: Mapped[int] = mapped_column(Integer, ForeignKey("evaluation_forms.id"))
    kpi_nombre: Mapped[str] = mapped_column(String(200))
    valor_actual: Mapped[float] = mapped_column(Float)
    valor_meta: Mapped[float] = mapped_column(Float)
    porcentaje: Mapped[float] = mapped_column(Float)  # (actual/meta)*100
    calculado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    form: Mapped["EvaluationForm"] = relationship(back_populates="kpi_records")


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[str] = mapped_column(String(100))
    form_id: Mapped[int] = mapped_column(Integer, ForeignKey("evaluation_forms.id"))
    puntaje_total: Mapped[float] = mapped_column(Float, default=0.0)
    comentarios: Mapped[str | None] = mapped_column(Text, nullable=True)
    evaluador_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fecha_evaluacion: Mapped[date] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")  # pendiente, completado, aprobado
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    form: Mapped["EvaluationForm"] = relationship(back_populates="results")
