import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_database():
    """
    DANGEROUS: Drops all tables by running alembic downgrade base,
    then upgrades to head, and seeds the database.
    DO NOT USE IN PRODUCTION.
    """
    logger.warning("WARNING: Resetting the database. DO NOT USE IN PRODUCTION.")
    
    try:
        # Step 1: Downgrade to base (drops all tables)
        logger.info("Downgrading database to base...")
        subprocess.run(["alembic", "downgrade", "base"], check=True)
        
        # Step 2: Upgrade to head (recreates all tables)
        logger.info("Upgrading database to head...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        
        # Step 3: Seed data
        logger.info("Seeding database...")
        subprocess.run(["python", "-m", "scripts.seed_database"], check=True)
        
        logger.info("Database reset successfully completed.")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error resetting database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    reset_database()
