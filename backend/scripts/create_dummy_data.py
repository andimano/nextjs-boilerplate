import asyncio
from backend.database import AsyncSessionLocal, engine, Base
from backend.models import Admin, Employee
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_dummy_data():
    async with AsyncSessionLocal() as session:
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Create dummy admin
        admin = Admin(
            email="admin@example.com",
            hashed_password=pwd_context.hash("adminpassword")
        )
        session.add(admin)

        # Create dummy employees
        employees = [
            Employee(nip="123456", name="John Doe", hashed_password=pwd_context.hash("password1")),
            Employee(nip="654321", name="Jane Smith", hashed_password=pwd_context.hash("password2")),
        ]
        session.add_all(employees)

        await session.commit()
        print("Dummy data created successfully.")

if __name__ == "__main__":
    asyncio.run(create_dummy_data())
