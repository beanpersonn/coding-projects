from database import Base, engine
import models

def init_database():
    print("Creating database...")

    Base.metadata.create_all(bind=engine)

    print("Database created successfully.")

if __name__ == "__main__":
    init_database()