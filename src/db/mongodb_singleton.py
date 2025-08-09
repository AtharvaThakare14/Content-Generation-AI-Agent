import sys
import os
import time
from typing import Dict, Any

from src.logging import logging
from src.constants.mongodb import *
from src.exception import CustomException
from src.configurations.mongodb import MongoDBConnection


class MongoDBSingleton:
    """
    Singleton class for MongoDB connection optimized for serverless environments.
    Implements connection pooling and handles reconnection for serverless functions.
    """
    _instance = None
    _initialized = False
    _last_connection_time = 0
    _connection_ttl = 60  # Time in seconds before checking connection

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBSingleton, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Initialize connection if not initialized or if connection is stale
        current_time = time.time()
        if not self._initialized or (current_time - self._last_connection_time) > self._connection_ttl:
            try:
                logging.info("Initializing MongoDB connection for serverless environment")
                self.mongodb_client = MongoDBConnection(database_name=AI_TUTOR_IQAN_DATABASE_NAME)
                
                # Initialize all collections
                self.domain_collection = self.mongodb_client.db[DOMAIN_COLLECTION_NAME]
                self.courses_collection = self.mongodb_client.db[COURSES_COLLECTION_NAME]
                self.modules_collection = self.mongodb_client.db[MODULES_COLLECTION_NAME]
                self.lessons_collection = self.mongodb_client.db[LESSONS_COLLECTION_NAME]
                self.on_demand_domains_collection = self.mongodb_client.db[ON_DEMAND_DOMAINS_ANALYSIS]
                self.segments_collection = self.mongodb_client.db[SEGMENTS_COLLECTION_NAME]
                self.combined_courses_collection = self.mongodb_client.db[COMBINED_COURSES_COLLECTION_NAME]
                
                # Update the initialization state and timestamp
                self._initialized = True
                self._last_connection_time = current_time
                logging.info("MongoDB connection initialized successfully")
            except Exception as e:
                logging.error(f"Error initializing MongoDB connection: {str(e)}")
                raise CustomException(e, sys)

    @property
    def client(self):
        """Get the MongoDB client instance"""
        return self.mongodb_client

    @property
    def db(self):
        """Get the MongoDB database instance"""
        return self.mongodb_client.db


# Create a global instance that can be imported and used across the application
mongodb = MongoDBSingleton()
