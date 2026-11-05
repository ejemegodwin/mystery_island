from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AlgoStrat"
    database_url: str
    secret_key: str  # long random string; used for JWTs and for hashing OTPs

    # Email provider (Resend)
    resend_api_key: str = ""
    email_from: str = "onboarding@resend.dev"

    # OTP rules
    otp_ttl_minutes: int = 10
    otp_max_attempts: int = 5
    otp_resend_cooldown_seconds: int = 60

    # Sessions
    access_token_minutes: int = 60

    # Development only: print codes to the console instead of sending email
    dev_print_otp: bool = False


settings = Settings()
