from src.logging import logging
from src.exception import CustomException
from src.constants.supabase import SUPABASE_KEY, SUPABASE_URL

from supabase import create_client, Client


class SupabaseConnection:
    def __init__(self):
        try:
            self.supabase_url = SUPABASE_URL
            self.supabase_key = SUPABASE_KEY
            self.supabase: Client = None

        except Exception as e:
            raise CustomException(
                f"Error initializing SupabaseConnection: {str(e)}")

    def connect(self):
        """
        Establishes a connection to Supabase and returns the client.
        """
        try:
            if not self.supabase_url or not self.supabase_key:
                raise ValueError("Supabase URL and Key must be set.")

            self.supabase = create_client(self.supabase_url, self.supabase_key)
            logging.info("Connected to Supabase successfully!")
            return self.supabase

        except Exception as e:
            logging.error(f"Error connecting to Supabase: {e}")
            raise CustomException(f"Error connecting to Supabase: {str(e)}")
