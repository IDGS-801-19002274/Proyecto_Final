import os
import openai_secret_manager

class DevelopmentConfig() :
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://zamora:zamora@127.0.0.1/zamoranos'
    SQLALCHEMY_TRACK_MODIFICATION = False
    SECRET_KEY = 'MY_SECRET_KEY'
    SESSION_COOKIE_SECURE = False

class Config(object):
    SECRET_KEY = 'MY_SECRET_KEY'
    SESSION_COOKIE_SECURE = False

config = {
    'development' : DevelopmentConfig
}

class OpenAIConfig:
    # Configuración de credenciales de OpenAI
    try:
        API_KEY = "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"
    except Exception as e:
        print("Error al obtener las credenciales de OpenAI:", e)

#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