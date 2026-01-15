from model import Base, engine

# This line is the "Table Builder"
# It looks at your User, Address, Portfolio, and Transaction classes and builds them in MariaDB
print("Building tables...")
Base.metadata.create_all(bind=engine)
print("Tables 'user', 'address', 'portfolio', and 'transactions' are now live in finance_app!")

