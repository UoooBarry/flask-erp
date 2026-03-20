from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import MappedAsDataclass, DeclarativeBase
from flask_jwt_extended import JWTManager
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, func


class Base(MappedAsDataclass, DeclarativeBase):
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, server_default=func.now(), init=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        init=False,
    )

    pass


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
jwt = JWTManager()
