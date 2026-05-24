from app.database import SessionLocal
from app.services.seed import seed_reference_data


def main() -> None:
    with SessionLocal() as session:
        result = seed_reference_data(session)
    print("Seed completed:", result)


if __name__ == "__main__":
    main()

