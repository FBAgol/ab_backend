from fastapi.middleware.cors import CORSMiddleware

def add_cors_middleware(app):
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # die URLs, die auf die API zugreifen dürfen   
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Erlaubte HTTP-Methoden
        allow_headers=["Content-Type", "Authorization"],  # Erlaubte Header zum beispiel für token oder Content-Type
    )
